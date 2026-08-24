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

metrics = {
    "Rainfed yield": "rainfed_yield_mean_kg_ha",
    "Irrigated yield": "irrigated_yield_mean_kg_ha",
    "Irrigation requirement": "irrigation_mean_mm",
    "Irrigation yield benefit": "incremental_benefit_mean_kg_ha",
    "Incremental IWUE": "incremental_iwue_mean_kg_m3",
    "Gross irrigation productivity": "gross_irrigation_productivity_mean_kg_m3",
    "Yield gap": "yield_gap_mean_percent",
    "Seasonal rainfall": "rainfed_seasonal_precip_mean_mm",
}

q = df[df["region"].eq(region)].copy()
available = {k: v for k, v in metrics.items() if v in q.columns}

metric_name = st.selectbox("Response", list(available))
metric = available[metric_name]

# Aggregate defensively in case a derivative table contains repeated rows.
plot = (
    q.groupby(["maturity_class", "planting_label"], as_index=False, observed=False)[metric]
     .mean()
)

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

    fig.add_trace(go.Scatter(
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
            + metric_name + ": %{y:,.2f}<extra></extra>"
        ),
    ))

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

st.dataframe(
    q.sort_values(
        ["maturity_class", "planting_label"],
        key=lambda s: s.map({d: i for i, d in enumerate(DATES)}) if s.name == "planting_label" else s
    ),
    width="stretch",
    hide_index=True,
)
