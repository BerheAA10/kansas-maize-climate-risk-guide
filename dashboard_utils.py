from pathlib import Path
import pandas as pd
import streamlit as st
from schema_utils import ensure_maturity_class, ensure_planting_label

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "data" / "public"
DEMO = ROOT / "data" / "demo"
ASSETS = ROOT / "assets"

REGIONS = ["Northwest","Northcentral","Northeast","Southwest","Southcentral","Southeast"]
MATURITIES = ["LS","MS","SS","VSS"]
SCENARIOS = ["Rainfed","Irrigated"]
DATES = ["April 1","April 10","April 20","May 1","May 10","May 20"]

FILES = {
    "threshold_summary": "heat_vs_cold_threshold_overall_summary.csv",
    "water_maturity_summary": "water_maturity_threshold_summary.csv",
    "safe17_regional_models": "regional_aligned_heat_cold_FE_penalties.csv",
    "safe16_penalties": "regional_date_heat_associated_penalty.csv",
    "safe14_integrated": "regional_yield_water_thermal_integrated.csv",
    "regional_paired": "regional_longterm_paired_metrics.csv",
    "regional_yield_water": "regional_longterm_yield_water.csv",
    "safe13_regional": "regional_thermal_risk_summary_long.csv",
    "top30_kg": "top30_temperature_penalties_kg_ha.csv",
    "top30_pct": "top30_temperature_penalties_pct.csv",
    "overview_climate": "regional_climate_overview.csv",
}

@st.cache_data(show_spinner=False)
def load_table(key: str):
    name = FILES[key]
    p = PUBLIC / name
    if p.exists():
        return pd.read_csv(p), "validated public export"
    p = DEMO / name
    if p.exists():
        return pd.read_csv(p), "demo summary"
    return pd.DataFrame(), "not available"

def source_badge(source):
    """Keep validated-source provenance internal rather than displaying it on research pages."""
    if source == "demo summary":
        st.caption("Demo summary shown.")
    elif source == "not available":
        st.warning("This panel requires an exported validated table.")

def format_threshold_order(df):
    order = {
        "Tmin ≤ 0°C":0, "Tmin ≤ −2.2°C":1, "Tmin ≤ −4°C":2,
        "Tmax ≥ 30°C":3, "Tmax ≥ 35°C":4, "Tmax ≥ 38°C":5,
    }
    out=df.copy()
    if "threshold_label" in out.columns:
        out["_order"]=out["threshold_label"].map(order).fillna(99)
        out=out.sort_values("_order").drop(columns="_order")
    return out

def image_files(kind="figures"):
    p=ASSETS/kind
    if not p.exists():
        return []
    return sorted([x for x in p.rglob("*") if x.suffix.lower() in {".png",".jpg",".jpeg"}])

def report_path():
    candidates = [
        ASSETS/"reports"/"Kansas_Maize_FreezeHeat_YieldPenalty_FULL_REPORT_SAFE18.pdf",
        ASSETS/"reports"/"Kansas_Maize_FreezeHeat_YieldPenalty_FULL_REPORT_SAFE18.docx",
    ]
    return [p for p in candidates if p.exists()]


# Publication chart styling used consistently across Streamlit line plots.
MATURITY_COLORS = {
    "LS": "#D7191C",   # sharp red
    "MS": "#0066CC",   # strong blue
    "SS": "#009E49",   # strong green
    "VSS": "#7A1FA2",  # strong purple
}
MATURITY_SYMBOLS = {
    "LS": "circle",
    "MS": "square",
    "SS": "diamond",
    "VSS": "triangle-up",
}

PLANTING_COLORS = {
    "April 1": "#D7191C",
    "April 10": "#0057B8",
    "April 20": "#00A651",
    "May 1": "#7A1FA2",
    "May 10": "#E67E00",
    "May 20": "#111111",
}
PLANTING_SYMBOLS = {
    "April 1": "circle",
    "April 10": "square",
    "April 20": "diamond",
    "May 1": "triangle-up",
    "May 10": "triangle-down",
    "May 20": "x",
}

