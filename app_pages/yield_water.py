import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from dashboard_utils import (
    load_table, source_badge, REGIONS, MATURITIES, DATES,
    ensure_maturity_class, ensure_planting_label,
    FIX05_MATURITY_STYLE, fix05_layout,
)

st.title("Yield, irrigation, rainfall & water productivity")

df, src = load_table("regional_paired")
source_badge(src)

if df.empty:
    st.warning("Export the six-date regional paired metrics table to activate this page.")
    st.stop()

df = ensure_maturity_class(df)
df = ensure_planting_label(df)

# A missing canonical planting date is a display-schema problem, not a seventh date.
unmapped = df["planting_label"].isna()
if unmapped.any():
    st.warning(
        f"{int(unmapped.sum())} row(s) have an unrecognized planting-date label and are excluded "
        "from plotting. No 'NaN' category is displayed."
    )
    df = df[~unmapped].copy()

region = st.selectbox("Region", REGIONS)

MIN95_LABEL = "Minimum irrigation retaining ≥95% of maximum yield (mm)"

metrics = {
    "Rainfed yield (kg/ha)": "rainfed_yield_mean_kg_ha",
    "Irrigated yield (kg/ha)": "irrigated_yield_mean_kg_ha",
    "Irrigation requirement (mm)": "irrigation_mean_mm",
    "Irrigation yield benefit (kg/ha)": "incremental_benefit_mean_kg_ha",
    "Incremental IWUE (kg/m³)": "incremental_iwue_mean_kg_m3",
    "Gross irrigation productivity (kg/m³)": "gross_irrigation_productivity_mean_kg_m3",
    "Yield gap (%)": "yield_gap_mean_percent",
    "Seasonal rainfall (mm)": "rainfed_seasonal_precip_mean_mm",
}

q = df[df["region"].eq(region)].copy()
available = {k: v for k, v in metrics.items() if v in q.columns}

min95_required = {
    "irrigated_yield_mean_kg_ha",
    "irrigation_mean_mm",
    "maturity_class",
    "planting_label",
}
response_options = list(available)
if min95_required.issubset(q.columns):
    response_options.append(MIN95_LABEL)

metric_name = st.selectbox("Response", response_options)
is_min95 = metric_name == MIN95_LABEL
min95_display = None

if is_min95:
    # Within the selected region and maturity class, retain planting dates whose
    # mean irrigated yield is at least 95% of that maturity class's maximum mean
    # irrigated yield, then choose the qualifying date with least mean irrigation.
    base95 = (
        q.groupby(
            ["maturity_class", "planting_label"],
            as_index=False,
            observed=True,
        )
        .agg(
            irrigated_yield_mean_kg_ha=("irrigated_yield_mean_kg_ha", "mean"),
            irrigation_mean_mm=("irrigation_mean_mm", "mean"),
        )
        .dropna(subset=["irrigated_yield_mean_kg_ha", "irrigation_mean_mm"])
    )

    base95["maximum_irrigated_yield_kg_ha"] = (
        base95.groupby("maturity_class", observed=True)[
            "irrigated_yield_mean_kg_ha"
        ].transform("max")
    )
    base95["yield_threshold_95_kg_ha"] = (
        0.95 * base95["maximum_irrigated_yield_kg_ha"]
    )
    base95["yield_retained_pct"] = (
        100.0
        * base95["irrigated_yield_mean_kg_ha"]
        / base95["maximum_irrigated_yield_kg_ha"]
    )

    candidates = base95[
        base95["irrigated_yield_mean_kg_ha"]
        >= base95["yield_threshold_95_kg_ha"]
    ].copy()

    date_order = {d: i for i, d in enumerate(DATES)}
    candidates["_date_order"] = candidates["planting_label"].map(date_order).fillna(999)
    candidates = candidates.sort_values(
        [
            "maturity_class",
            "irrigation_mean_mm",
            "irrigated_yield_mean_kg_ha",
            "_date_order",
        ],
        ascending=[True, True, False, True],
    )

    selected95 = (
        candidates.groupby("maturity_class", as_index=False, observed=True)
        .first()
    )

    plot = selected95[
        ["maturity_class", "planting_label", "irrigation_mean_mm"]
    ].rename(columns={"irrigation_mean_mm": "minimum_irrigation_95_mm"})
    metric = "minimum_irrigation_95_mm"

    min95_display = selected95[
        [
            "maturity_class",
            "planting_label",
            "irrigation_mean_mm",
            "irrigated_yield_mean_kg_ha",
            "maximum_irrigated_yield_kg_ha",
            "yield_retained_pct",
        ]
    ].rename(
        columns={
            "maturity_class": "Maturity class",
            "planting_label": "Selected planting date",
            "irrigation_mean_mm": "Minimum irrigation (mm)",
            "irrigated_yield_mean_kg_ha": "Irrigated yield at selected option (kg/ha)",
            "maximum_irrigated_yield_kg_ha": "Maximum irrigated yield (kg/ha)",
            "yield_retained_pct": "Yield retained (%)",
        }
    )
