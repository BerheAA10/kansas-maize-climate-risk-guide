import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from dashboard_utils import (
    load_table, source_badge, format_threshold_order,
    REGIONS, MATURITIES, SCENARIOS, DATES,
)

st.title("Heat & freeze probability")

summary, src = load_table("threshold_summary")
source_badge(src)
if summary.empty:
    st.warning("Validated threshold summary is not available.")
    st.stop()

summary = format_threshold_order(summary)
heat = summary[summary["family"].eq("Heat")]
cold = summary[summary["family"].eq("Cold")]

c1, c2, c3 = st.columns(3)
c1.metric("Significant harmful heat models", f"{int(heat['significant_positive_penalty_models'].sum())}")
c2.metric("Significant harmful cold models", f"{int(cold['significant_positive_penalty_models'].sum())}")
if not heat.empty:
    m = heat.loc[heat["median_penalty_kg_ha"].idxmax()]
    c3.metric("Largest median heat penalty", f"{m['median_penalty_kg_ha']:,.0f} kg/ha")

left, right = st.columns(2)

with left:
    st.markdown("### Event probability")
    fig = go.Figure(go.Bar(
        x=summary["threshold_label"],
        y=summary["median_event_probability_pct"],
        marker_color=["#2B83BA" if f == "Cold" else "#D7191C" for f in summary["family"]],
        marker_line_color="#000000",
        marker_line_width=1.1,
        width=0.42,
        hovertemplate="<b>%{x}</b><br>Median event probability: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=315, bargap=0.50,
        margin=dict(l=55, r=15, t=8, b=80),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=15, color="#000000"),
        showlegend=False,
    )
    fig.update_xaxes(
        title="Threshold", tickangle=-25,
        tickfont=dict(size=13, color="#000000"),
        title_font=dict(size=15, color="#000000"),
        linecolor="#000000",
    )
    fig.update_yaxes(
        title="Probability (%)",
        tickfont=dict(size=14, color="#000000"),
        title_font=dict(size=15, color="#000000"),
        gridcolor="#DDDDDD", linecolor="#000000",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.markdown("### Median associated yield penalty")
    fig = go.Figure(go.Bar(
        x=summary["threshold_label"],
        y=summary["median_penalty_kg_ha"],
        marker_color=["#2B83BA" if f == "Cold" else "#D7191C" for f in summary["family"]],
        marker_line_color="#000000",
        marker_line_width=1.1,
        width=0.42,
        hovertemplate="<b>%{x}</b><br>Median penalty: %{y:,.0f} kg/ha<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="#000000", line_width=1.3)
    fig.update_layout(
        height=315, bargap=0.50,
        margin=dict(l=60, r=15, t=8, b=80),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=15, color="#000000"),
        showlegend=False,
    )
    fig.update_xaxes(
        title="Threshold", tickangle=-25,
        tickfont=dict(size=13, color="#000000"),
        title_font=dict(size=15, color="#000000"),
        linecolor="#000000",
    )
    fig.update_yaxes(
        title="Penalty (kg/ha)",
        tickfont=dict(size=14, color="#000000"),
        title_font=dict(size=15, color="#000000"),
        gridcolor="#DDDDDD", linecolor="#000000",
    )
    st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("How heat & freeze affect yield")

models, model_src = load_table("safe17_regional_models")
source_badge(model_src)

if models.empty:
    st.info("The full SAFE17 regional model table is not present in this bundle.")
else:
    compare_by = st.selectbox(
        "Compare yield effects by",
        ["Planting date", "Maturity class", "Region", "Water regime", "Temperature threshold"],
    )
    metric_label = st.selectbox(
        "Yield / risk response",
        ["Associated yield penalty (kg/ha)", "Associated yield penalty (%)", "Event probability (%)"],
    )
    metric_map = {
        "Associated yield penalty (kg/ha)": "associated_penalty_kg_ha",
        "Associated yield penalty (%)": "associated_penalty_pct",
        "Event probability (%)": "event_probability_pct",
    }
    metric = metric_map[metric_label]

    a, b, c = st.columns(3)
    region = None if compare_by == "Region" else a.selectbox("Region", REGIONS)
    scenario = None if compare_by == "Water regime" else b.selectbox("Water regime", SCENARIOS)
    maturity = None if compare_by == "Maturity class" else c.selectbox("Maturity class", MATURITIES)

    d1, d2, d3 = st.columns(3)
    planting = None if compare_by == "Planting date" else d1.selectbox("Planting date", DATES)
    family = d2.selectbox("Stress family", ["Heat", "Cold"])

    family_thresholds = {
        "Heat": ["Tmax ≥ 30°C", "Tmax ≥ 35°C", "Tmax ≥ 38°C"],
        "Cold": ["Tmin ≤ 0°C", "Tmin ≤ −2.2°C", "Tmin ≤ −4°C"],
    }
    threshold = None if compare_by == "Temperature threshold" else d3.selectbox(
        "Temperature threshold", family_thresholds[family]
    )

    q = models.copy()
    if region is not None:
        q = q[q["region"].eq(region)]
    if scenario is not None:
        q = q[q["scenario"].eq(scenario)]
    if maturity is not None:
        q = q[q["maturity_class"].eq(maturity)]
    if planting is not None:
        q = q[q["planting_label"].eq(planting)]
    q = q[q["family"].eq(family)]
    if threshold is not None:
        q = q[q["threshold_label"].eq(threshold)]

    dim_map = {
        "Planting date": "planting_label",
        "Maturity class": "maturity_class",
        "Region": "region",
        "Water regime": "scenario",
        "Temperature threshold": "threshold_label",
    }
    dim = dim_map[compare_by]

    if q.empty:
        st.warning("No estimable SAFE17 model rows match this combination.")
    else:
        plot = (
            q.groupby(dim, as_index=False)
             .agg(
                 value=(metric, "median"),
                 event_probability_pct=("event_probability_pct", "median"),
                 p_value=("p_value", "median"),
             )
        )

        orders = {
            "planting_label": DATES,
            "maturity_class": MATURITIES,
            "region": REGIONS,
            "scenario": SCENARIOS,
            "threshold_label": family_thresholds[family],
        }
        if dim in orders:
            plot[dim] = pd.Categorical(plot[dim], categories=orders[dim], ordered=True)
            plot = plot.sort_values(dim)

        color = "#D7191C" if family == "Heat" else "#2B83BA"

        fig = go.Figure(go.Bar(
            x=plot[dim].astype(str),
            y=plot["value"],
            marker_color=color,
            marker_line_color="#000000",
            marker_line_width=1.15,
            width=0.46,
            customdata=plot[["event_probability_pct", "p_value"]].to_numpy(),
            hovertemplate=(
                "<b>%{x}</b><br>"
                + metric_label + ": %{y:,.2f}<br>"
                "Event probability: %{customdata[0]:.2f}%<br>"
                "p-value: %{customdata[1]:.3g}<extra></extra>"
            ),
        ))
        if "penalty" in metric_label.lower():
            fig.add_hline(y=0, line_color="#000000", line_width=1.3)

        fig.update_layout(
            height=360,
            margin=dict(l=70, r=20, t=12, b=65),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Arial", size=16, color="#000000"),
            showlegend=False,
        )
        fig.update_xaxes(
            title=compare_by,
            tickfont=dict(size=14, color="#000000"),
            title_font=dict(size=16, color="#000000"),
            linecolor="#000000",
        )
        fig.update_yaxes(
            title=metric_label,
            tickfont=dict(size=15, color="#000000"),
            title_font=dict(size=16, color="#000000"),
            gridcolor="#DDDDDD", linecolor="#000000",
        )
        st.plotly_chart(fig, width="stretch")

        st.dataframe(
            plot.rename(columns={
                dim: compare_by,
                "value": metric_label,
                "event_probability_pct": "Event probability (%)",
                "p_value": "Median p-value",
            }).round(3),
            width="stretch",
            hide_index=True,
        )

st.divider()
st.subheader("Thermal-event definitions")
st.markdown(
    """
**Heat:** flowering/silking proxy (anthesis-centered ADAT ±7 d), Tmax ≥30, ≥35, ≥38°C.  
**Cold/freeze:** late season through DSSAT physiological maturity, Tmin ≤0, ≤−2.2, ≤−4°C.

Positive temperature-associated yield penalty means yield was lower when the event occurred.
These estimates are model-based statistical associations, not direct experimental causal-damage coefficients.
"""
)