def apply_publication_plot_style(fig, *, x_title=None, y_title=None, legend_title=None, height=520):
    """Apply high-contrast publication-style formatting to Plotly figures."""
    fig.update_layout(
        height=height,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", size=15, color="#111111"),
        title_font=dict(size=18, color="#111111"),
        legend=dict(
            title=dict(text=legend_title if legend_title is not None else "", font=dict(size=14, color="#111111")),
            font=dict(size=14, color="#111111"),
            bgcolor="rgba(255,255,255,0.96)",
            bordercolor="#444444",
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=70, r=30, t=80, b=70),
    )
    fig.update_xaxes(
        title_text=x_title,
        title_font=dict(size=16, color="#111111"),
        tickfont=dict(size=14, color="#111111"),
        linecolor="#111111",
        linewidth=1.5,
        mirror=True,
        ticks="outside",
        tickcolor="#111111",
        gridcolor="#E6E6E6",
        zerolinecolor="#BBBBBB",
    )
    fig.update_yaxes(
        title_text=y_title,
        title_font=dict(size=16, color="#111111"),
        tickfont=dict(size=14, color="#111111"),
        linecolor="#111111",
        linewidth=1.5,
        mirror=True,
        ticks="outside",
        tickcolor="#111111",
        gridcolor="#E6E6E6",
        zerolinecolor="#BBBBBB",
    )
    return fig

def strengthen_line_traces(fig, *, line_width=3.4, marker_size=9):
    """Make all line traces visibly distinct with stronger line/marker treatment."""
    fig.update_traces(
        line=dict(width=line_width),
        marker=dict(size=marker_size, line=dict(width=1.1, color="#111111")),
    )
    return fig


# =====================================================================
# SAFE19_FIX04 — stronger publication chart styling
# These definitions intentionally override earlier SAFE19 styling.
# =====================================================================

MATURITY_COLORS = {
    "LS": "#E41A1C",   # vivid red
    "MS": "#0066FF",   # vivid blue
    "SS": "#00A651",   # vivid green
    "VSS": "#8A2BE2",  # vivid purple
}
MATURITY_SYMBOLS = {
    "LS": "circle",
    "MS": "square",
    "SS": "diamond",
    "VSS": "triangle-up",
}
MATURITY_DASHES = {
    "LS": "solid",
    "MS": "dash",
    "SS": "dot",
    "VSS": "dashdot",
}

PLANTING_COLORS = {
    "April 1": "#E41A1C",   # red
    "April 10": "#0066FF",  # blue
    "April 20": "#00A651",  # green
    "May 1": "#8A2BE2",     # purple
    "May 10": "#FF8C00",    # orange
    "May 20": "#111111",    # black
}
PLANTING_SYMBOLS = {
    "April 1": "circle",
    "April 10": "square",
    "April 20": "diamond",
    "May 1": "triangle-up",
    "May 10": "triangle-down",
    "May 20": "x",
}
PLANTING_DASHES = {
    "April 1": "solid",
    "April 10": "dash",
    "April 20": "dot",
    "May 1": "dashdot",
    "May 10": "longdash",
    "May 20": "longdashdot",
}

