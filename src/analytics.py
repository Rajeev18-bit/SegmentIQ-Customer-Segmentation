import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

REQUIRED_COLUMNS = ["InvoiceNo", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID"]

def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing

def prepare_customer_features(raw):
    df = raw.copy()
    valid, missing = validate_columns(df)
    if not valid:
        raise ValueError(f"Missing required columns: {missing}")

    original_rows = int(len(df))
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce", dayfirst=True)

    missing_customer = int(df["CustomerID"].isna().sum())
    invalid_date = int(df["InvoiceDate"].isna().sum())
    cancellation_mask = df["InvoiceNo"].str.upper().str.startswith("C")
    cancellations = int(cancellation_mask.sum())

    # For purchase-based RFM, exclude cancellations/returns and non-positive lines.
    clean = df.loc[
        df["CustomerID"].notna()
        & df["InvoiceDate"].notna()
        & df["Quantity"].gt(0)
        & df["UnitPrice"].gt(0)
        & ~cancellation_mask
    ].copy()

    clean["CustomerID"] = clean["CustomerID"].astype("int64")
    clean["LineValue"] = clean["Quantity"] * clean["UnitPrice"]
    if clean.empty:
        raise ValueError("No valid purchase rows remain after cleaning. Check your uploaded data.")

    # Use one day after the latest observed transaction as the RFM reference date.
    reference_date = clean["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    rfm = clean.groupby("CustomerID").agg(
        LastPurchase=("InvoiceDate", "max"),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("LineValue", "sum"),
        TotalQuantity=("Quantity", "sum"),
    ).reset_index()
    rfm["Recency"] = (reference_date - rfm["LastPurchase"].dt.normalize()).dt.days
    rfm["Frequency"] = rfm["Frequency"].astype(int)
    rfm["Monetary"] = rfm["Monetary"].astype(float)
    rfm["TotalQuantity"] = rfm["TotalQuantity"].astype(int)

    # Use log1p to reduce skew before standardization; retain original RFM values for reporting.
    feature_cols = ["Recency", "Frequency", "Monetary"]
    model_features = np.log1p(rfm[feature_cols].clip(lower=0))
    scaler = StandardScaler()
    scaled = scaler.fit_transform(model_features)
    rfm.attrs["scaled_features"] = scaled
    rfm.attrs["feature_columns"] = feature_cols

    audit = {
        "raw_rows": original_rows,
        "rows_missing_customer_id": missing_customer,
        "rows_with_invalid_invoice_date": invalid_date,
        "cancellation_invoice_rows_detected": cancellations,
        "valid_purchase_rows_used": int(len(clean)),
        "customers_after_cleaning": int(rfm["CustomerID"].nunique()),
        "reference_date_for_recency": str(reference_date.date()),
        "cleaning_rule": "Requires customer ID/date; positive quantity and unit price; excludes invoice numbers starting with C."
    }
    return rfm, audit

def run_kmeans(customers, n_clusters=4):
    result = customers.copy()
    feature_cols = ["Recency", "Frequency", "Monetary"]
    features = np.log1p(result[feature_cols].clip(lower=0))
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    n_clusters = int(max(2, min(n_clusters, len(result) - 1)))
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)
    result["Cluster"] = labels
    # Human-readable labels are based on relative monetary value and recency.
    profile = result.groupby("Cluster").agg(
        median_recency=("Recency", "median"),
        median_monetary=("Monetary", "median"),
        median_frequency=("Frequency", "median")
    )
    value_order = profile.sort_values(["median_monetary", "median_frequency"], ascending=False).index.tolist()
    label_names = {}
    if len(value_order) >= 1:
        label_names[value_order[0]] = "High Value"
    if len(value_order) >= 2:
        label_names[value_order[1]] = "Loyal / Regular"
    if len(value_order) >= 3:
        label_names[value_order[-1]] = "Needs Attention"
    for cluster_id in value_order:
        if cluster_id not in label_names:
            label_names[cluster_id] = f"Core Segment {cluster_id + 1}"
    result["Segment"] = result["Cluster"].map(label_names)

    silhouette = None
    if len(result) > n_clusters and result["Cluster"].nunique() > 1:
        sample_size = min(5000, len(result))
        try:
            silhouette = float(silhouette_score(X, labels, sample_size=sample_size if sample_size < len(result) else None, random_state=42))
        except Exception:
            silhouette = None

    info = {
        "algorithm": "K-Means",
        "n_clusters": int(n_clusters),
        "silhouette_score": silhouette,
        "inertia": float(model.inertia_),
        "features": feature_cols,
        "transformation": "log1p + StandardScaler",
        "random_state": 42,
        "n_init": 10
    }
    return result, info

def build_summary(clustered):
    summary = clustered.groupby("Segment").agg(
        Customers=("CustomerID", "nunique"),
        Revenue=("Monetary", "sum"),
        **{"Avg. spend": ("Monetary", "mean")},
        **{"Median recency (days)": ("Recency", "median")},
        **{"Avg. invoices": ("Frequency", "mean")}
    ).reset_index()
    total_customers = max(int(summary["Customers"].sum()), 1)
    total_revenue = max(float(summary["Revenue"].sum()), 0.0)
    summary["Customer share"] = summary["Customers"] / total_customers * 100
    summary["Revenue share"] = summary["Revenue"] / total_revenue * 100 if total_revenue else 0
    summary["Median recency (days)"] = summary["Median recency (days)"].round(1)
    summary["Avg. invoices"] = summary["Avg. invoices"].round(2)
    summary["Avg. spend"] = summary["Avg. spend"].round(2)
    summary["Revenue"] = summary["Revenue"].round(2)
    return summary.sort_values("Revenue", ascending=False)

def evaluate_cluster_counts(customers, min_k=2, max_k=8):
    feature_cols = ["Recency", "Frequency", "Monetary"]
    features = np.log1p(customers[feature_cols].clip(lower=0))
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    rows = []
    max_k = min(max_k, len(customers) - 1)
    for k in range(min_k, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        score = None
        if len(set(labels)) > 1:
            try:
                sample_size = min(5000, len(customers))
                score = silhouette_score(X, labels, sample_size=sample_size if sample_size < len(customers) else None, random_state=42)
            except Exception:
                pass
        rows.append({"Clusters (k)": k, "Inertia": float(model.inertia_), "Silhouette score": score})
    return pd.DataFrame(rows)