else:
    metric = available[metric_name]
    plot = (
        q.groupby(
            ["maturity_class", "planting_label"],
            as_index=False,
            observed=False,
        )[metric]
        .mean()
    )

if is_min95:
    # Special decision-support presentation used ONLY for the >=95% response.
    # Primary axis: minimum irrigation required to retain >=95% of maximum yield.
    # Secondary axis: irrigated yield achieved at that selected water-saving option.
    special = selected95.copy()

    maturity_order = {m: i for i, m in enumerate(MATURITIES)}
    special["_maturity_order"] = (
        special["maturity_class"].map(maturity_order).fillna(999)
    )
    special = special.sort_values("_maturity_order")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=special["maturity_class"],
            y=special["irrigation_mean_mm"],
            name="Minimum irrigation (mm)",
            width=0.46,
            marker=dict(
                color=[
                    FIX05_MATURITY_STYLE[m]["color"]
                    if m in FIX05_MATURITY_STYLE
                    else "#777777"
                    for m in special["maturity_class"]
                ],
                line=dict(color="#000000", width=1.2),
            ),
            text=special["planting_label"],
            textposition="outside",
            customdata=special[
                [
                    "planting_label",
                    "irrigated_yield_mean_kg_ha",
                    "maximum_irrigated_yield_kg_ha",
                    "yield_retained_pct",
                ]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Selected planting date: %{customdata[0]}<br>"
                "Minimum irrigation: %{y:,.1f} mm<br>"
                "Corresponding irrigated yield: %{customdata[1]:,.0f} kg/ha<br>"
                "Maximum irrigated yield: %{customdata[2]:,.0f} kg/ha<br>"
                "Yield retained: %{customdata[3]:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=special["maturity_class"],
            y=special["irrigated_yield_mean_kg_ha"],
            name="Irrigated Yield (kg/ha)",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#1F1F1F", width=4.5),
            marker=dict(
                color="#FFFFFF",
                size=13,
                symbol="circle",
                line=dict(color="#1F1F1F", width=2.5),
            ),
            customdata=special[
                ["planting_label", "yield_retained_pct"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Selected planting date: %{customdata[0]}<br>"
                "Corresponding irrigated yield: %{y:,.0f} kg/ha<br>"
                "Yield retained: %{customdata[1]:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fix05_layout(
        fig,
        "Maturity class",
        "Minimum irrigation retaining ≥95% of maximum yield (mm)",
        "Response",
        620,
    )

    fig.update_layout(
        # SAFE20_FIX05 secondary-axis styling:
        yaxis2=dict(
            title=dict(
                text="Irrigated Yield (kg/ha)",
                font=dict(size=22, color="#1F1F1F"),
                standoff=18,
            ),
            tickfont=dict(size=18, color="#1F1F1F"),
            ticks="outside",
            ticklen=8,
            tickwidth=2,
            tickcolor="#1F1F1F",
            showline=True,
            linecolor="#1F1F1F",
            linewidth=2,
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
            automargin=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title_text="",
        ),
        margin=dict(t=105, r=135),
        bargap=0.52,
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=MATURITIES,
    )

    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Bars show the minimum mean irrigation required to retain at least 95% "
        "of maximum mean irrigated yield. Bar labels identify the selected planting "
        "date. The secondary-axis line shows Irrigated Yield (kg/ha) at the selected option."
    )

else:
    # All other Yield & Water responses retain the existing single-axis figure.
    fig = go.Figure()

    for maturity in MATURITIES:
        s = plot[plot["maturity_class"].eq(maturity)].copy()
        if s.empty:
            continue

        # Reindex to all six canonical planting dates.
        s = (
            s.set_index("planting_label")
            .reindex(DATES)
            .rename_axis("planting_label")
            .reset_index()
        )

        sty = FIX05_MATURITY_STYLE[maturity]

        fig.add_trace(
            go.Scatter(
                x=DATES,
                y=s[metric],
                mode="lines+markers",
                name=maturity,
                connectgaps=False,
                line=dict(
                    color=sty["color"],
                    width=5.2,
                    dash=sty["dash"],
                ),
                marker=dict(
                    color=sty["color"],
                    size=13,
                    symbol=sty["symbol"],
                    line=dict(color="#000000", width=1.8),
                ),
                hovertemplate=(
                    f"<b>{maturity}</b><br>"
                    "Planting date: %{x}<br>"
                    + metric_name
                    + ": %{y:,.2f}<extra></extra>"
                ),
            )
        )

    fix05_layout(
        fig,
        "Planting date",
        metric_name,
        "Maturity class",
        600,
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=DATES,
        tickmode="array",
        tickvals=DATES,
        ticktext=DATES,
    )

    st.plotly_chart(fig, width="stretch")

    st.markdown(
        "**Line key:** "
        "LS = red ● solid | "
        "MS = blue ■ dashed | "
        "SS = green ◆ dotted | "
        "VSS = purple ▲ dash-dot"
    )

# Date-completeness diagnostic.
expected = set(DATES)
coverage = (
    q.groupby("maturity_class")["planting_label"]
     .apply(lambda x: sorted(set(x.dropna()), key=lambda d: DATES.index(d) if d in DATES else 999))
)

missing_messages = []
for maturity in MATURITIES:
    dates_present = set(coverage.get(maturity, []))
    missing = [d for d in DATES if d not in dates_present]
    if missing:
        missing_messages.append(f"{maturity}: {', '.join(missing)}")

if missing_messages:
    st.info(
        "The x-axis always shows all six planting dates. "
        "If a maturity class has no validated value for a date, the line is left blank at that date. "
        "Missing data: " + " | ".join(missing_messages)
    )

with st.expander("Response definitions and units"):
    st.markdown(
        """
- **Rainfed yield (kg/ha):** mean simulated grain yield under rainfed management.
- **Irrigated yield (kg/ha):** mean simulated grain yield under irrigated management.
- **Irrigation requirement (mm):** mean seasonal irrigation water applied/required in the irrigated simulation.
- **Irrigation yield benefit (kg/ha):** irrigated yield minus rainfed yield.
- **Incremental IWUE (kg/m³):** irrigation-induced yield gain per cubic meter of irrigation water.
- **Gross irrigation productivity (kg/m³):** irrigated grain yield per cubic meter of irrigation water.
- **Yield gap (%):** percentage yield-gap response in the validated paired derivative table.
- **Seasonal rainfall (mm):** mean crop-season precipitation for the rainfed simulation window.
- **Minimum irrigation retaining ≥95% of maximum yield (mm):** within the selected region and maturity class, the lowest mean irrigation requirement among planting dates whose mean irrigated yield is at least 95% of the maximum mean irrigated yield.
        """
    )

if is_min95 and min95_display is not None:
    st.dataframe(
        min95_display.round(2),
        width="stretch",
        hide_index=True,
    )
else:
    st.dataframe(
        q.sort_values(
            ["maturity_class", "planting_label"],
            key=lambda s: s.map({d: i for i, d in enumerate(DATES)}) if s.name == "planting_label" else s
        ),
        width="stretch",
        hide_index=True,
    )
