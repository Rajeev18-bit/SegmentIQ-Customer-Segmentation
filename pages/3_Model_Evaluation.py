import streamlit as st
import plotly.express as px
from src.analytics import evaluate_cluster_counts
from src.ui import apply_theme, metric_card

st.set_page_config(page_title="Model Evaluation | SegmentIQ", page_icon="◈", layout="wide")
apply_theme()
st.title("Model Evaluation")
st.markdown("Compare candidate cluster counts using inertia (Elbow Method) and silhouette score.")

if "customers" not in st.session_state:
    st.warning("Load a dataset from the Overview page first.")
    st.stop()

df = st.session_state["customers"]
info = st.session_state["model_info"]
score = info["silhouette_score"]
a, b, c = st.columns(3)
metric_card(a, "SELECTED CLUSTERS", str(info["n_clusters"]))
metric_card(b, "SILHOUETTE SCORE", "N/A" if score is None else f"{score:.3f}", "Higher is generally better; interpret alongside the cluster profiles.")
metric_card(c, "INERTIA", f"{info['inertia']:,.1f}", "Lower generally improves as more clusters are added.")

with st.spinner("Evaluating candidate cluster counts…"):
    evaluation = evaluate_cluster_counts(df, 2, 8)
left, right = st.columns(2)
with left:
    fig = px.line(evaluation, x="Clusters (k)", y="Inertia", markers=True, title="Elbow Method")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.line(evaluation, x="Clusters (k)", y="Silhouette score", markers=True, title="Silhouette Score")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_range=[-1,1])
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(evaluation.round(4), use_container_width=True, hide_index=True)
st.info("These metrics support model selection; they do not prove that one cluster count is universally correct. Review business interpretability and segment sizes as well.")
