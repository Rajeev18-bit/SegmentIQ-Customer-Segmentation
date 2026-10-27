import streamlit as st
import plotly.express as px
from src.ui import apply_theme, metric_card

st.set_page_config(page_title="Customer Segments | SegmentIQ", page_icon="◈", layout="wide")
apply_theme()
st.title("Customer Segments")
st.markdown("Explore the clusters discovered from customer purchase behaviour.")

if "customers" not in st.session_state:
    st.warning("Load a dataset from the Overview page first.")
    st.stop()

df = st.session_state["customers"].copy()
summary = st.session_state["summary"]
a, b, c = st.columns(3)
metric_card(a, "SEGMENTS", str(df["Cluster"].nunique()), "K-Means cluster count")
metric_card(b, "CUSTOMERS", f"{len(df):,}", "Unique customers")
metric_card(c, "MODEL", "K-Means", "RFM-based unsupervised clustering")

left, right = st.columns([1.2, 1])
with left:
    st.markdown("#### Customer map")
    fig = px.scatter(df, x="Frequency", y="Monetary", color="Segment", size="Monetary",
                     hover_data=["CustomerID", "Recency", "Frequency", "Monetary"],
                     log_x=True, log_y=True, opacity=.72,
                     color_discrete_sequence=px.colors.qualitative.Bold,
                     labels={"Frequency":"Purchase invoices (log scale)", "Monetary":"Net spend (£, log scale)"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text="Segment")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Customer share")
    fig2 = px.pie(summary, names="Segment", values="Customers", hole=.62, color_discrete_sequence=px.colors.qualitative.Bold)
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text="")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("#### Segment profile")
st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("#### Find customers")
segments = ["All segments"] + sorted(df["Segment"].unique().tolist())
selected = st.selectbox("Filter by segment", segments)
search = st.text_input("Search Customer ID", placeholder="e.g. 17850")
filtered = df if selected == "All segments" else df[df["Segment"] == selected]
if search.strip().isdigit():
    filtered = filtered[filtered["CustomerID"].astype(str).str.contains(search.strip(), regex=False)]
st.dataframe(filtered[["CustomerID","Recency","Frequency","Monetary","Cluster","Segment"]].sort_values("Monetary", ascending=False), use_container_width=True, hide_index=True)