def apply_publication_plot_style(fig, *, x_title=None, y_title=None, legend_title=None, height=560):
    """High-contrast chart style for readability on screen and in publication export."""
    fig.update_layout(
        height=height,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Arial, Helvetica, sans-serif", size=17, color="#000000"),
        title_font=dict(size=21, color="#000000"),
        legend=dict(
            title=dict(
                text=legend_title if legend_title is not None else "",
                font=dict(size=16, color="#000000"),
            ),
            font=dict(size=15, color="#000000"),
            bgcolor="rgba(255,255,255,0.98)",
            bordercolor="#000000",
            borderwidth=1.2,
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=82, r=35, t=95, b=82),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#000000",
            font=dict(size=15, color="#000000"),
        ),
    )
    fig.update_xaxes(
        title_text=x_title,
        title_font=dict(size=18, color="#000000"),
        tickfont=dict(size=16, color="#000000"),
        linecolor="#000000",
        linewidth=2,
        mirror=True,
        ticks="outside",
        tickwidth=2,
        ticklen=6,
        tickcolor="#000000",
        gridcolor="#D9D9D9",
        gridwidth=1,
        zerolinecolor="#888888",
        zerolinewidth=1,
    )
    fig.update_yaxes(
        title_text=y_title,
        title_font=dict(size=18, color="#000000"),
        tickfont=dict(size=16, color="#000000"),
        linecolor="#000000",
        linewidth=2,
        mirror=True,
        ticks="outside",
        tickwidth=2,
        ticklen=6,
        tickcolor="#000000",
        gridcolor="#D9D9D9",
        gridwidth=1,
        zerolinecolor="#888888",
        zerolinewidth=1,
    )
    return fig

def strengthen_line_traces(fig, *, line_width=4.5, marker_size=12):
    """Thick, high-contrast line/marker styling."""
    fig.update_traces(
        line=dict(width=line_width),
        marker=dict(
            size=marker_size,
            line=dict(width=1.6, color="#000000"),
        ),
    )
    return fig

def apply_trace_dashes(fig, dash_map):
    """
    Apply line dash patterns by Plotly trace name.
    Plotly trace name is the category label for the color/symbol variable.
    """
    for tr in fig.data:
        if tr.name in dash_map:
            tr.line.dash = dash_map[tr.name]
    return fig


# SAFE19_FIX05 explicit visual encodings
FIX05_MATURITY_STYLE = {
    "LS":  {"color":"#E31A1C", "symbol":"circle",      "dash":"solid"},
    "MS":  {"color":"#0057D9", "symbol":"square",      "dash":"dash"},
    "SS":  {"color":"#00A651", "symbol":"diamond",     "dash":"dot"},
    "VSS": {"color":"#7B1FA2", "symbol":"triangle-up", "dash":"dashdot"},
}
FIX05_PLANTING_STYLE = {
    "April 1":  {"color":"#E31A1C", "symbol":"circle",        "dash":"solid"},
    "April 10": {"color":"#0057D9", "symbol":"square",        "dash":"dash"},
    "April 20": {"color":"#00A651", "symbol":"diamond",       "dash":"dot"},
    "May 1":    {"color":"#7B1FA2", "symbol":"triangle-up",   "dash":"dashdot"},
    "May 10":   {"color":"#FF8C00", "symbol":"triangle-down", "dash":"longdash"},
    "May 20":   {"color":"#111111", "symbol":"x",             "dash":"longdashdot"},
}

def fix05_layout(fig, x_title, y_title, legend_title, height=590):
    fig.update_layout(
        height=height,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial, Helvetica, sans-serif", size=18, color="#000000"),
        legend=dict(
            title=dict(text=legend_title, font=dict(size=17, color="#000000")),
            font=dict(size=16, color="#000000"),
            bgcolor="rgba(255,255,255,0.98)", bordercolor="#000000", borderwidth=1.3,
            orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0,
        ),
        margin=dict(l=90,r=35,t=100,b=90),
        hoverlabel=dict(bgcolor="white", bordercolor="#000000", font=dict(size=16,color="#000000")),
    )
    fig.update_xaxes(title=x_title, title_font=dict(size=19,color="#000000"),
                     tickfont=dict(size=17,color="#000000"), linecolor="#000000", linewidth=2.2,
                     mirror=True, ticks="outside", tickwidth=2, ticklen=7, tickcolor="#000000",
                     gridcolor="#D7D7D7", gridwidth=1)
    fig.update_yaxes(title=y_title, title_font=dict(size=19,color="#000000"),
                     tickfont=dict(size=17,color="#000000"), linecolor="#000000", linewidth=2.2,
                     mirror=True, ticks="outside", tickwidth=2, ticklen=7, tickcolor="#000000",
                     gridcolor="#D7D7D7", gridwidth=1)
    return fig
