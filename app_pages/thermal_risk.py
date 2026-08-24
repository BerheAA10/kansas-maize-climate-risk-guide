import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from dashboard_utils import (
    load_table,
    source_badge,
    format_threshold_order,
    REGIONS,
    MATURITIES,
    SCENARIOS,
    DATES,
    ensure_planting_label,
)
from schema_utils import ensure_maturity_class

st.title("Heat & freeze probability")

summary, src = load_table("threshold_summary")
source_badge(src)

if summary.empty:
    st.warning("Validated threshold summary is not available.")
    st.stop()

summary = format_threshold_order(summary)

# ------------------------------------------------------------------
# Headline metrics
# ------------------------------------------------------------------
heat = summary[summary["family"].eq("Heat")]
cold = summary[summary["family"].eq("Cold")]

c1, c2, c3 = st.columns(3)

c1.metric(
    "Significant harmful heat models",
    f"{int(heat['significant_positive_penalty_models'].sum())}",
)

c2.metric(
    "Significant harmful cold models",
    f"{int(cold['significant_positive_penalty_models'].sum())}",
)

if not heat.empty:
    m = heat.loc[heat["median_penalty_kg_ha"].idxmax()]
    c3.metric(
        "Largest median heat penalty",
        f"{m['median_penalty_kg_ha']:,.0f} kg/ha",
    )

st.divider()

# ------------------------------------------------------------------
# Threshold summary — show one stress family at a time.
# This prevents six long threshold labels from being squeezed together.
# ------------------------------------------------------------------
st.subheader("Thermal-risk threshold summary")

family_view = st.radio(
    "Stress family",
    ["Heat", "Cold / freeze"],
    horizontal=True,
    key="thermal_summary_family",
)

family_key = "Heat" if family_view == "Heat" else "Cold"
view = summary[summary["family"].eq(family_key)].copy()

family_color = "#D7191C" if family_key == "Heat" else "#2B83BA"

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.markdown("### Event probability")

        fig = go.Figure(go.Bar(
            x=view["threshold_label"],
            y=view["median_event_probability_pct"],
            marker_color=family_color,
            marker_line_color="#000000",
            marker_line_width=1.2,
            width=0.46,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Median event probability: %{y:.1f}%"
                "<extra></extra>"
            ),
        ))

        fig.update_layout(
            height=390,
            bargap=0.42,
            margin=dict(l=72, r=24, t=20, b=88),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(
                family="Arial, Helvetica, sans-serif",
                size=17,
                color="#000000",
            ),
            showlegend=False,
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                bordercolor="#000000",
                font=dict(size=16, color="#000000"),
            ),
        )

        fig.update_xaxes(
            title="Temperature threshold",
            tickangle=0,
            tickfont=dict(size=15, color="#000000"),
            title_font=dict(size=18, color="#000000"),
            linecolor="#000000",
            linewidth=2.0,
            showline=True,
            mirror=True,
            ticks="outside",
            tickcolor="#000000",
        )

        fig.update_yaxes(
            title="Median event probability (%)",
            tickfont=dict(size=16, color="#000000"),
            title_font=dict(size=18, color="#000000"),
            gridcolor="#D9D9D9",
            linecolor="#000000",
            linewidth=2.0,
            showline=True,
            mirror=True,
            ticks="outside",
            tickcolor="#000000",
            rangemode="tozero",
        )

        st.plotly_chart(fig, width="stretch")

with right:
    with st.container(border=True):
        st.markdown("### Median associated yield penalty")

        fig = go.Figure(go.Bar(
            x=view["threshold_label"],
            y=view["median_penalty_kg_ha"],
            marker_color=family_color,
            marker_line_color="#000000",
            marker_line_width=1.2,
            width=0.46,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Median associated yield penalty: %{y:,.1f} kg/ha"
                "<extra></extra>"
            ),
        ))

        fig.add_hline(
            y=0,
            line_color="#000000",
            line_width=1.4,
        )

        fig.update_layout(
            height=390,
            bargap=0.42,
            margin=dict(l=78, r=24, t=20, b=88),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(
                family="Arial, Helvetica, sans-serif",
                size=17,
                color="#000000",
            ),
            showlegend=False,
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                bordercolor="#000000",
                font=dict(size=16, color="#000000"),
            ),
        )

        fig.update_xaxes(
            title="Temperature threshold",
            tickangle=0,
            tickfont=dict(size=15, color="#000000"),
            title_font=dict(size=18, color="#000000"),
            linecolor="#000000",
            linewidth=2.0,
            showline=True,
            mirror=True,
            ticks="outside",
            tickcolor="#000000",
        )

        fig.update_yaxes(
            title="Median associated yield penalty (kg/ha)",
            tickfont=dict(size=16, color="#000000"),
            title_font=dict(size=18, color="#000000"),
            gridcolor="#D9D9D9",
            linecolor="#000000",
            linewidth=2.0,
            showline=True,
            mirror=True,
            ticks="outside",
            tickcolor="#000000",
        )

        st.plotly_chart(fig, width="stretch")


# ------------------------------------------------------------------
# Interactive yield-impact explorer
# ------------------------------------------------------------------
st.divider()
st.subheader("How heat & freeze affect yield")

models, model_src = load_table("safe17_regional_models")
source_badge(model_src)

if models.empty:
    st.info("The regional heat/cold yield-association table is not present in this bundle.")
