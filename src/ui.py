import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    :root { --navy:#0b1220; --panel:#111c2f; --line:#24334b; --muted:#9aa9bf; --cyan:#5eead4; }
    .stApp { background: radial-gradient(ellipse at top left, #13213a 0%, #0b1220 45%, #080d17 100%); color:#edf3fb; }
    [data-testid="stSidebar"] { background:#080e19; border-right:1px solid #1e2b40; }
    [data-testid="stSidebar"] * { color:#dce7f7; }
    h1,h2,h3 { color:#f4f7fc !important; letter-spacing:-0.025em; }
    p, label, .stMarkdown { color:#d5dfed; }
    [data-testid="stMetric"] { background:linear-gradient(145deg,#14233a,#101a2b); padding:18px 20px; border:1px solid #293b55; border-radius:16px; }
    [data-testid="stMetricLabel"] { color:#9fb0c7 !important; font-size:.78rem; letter-spacing:.08em; }
    [data-testid="stMetricValue"] { color:#f4f8ff !important; }
    .panel { background:linear-gradient(145deg,#14233a,#101a2b); border:1px solid #293b55; border-radius:16px; padding:20px; min-height:150px; }
    .panel h3 { margin:.4rem 0; font-size:1.1rem; }
    .panel p { color:#9fb0c7; font-size:.9rem; }
    .eyebrow { color:#5eead4; font-size:.75rem; letter-spacing:.14em; font-weight:700; }
    .section-title { font-size:1.05rem; font-weight:700; margin:1rem 0 .65rem; color:#f4f7fc; }
    [data-testid="stDataFrame"] { border:1px solid #293b55; border-radius:12px; overflow:hidden; }
    .stButton button, .stDownloadButton button { border-radius:10px; border:1px solid #3b587a; }
    div[data-baseweb="select"] > div { background-color:#111c2f; border-color:#2a3c55; }
    </style>
    """, unsafe_allow_html=True)

def metric_card(col, label, value, help_text=""):
    with col:
        st.metric(label, value, help=help_text)
