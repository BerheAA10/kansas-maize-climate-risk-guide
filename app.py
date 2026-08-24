from pathlib import Path
import streamlit as st

APP_BUILD = "SAFE19_FIX13"

st.set_page_config(
    page_title="Kansas Maize Climate-Risk Guide",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
.stApp, .stApp p, .stApp label, .stApp span, [data-testid="stMetricLabel"],
[data-testid="stMetricValue"], [data-testid="stCaptionContainer"], [data-testid="stMarkdownContainer"] {
    color:#000000 !important;
}
.stSelectbox label, .stRadio label, .stCheckbox label, .stSlider label {
    color:#000000 !important; font-size:1.02rem !important; font-weight:600 !important;
}
</style>
""", unsafe_allow_html=True)

PAGES = {
    "Research atlas": [
        st.Page("app_pages/home.py", title="Overview", icon="🏠", default=True),
        st.Page("app_pages/yield_penalty.py", title="Yield penalties", icon="📉"),
        st.Page("app_pages/planting_maturity.py", title="Planting date × maturity", icon="🌱"),
        st.Page("app_pages/yield_water.py", title="Yield & water", icon="💧"),
        st.Page("app_pages/producer_optimizer.py", title="Producer Optimizer", icon="🎯"),
        st.Page("app_pages/thermal_risk.py", title="Heat & freeze risk", icon="🌡️"),
    ],
    "Science & methods": [
        st.Page("app_pages/methods.py", title="Methods & definitions", icon="📘"),
    ],
}

pg = st.navigation(PAGES)
pg.run()