else:
    models = ensure_maturity_class(models)
    models = ensure_planting_label(models)
    models = models[models["planting_label"].notna()].copy()

    top1, top2 = st.columns(2, gap="large")

    with top1:
        compare_by = st.selectbox(
            "Compare yield effects by",
            [
                "Planting date",
                "Maturity class",
                "Region",
                "Water regime",
                "Temperature threshold",
            ],
        )

    with top2:
        metric_label = st.selectbox(
            "Yield / risk response",
            [
                "Associated yield penalty (kg/ha)",
                "Associated yield penalty (%)",
                "Event probability (%)",
            ],
        )

    metric_map = {
        "Associated yield penalty (kg/ha)": "associated_penalty_kg_ha",
        "Associated yield penalty (%)": "associated_penalty_pct",
        "Event probability (%)": "event_probability_pct",
    }
    metric = metric_map[metric_label]

    family = st.radio(
        "Stress family for the yield comparison",
        ["Heat", "Cold / freeze"],
        horizontal=True,
        key="thermal_explorer_family",
    )
    family_key = "Heat" if family == "Heat" else "Cold"

    family_thresholds = {
        "Heat": ["Tmax ≥ 30°C", "Tmax ≥ 35°C", "Tmax ≥ 38°C"],
        "Cold": ["Tmin ≤ 0°C", "Tmin ≤ −2.2°C", "Tmin ≤ −4°C"],
    }

    # Build only the filters that are relevant to the selected comparison.
    filter_specs = []

    if compare_by != "Region":
        filter_specs.append(("Region", REGIONS))
    if compare_by != "Water regime":
        filter_specs.append(("Water regime", SCENARIOS))
    if compare_by != "Maturity class":
        filter_specs.append(("Maturity class", MATURITIES))
    if compare_by != "Planting date":
        filter_specs.append(("Planting date", DATES))
    if compare_by != "Temperature threshold":
        filter_specs.append(("Temperature threshold", family_thresholds[family_key]))

    selections = {}

    # Two filters per row keeps the page readable at typical browser widths.
    for start in range(0, len(filter_specs), 2):
        row = st.columns(2, gap="large")
        for i, (label, options) in enumerate(filter_specs[start:start + 2]):
            with row[i]:
                selections[label] = st.selectbox(
                    label,
                    options,
                    key=f"thermal_filter_{label}_{compare_by}_{family_key}",
                )

    q = models.copy()

    if "Region" in selections:
        q = q[q["region"].eq(selections["Region"])]

    if "Water regime" in selections:
        q = q[q["scenario"].eq(selections["Water regime"])]

    if "Maturity class" in selections:
        q = q[q["maturity_class"].eq(selections["Maturity class"])]

    if "Planting date" in selections:
        q = q[q["planting_label"].eq(selections["Planting date"])]

    q = q[q["family"].eq(family_key)]

    if "Temperature threshold" in selections:
        q = q[q["threshold_label"].eq(selections["Temperature threshold"])]

    dim_map = {
        "Planting date": "planting_label",
        "Maturity class": "maturity_class",
        "Region": "region",
        "Water regime": "scenario",
        "Temperature threshold": "threshold_label",
    }
    dim = dim_map[compare_by]

    if q.empty:
        st.warning("No estimable model rows match this combination.")
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
            "threshold_label": family_thresholds[family_key],
        }

        if dim in orders:
            plot[dim] = pd.Categorical(
                plot[dim],
                categories=orders[dim],
                ordered=True,
            )
            plot = plot.sort_values(dim)

        color = "#D7191C" if family_key == "Heat" else "#2B83BA"

        with st.container(border=True):
            fig = go.Figure(go.Bar(
                x=plot[dim].astype(str),
                y=plot["value"],
                marker_color=color,
                marker_line_color="#000000",
                marker_line_width=1.2,
                width=0.50,
                customdata=plot[
                    ["event_probability_pct", "p_value"]
                ].to_numpy(),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    + metric_label
                    + ": %{y:,.2f}<br>"
                    "Event probability: %{customdata[0]:.2f}%<br>"
                    "p-value: %{customdata[1]:.3g}"
                    "<extra></extra>"
                ),
            ))

            if "penalty" in metric_label.lower():
                fig.add_hline(
                    y=0,
                    line_color="#000000",
                    line_width=1.4,
                )

            fig.update_layout(
                height=455,
                margin=dict(l=92, r=30, t=28, b=88),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(
                    family="Arial, Helvetica, sans-serif",
                    size=17,
                    color="#000000",
                ),
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="#FFFFFF",
                    bordercolor="#000000",
                    font=dict(size=16, color="#000000"),
                ),
            )

            fig.update_xaxes(
                title=compare_by,
                tickfont=dict(size=16, color="#000000"),
                title_font=dict(size=19, color="#000000"),
                linecolor="#000000",
                linewidth=2.0,
                showline=True,
                mirror=True,
                ticks="outside",
                tickcolor="#000000",
            )

            fig.update_yaxes(
                title=metric_label,
                tickfont=dict(size=16, color="#000000"),
                title_font=dict(size=19, color="#000000"),
                gridcolor="#D9D9D9",
                linecolor="#000000",
                linewidth=2.0,
                showline=True,
                mirror=True,
                ticks="outside",
                tickcolor="#000000",
            )

            st.plotly_chart(fig, width="stretch")

        with st.expander("View selected comparison values"):
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


# ------------------------------------------------------------------
# Definitions at bottom
# ------------------------------------------------------------------
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
