import streamlit as st
from src.ui import apply_theme, metric_card

st.set_page_config(page_title="Data Explorer | SegmentIQ", page_icon="◈", layout="wide")
apply_theme()
st.title("Data Explorer")
st.markdown("Inspect the source transactions and review the cleaning audit.")

if "raw_data" not in st.session_state:
    st.warning("Load a dataset from the Overview page first.")
    st.stop()

raw = st.session_state["raw_data"]
audit = st.session_state["audit"]
c1, c2, c3 = st.columns(3)
metric_card(c1, "RAW ROWS", f"{len(raw):,}")
metric_card(c2, "COLUMNS", str(len(raw.columns)))
metric_card(c3, "CLEAN PURCHASE ROWS", f"{audit['valid_purchase_rows_used']:,}")

with st.expander("Cleaning audit details", expanded=True):
    st.json(audit)

st.markdown("#### Source data preview")
st.dataframe(raw.head(100), use_container_width=True, hide_index=True)
st.markdown("#### Missing values by column")
missing = raw.isna().sum().rename("Missing values").to_frame()
missing["Missing %"] = (missing["Missing values"] / max(len(raw), 1) * 100).round(2)
st.dataframe(missing.sort_values("Missing values", ascending=False), use_container_width=True)
