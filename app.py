import streamlit as st
import pandas as pd
from pathlib import Path
from src.analytics import prepare_customer_features, run_kmeans, build_summary, validate_columns
from src.ui import apply_theme, metric_card

st.set_page_config(page_title="SegmentIQ | Customer Analytics", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
apply_theme()

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_FILE = DATA_DIR / "Online Retail.xlsx"

st.sidebar.markdown("# ◈ SegmentIQ")
st.sidebar.caption("CUSTOMER INTELLIGENCE PLATFORM")
st.sidebar.divider()
st.sidebar.markdown("### Data source")
uploaded = st.sidebar.file_uploader("Upload transaction data", type=["csv", "xlsx", "xls"], help="Expected columns: InvoiceNo, Quantity, InvoiceDate, UnitPrice, CustomerID. Country and Description are optional.")

@st.cache_data(show_spinner=False)
def read_data(file_bytes, file_name):
    import io
    buffer = io.BytesIO(file_bytes)
    if file_name.lower().endswith(".csv"):
        return pd.read_csv(buffer, low_memory=False)
    return pd.read_excel(buffer)

raw = None
source_label = None
try:
    if uploaded is not None:
        raw = read_data(uploaded.getvalue(), uploaded.name)
        source_label = uploaded.name
    elif DEFAULT_FILE.exists():
        raw = read_data(DEFAULT_FILE.read_bytes(), DEFAULT_FILE.name)
        source_label = DEFAULT_FILE.name
except Exception as exc:
    st.error(f"Could not read this file: {exc}")

if raw is None:
    st.title("Customer Segmentation Analytics")
    st.markdown("### Turn transaction history into actionable customer groups.")
    st.markdown("This project combines **RFM analysis**, **K-Means clustering**, model evaluation, and an interactive analytics dashboard.")
    st.info("To begin, download the official UCI Online Retail dataset and upload the `Online Retail.xlsx` file using the sidebar.")
    st.markdown("[Open the official UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail)")
    st.markdown("#### Expected workflow")
    cols = st.columns(4)
    for col, num, title, desc in zip(cols, ["01", "02", "03", "04"], ["Load data", "Clean records", "Build RFM", "Evaluate clusters"], ["CSV / Excel upload", "Handle returns and missing IDs", "Recency, frequency, monetary", "K-Means + Silhouette"]):
        with col:
            st.markdown(f'<div class="panel"><div class="eyebrow">{num}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.stop()

required_ok, missing = validate_columns(raw)
if not required_ok:
    st.error("This dataset is missing required columns: " + ", ".join(missing))
    st.write("Required columns: InvoiceNo, Quantity, InvoiceDate, UnitPrice, CustomerID")
    st.stop()

with st.sidebar:
    st.caption(f"Loaded: {source_label}")
    st.caption(f"{len(raw):,} raw rows")
    st.divider()
    n_clusters = st.slider("Number of customer clusters", min_value=2, max_value=8, value=4, step=1)
    st.caption("Change the cluster count to recalculate the segmentation.")

try:
    with st.spinner("Cleaning transactions and calculating customer segments…"):
        customers, audit = prepare_customer_features(raw)
        clustered, model_info = run_kmeans(customers, n_clusters=n_clusters)
        summary = build_summary(clustered)
except Exception as exc:
    st.error(f"Could not process this dataset: {exc}")
    st.stop()

st.session_state["raw_data"] = raw
st.session_state["source_label"] = source_label
st.session_state["customers"] = clustered
st.session_state["summary"] = summary
st.session_state["audit"] = audit
st.session_state["model_info"] = model_info
st.session_state["n_clusters"] = n_clusters

st.title("Customer Intelligence Overview")
st.markdown("A data-driven view of customer value, purchase behaviour and segment composition.")
st.caption(f"Data source: {source_label} · Customer-level results are recalculated from the selected transaction file.")

total_customers = len(clustered)
total_revenue = float(clustered["Monetary"].sum())
total_orders = int(clustered["Frequency"].sum())
avg_spend = float(clustered["Monetary"].mean()) if total_customers else 0
c1, c2, c3, c4 = st.columns(4)
metric_card(c1, "CUSTOMERS ANALYSED", f"{total_customers:,}", "Unique customers with valid purchases")
metric_card(c2, "NET SALES VALUE", f"£{total_revenue:,.2f}", "After excluding cancelled/invalid lines")
metric_card(c3, "CUSTOMER INVOICES", f"{total_orders:,}", "Distinct purchase invoices summed across customers")
metric_card(c4, "AVG. CUSTOMER VALUE", f"£{avg_spend:,.2f}", "Average monetary value per customer")

left, right = st.columns([1.3, 1])
with left:
    st.markdown('<div class="section-title">Segment composition</div>', unsafe_allow_html=True)
    st.bar_chart(summary.set_index("Segment")["Customers"], use_container_width=True)
with right:
    st.markdown('<div class="section-title">Revenue by segment</div>', unsafe_allow_html=True)
    st.bar_chart(summary.set_index("Segment")["Revenue"], use_container_width=True)

st.markdown('<div class="section-title">Segment profile</div>', unsafe_allow_html=True)
display = summary.copy()
display["Revenue"] = display["Revenue"].map(lambda x: f"£{x:,.2f}")
display["Avg. spend"] = display["Avg. spend"].map(lambda x: f"£{x:,.2f}")
display["Revenue share"] = display["Revenue share"].map(lambda x: f"{x:.1f}%")
st.dataframe(display, use_container_width=True, hide_index=True)

with st.expander("Data quality audit"):
    st.write("The pipeline keeps an audit summary of how transaction rows were handled.")
    st.json(audit)
    st.caption("The dashboard uses only rows with valid customer IDs, positive quantity and positive unit price; cancellation invoices are excluded from purchase metrics.")
