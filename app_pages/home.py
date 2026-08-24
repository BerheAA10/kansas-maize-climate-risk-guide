from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from dashboard_utils import load_table, format_threshold_order, REGIONS

st.title("Kansas Maize Climate-Risk Guide")

thresholds, _ = load_table("threshold_summary")
thresholds = format_threshold_order(thresholds) if not thresholds.empty else thresholds
climate, _ = load_table("overview_climate")

ROOT = Path(__file__).resolve().parents[1]
OVERVIEW = ROOT / "assets" / "overview"
SCATTER = OVERVIEW / "overview_rainfall_vs_et_scatter.png"
BARS_WATER = OVERVIEW / "overview_rainfall_et_bars.png"
BARS_TEMP = OVERVIEW / "overview_tmax_tmin_bars.png"

REGION_COLORS = {
    "Northwest": "#1f78b4",
    "Northcentral": "#33a02c",
    "Northeast": "#6a3d9a",
    "Southwest": "#e31a1c",
    "Southcentral": "#ff7f00",
    "Southeast": "#b15928",
}

def make_kansas_study_map():
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locationmode="USA-states",
        locations=["KS"],
        z=[1],
        zmin=0,
        zmax=1,
        colorscale=[[0, "#f3eed9"], [1, "#f3eed9"]],
        showscale=False,
        marker_line_color="#000000",
        marker_line_width=2.3,
        hovertemplate="<b>Kansas</b><extra></extra>",
        name="Kansas",
    ))

    # Representative locations for the six analysis regions.
    regions = [
        ("Northwest", -100.65, 39.35),
        ("Northcentral", -98.40, 39.40),
        ("Northeast", -95.90, 39.35),
        ("Southwest", -100.70, 37.55),
        ("Southcentral", -98.35, 37.55),
        ("Southeast", -95.85, 37.35),
    ]

    for name, lon, lat in regions:
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            mode="markers+text",
            text=[name],
            textposition="top center",
            name=name,
            marker=dict(
                size=13,
                color=REGION_COLORS[name],
                line=dict(color="#000000", width=1.2),
            ),
            textfont=dict(size=14, color="#000000"),
            hovertemplate=f"<b>{name}</b><extra></extra>",
        ))

    fig.update_geos(
        scope="usa",
        projection_type="albers usa",
        fitbounds="locations",
        showland=True,
        landcolor="#ffffff",
        showlakes=False,
        showrivers=False,
        showsubunits=True,
        subunitcolor="#cfcfcf",
        bgcolor="#ffffff",
    )

    fig.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=28, b=5),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#000000", size=16),
        legend=dict(
            orientation="h",
            y=-0.05,
            x=0.0,
            font=dict(size=13, color="#000000"),
            bgcolor="rgba(255,255,255,0.96)",
        ),
        annotations=[dict(
            text="Kansas study regions",
            x=0.02,
            y=1.04,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=20, color="#000000"),
        )],
    )
    return fig


def climate_chart_layout(fig, x_title, y_title, height=440):
    fig.update_layout(
        height=height,
        margin=dict(l=86, r=30, t=46, b=82),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Arial, Helvetica, sans-serif", size=18, color="#000000"),
        legend=dict(
            font=dict(size=16, color="#000000"),
            orientation="h",
            y=1.05,
            x=0,
            bgcolor="rgba(255,255,255,0.97)",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#000000",
            font=dict(size=16, color="#000000"),
        ),
    )
    fig.update_xaxes(
        title=x_title,
        title_font=dict(size=20, color="#000000"),
        tickfont=dict(size=17, color="#000000"),
        linecolor="#000000",
        linewidth=2.0,
        ticks="outside",
        tickcolor="#000000",
        gridcolor="#D9D9D9",
        mirror=True,
        showline=True,
        zeroline=False,
    )
    fig.update_yaxes(
        title=y_title,
        title_font=dict(size=20, color="#000000"),
        tickfont=dict(size=17, color="#000000"),
        linecolor="#000000",
        linewidth=2.0,
        ticks="outside",
        tickcolor="#000000",
        gridcolor="#D9D9D9",
        mirror=True,
        showline=True,
        zeroline=False,
    )
    return fig


def normalized_climate_table():
    if climate.empty:
        return None

    needed = [
        "region",
        "mean_seasonal_rainfall_mm",
        "mean_crop_et_mm",
        "mean_tmax_c",
        "mean_tmin_c",
    ]
    if not set(needed).issubset(climate.columns):
        return None

    q = (
        climate[needed]
        .copy()
        .groupby("region", as_index=False)
        .mean(numeric_only=True)
    )
    q["region"] = pd.Categorical(q["region"], categories=REGIONS, ordered=True)
    q = q.sort_values("region")
    return q


def plot_rainfall_et_scatter(q):
    fig = go.Figure()

    low = min(q["mean_seasonal_rainfall_mm"].min(), q["mean_crop_et_mm"].min())
    high = max(q["mean_seasonal_rainfall_mm"].max(), q["mean_crop_et_mm"].max())

    fig.add_trace(go.Scatter(
        x=[low, high],
        y=[low, high],
        mode="lines",
        line=dict(color="#4F94CD", width=2.1, dash="dash"),
        name="1:1 reference",
        hoverinfo="skip",
    ))

    for _, r in q.iterrows():
        region = str(r["region"])
        fig.add_trace(go.Scatter(
            x=[r["mean_seasonal_rainfall_mm"]],
            y=[r["mean_crop_et_mm"]],
            mode="markers+text",
            text=[region],
            textposition="top center",
            name=region,
            showlegend=False,
            marker=dict(
                size=14,
                color=REGION_COLORS.get(region, "#333333"),
                line=dict(color="#000000", width=1.4),
            ),
            textfont=dict(size=17, color="#000000"),
            hovertemplate=(
                f"<b>{region}</b><br>"
                "Seasonal rainfall: %{x:.1f} mm<br>"
                "Crop ET: %{y:.1f} mm<extra></extra>"
            ),
        ))

    climate_chart_layout(
        fig,
        "Mean seasonal rainfall (mm)",
        "Mean crop evapotranspiration, ETCM (mm)",
        470,
    )
    return fig


