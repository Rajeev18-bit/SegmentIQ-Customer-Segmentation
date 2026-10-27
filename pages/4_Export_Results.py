import streamlit as st
import pandas as pd
from src.ui import apply_theme

st.set_page_config(page_title="Export Results | SegmentIQ", page_icon="◈", layout="wide")
apply_theme()
st.title("Export Results")
st.markdown("Download the customer-level segmentation and summary tables for your report.")

if "customers" not in st.session_state:
    st.warning("Load a dataset from the Overview page first.")
    st.stop()

customers = st.session_state["customers"]
summary = st.session_state["summary"]
audit = st.session_state["audit"]
model_info = st.session_state["model_info"]

st.markdown("#### Customer-level results")
st.dataframe(customers.head(30), use_container_width=True, hide_index=True)
st.download_button("Download segmented customers (CSV)", customers.to_csv(index=False).encode("utf-8"), file_name="customer_segments.csv", mime="text/csv", use_container_width=True)
st.download_button("Download segment summary (CSV)", summary.to_csv(index=False).encode("utf-8"), file_name="segment_summary.csv", mime="text/csv", use_container_width=True)

report = {
    "source": st.session_state.get("source_label", "Uploaded dataset"),
    "model": model_info,
    "data_quality_audit": audit,
    "segment_summary": summary.to_dict(orient="records"),
}
st.download_button("Download analysis metadata (JSON)", pd.Series(report).to_json(indent=2).encode("utf-8"), file_name="analysis_metadata.json", mime="application/json", use_container_width=True)
st.caption("Exports contain results calculated during this session. Re-run analysis after changing the source data or cluster count.")