def plot_rainfall_et_bars(q):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=q["region"].astype(str),
        y=q["mean_seasonal_rainfall_mm"],
        name="Seasonal rainfall",
        marker_color="#1f77b4",
        marker_line_color="#000000",
        marker_line_width=0.8,
        width=0.34,
    ))
    fig.add_trace(go.Bar(
        x=q["region"].astype(str),
        y=q["mean_crop_et_mm"],
        name="Crop ET",
        marker_color="#ff7f0e",
        marker_line_color="#000000",
        marker_line_width=0.8,
        width=0.34,
    ))
    fig.update_layout(barmode="group", bargap=0.24)
    climate_chart_layout(fig, "Kansas region", "Water depth (mm)", 450)
    fig.update_xaxes(tickangle=-18)
    return fig


def plot_tmax_tmin(q):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=q["region"].astype(str),
        y=q["mean_tmax_c"],
        name="Mean maximum temperature",
        marker_color="#1f77b4",
        marker_line_color="#000000",
        marker_line_width=0.8,
        width=0.34,
    ))
    fig.add_trace(go.Bar(
        x=q["region"].astype(str),
        y=q["mean_tmin_c"],
        name="Mean minimum temperature",
        marker_color="#ff7f0e",
        marker_line_color="#000000",
        marker_line_width=0.8,
        width=0.34,
    ))
    fig.update_layout(barmode="group", bargap=0.24)
    climate_chart_layout(fig, "Kansas region", "Temperature (°C)", 450)
    fig.update_xaxes(tickangle=-18)
    return fig


left, right = st.columns([0.80, 1.65], gap="large")

with left:
    st.plotly_chart(make_kansas_study_map(), width="stretch")
    st.markdown(
        "**Overview note.** The map shows the Kansas state outline and representative "
        "locations for the six analysis regions used in this study."
    )

with right:
    st.subheader("Climate context for the six regions")
    tab1, tab2, tab3 = st.tabs([
        "Rainfall vs crop ET",
        "Regional rainfall and crop ET",
        "Mean Tmax and Tmin",
    ])

    climate_q = normalized_climate_table()

    with tab1:
        with st.container(border=True):
            if climate_q is not None:
                st.plotly_chart(plot_rainfall_et_scatter(climate_q), width="stretch")
            elif SCATTER.exists():
                st.image(str(SCATTER), width="stretch")
            else:
                st.warning("Rainfall versus crop ET overview is unavailable.")

    with tab2:
        with st.container(border=True):
            if climate_q is not None:
                st.plotly_chart(plot_rainfall_et_bars(climate_q), width="stretch")
            elif BARS_WATER.exists():
                st.image(str(BARS_WATER), width="stretch")
            else:
                st.warning("Regional rainfall and crop ET overview is unavailable.")

    with tab3:
        with st.container(border=True):
            if climate_q is not None:
                st.plotly_chart(plot_tmax_tmin(climate_q), width="stretch")
            elif BARS_TEMP.exists():
                st.image(str(BARS_TEMP), width="stretch")
            else:
                st.warning("Regional Tmax/Tmin overview is unavailable.")


st.divider()
st.subheader("Key climate-risk signals")

if thresholds.empty:
    st.info("Validated threshold summary is not available.")
else:
    cols = st.columns(4)
    h38 = thresholds[thresholds["threshold_label"].eq("Tmax ≥ 38°C")]
    h35 = thresholds[thresholds["threshold_label"].eq("Tmax ≥ 35°C")]
    c0 = thresholds[thresholds["threshold_label"].eq("Tmin ≤ 0°C")]

    if not h38.empty:
        r = h38.iloc[0]
        cols[0].metric(
            "≥38°C significant harmful models",
            f"{int(r['significant_positive_penalty_models'])}/{int(r['estimable_regional_models'])}",
        )
        cols[1].metric(
            "≥38°C median penalty",
            f"{r['median_penalty_kg_ha']:,.0f} kg/ha",
        )

    if not h35.empty:
        cols[2].metric(
            "≥35°C median probability",
            f"{h35.iloc[0]['median_event_probability_pct']:.1f}%",
        )

    if not c0.empty:
        cols[3].metric(
            "≤0°C median probability",
            f"{c0.iloc[0]['median_event_probability_pct']:.1f}%",
        )

st.markdown(
    """
- **Flowering heat is generally the dominant statewide thermal concern**, especially at ≥35°C and ≥38°C.
- **Regional climate context appears directly in the overview** using rainfall, crop ET, Tmax, and Tmin.
- **The Kansas state map is a state-outline view** with the six study regions clearly identified.
"""
)


st.divider()
st.subheader("Study context")

st.markdown(
    """
An interactive research showcase of the Kansas DSSAT maize planting-date × maturity × water-regime study,
with emphasis on **flowering heat**, **premature freeze**, **yield penalties**, **irrigation**, and
**climate-resilient planting windows**.

**Study design:** 2,776 sites · 1981–2018 · 6 planting dates · 4 maturity classes · rainfed + irrigated.
"""
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kansas DSSAT sites", "2,776")
c2.metric("Years", "38")
c3.metric("Planting dates", "6")
c4.metric("Water regimes", "2")

