import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import (
    ensure_planting_label,
    load_table, source_badge, REGIONS, SCENARIOS, MATURITIES, DATES, MATURITY_COLORS, apply_publication_plot_style
)

st.title("Producer Optimizer")
safe14, src14 = load_table("safe14_integrated")
paired, srcp = load_table("regional_paired")

if safe14.empty:
    st.warning(
        "The validated SAFE14 integrated table is required for the Producer Optimizer. "
        "Prepare the public bundle from the validated H-drive outputs."
    )
    st.stop()

source_badge(src14)

# Normalize expected schemas.
d = ensure_planting_label(safe14.copy())
d = d[d["planting_label"].notna()].copy()
if "maturity_class" not in d.columns and "cultivar_id" in d.columns:
    cmap = {"990001":"LS","990002":"MS","990003":"SS","990004":"VSS"}
    cid = d["cultivar_id"].astype(str).str.replace(r"\.0$","",regex=True)
    d["maturity_class"] = cid.map(cmap)

# Add IWUE / paired metrics when available.
if not paired.empty:
    p = paired.copy()
    if "maturity_class" not in p.columns:
        cmap = {"990001":"LS","990002":"MS","990003":"SS","990004":"VSS"}
        cid = p["cultivar_id"].astype(str).str.replace(r"\.0$","",regex=True)
        p["maturity_class"] = cid.map(cmap)
    keep = [
        c for c in [
            "region","planting_label","maturity_class",
            "incremental_iwue_mean_kg_m3",
            "gross_irrigation_productivity_mean_kg_m3",
            "irrigation_mean_mm",
            "rainfed_seasonal_precip_mean_mm",
        ] if c in p.columns
    ]
    if {"region","planting_label","maturity_class"}.issubset(keep):
        p = p[keep].drop_duplicates(["region","planting_label","maturity_class"])
        # SAFE14 may already have irrigation_mean_mm; keep SAFE14 value first.
        d = d.merge(
            p,
            on=["region","planting_label","maturity_class"],
            how="left",
            suffixes=("","_paired")
        )
        if "irrigation_mean_mm_paired" in d.columns:
            if "irrigation_mean_mm" not in d.columns:
                d["irrigation_mean_mm"] = d["irrigation_mean_mm_paired"]
            else:
                d["irrigation_mean_mm"] = d["irrigation_mean_mm"].fillna(
                    d["irrigation_mean_mm_paired"]
                )

c1, c2, c3 = st.columns(3)
region = c1.selectbox("Region", REGIONS)
scenario = c2.selectbox("Water regime", SCENARIOS)
maturity_scope = c3.selectbox("Maturity class to consider", ["All maturity classes", "LS", "MS", "SS", "VSS"])

q = d[(d["region"] == region) & (d["scenario"] == scenario)].copy()
if maturity_scope != "All maturity classes":
    q = q[q["maturity_class"].eq(maturity_scope)].copy()

if q.empty:
    st.warning("No validated optimizer rows exist for this selection.")
    st.stop()

st.subheader("Producer priorities")
st.info(
    "**Important:** the priority controls below are decision weights, not measurements from one cultivar. "
    "They are applied to every planting-date × maturity-class candidate allowed by the **Maturity class to consider** selection above."
)
st.markdown(f"**Current optimization scope:** {region} · {scenario} · **{maturity_scope}**")

profile = st.selectbox(
    "Decision profile",
    [
        "Balanced resilience",
        "Maximum yield",
        "Near-optimal yield with lower thermal risk",
        "Water-conscious irrigated production",
        "Custom weights",
    ],
)

# Default weights sum need not equal 100; the optimizer normalizes them.
defaults = {
    "Balanced resilience": (40, 30, 15, 10, 5),
    "Maximum yield": (70, 15, 5, 5, 5),
    "Near-optimal yield with lower thermal risk": (45, 40, 5, 5, 5),
    "Water-conscious irrigated production": (35, 25, 25, 10, 5),
    "Custom weights": (40, 30, 15, 10, 5),
}
wy, wt, ww, wp, wi = defaults[profile]

if profile == "Custom weights":
    a,b,c,dw,e = st.columns(5)
    wy = a.slider("Weight — Yield",0,100,wy,5)
    wt = b.slider("Weight — Thermal risk",0,100,wt,5)
    ww = c.slider("Weight — Irrigation",0,100,ww,5)
    wp = dw.slider("Weight — Yield penalty",0,100,wp,5)
    wi = e.slider("Weight — IWUE",0,100,wi,5)

near_optimal = st.checkbox(
    "Restrict to options ≥95% of maximum yield",
    value=(profile == "Near-optimal yield with lower thermal risk"),
)

# For rainfed systems irrigation/IWUE should not influence ranking.
if scenario == "Rainfed":
    ww = 0
    wi = 0

# Determine metrics.
yield_col = "mean_yield_kg_ha"
thermal_col = (
    "thermal_screening_index_pct"
    if "thermal_screening_index_pct" in q.columns
    else None
)
penalty_col = "yield_penalty_pct" if "yield_penalty_pct" in q.columns else None
irrig_col = "irrigation_mean_mm" if "irrigation_mean_mm" in q.columns else None
iwue_col = (
    "incremental_iwue_mean_kg_m3"
    if "incremental_iwue_mean_kg_m3" in q.columns
    else None
)

needed = [yield_col]
if not all(c in q.columns for c in needed):
    st.error("Required validated yield metric is missing.")
    st.stop()

if near_optimal:
    ymax = pd.to_numeric(q[yield_col],errors="coerce").max()
    q = q[pd.to_numeric(q[yield_col],errors="coerce") >= 0.95*ymax].copy()

def benefit_norm(s):
    x = pd.to_numeric(s,errors="coerce")
    lo,hi = x.min(),x.max()
    if not np.isfinite(lo) or not np.isfinite(hi) or hi == lo:
        return pd.Series(0.5,index=s.index)
    return (x-lo)/(hi-lo)

def cost_norm(s):
    return 1-benefit_norm(s)

scores = pd.Series(0.0,index=q.index)
weight_sum = 0.0

scores += wy * benefit_norm(q[yield_col]); weight_sum += wy

if thermal_col:
    scores += wt * cost_norm(q[thermal_col]); weight_sum += wt

if penalty_col:
    scores += wp * cost_norm(q[penalty_col]); weight_sum += wp

if scenario == "Irrigated" and irrig_col and ww > 0:
    scores += ww * cost_norm(q[irrig_col]); weight_sum += ww

if scenario == "Irrigated" and iwue_col and wi > 0:
    scores += wi * benefit_norm(q[iwue_col]); weight_sum += wi

if weight_sum <= 0:
    st.error("At least one optimizer weight must be greater than zero.")
    st.stop()

q["producer_score"] = 100 * scores / weight_sum
q = q.sort_values(
    ["producer_score", yield_col],
    ascending=[False, False]
).reset_index(drop=True)
q["rank"] = np.arange(1,len(q)+1)

top = q.head(5).copy()

best = top.iloc[0]
best_maturity = str(best["maturity_class"])
best_date = str(best["planting_label"])

st.success(
    f"Top-ranked producer option: **{best_date} planting · {best_maturity} maturity class** "
    f"with Producer Score **{best['producer_score']:.1f}/100**."
)

st.warning(
    f"All performance cards below refer specifically to **{best_maturity} maturity class**, planted on **{best_date}**, under **{scenario}** conditions in **{region}**."
)

id1, id2, id3 = st.columns(3)
id1.metric("Recommended maturity class", best_maturity)
id2.metric("Recommended planting date", best_date)
id3.metric("Producer Score", f"{best['producer_score']:.1f}/100")

st.markdown(
    f"### Selected cultivar maturity class: **{best_maturity}**  "
    f"| Planting date: **{best_date}**"
)

st.markdown(
    f"**Performance metrics below are for: {best_date} × {best_maturity} × {scenario} × {region}.**"
)

m1,m2,m3,m4 = st.columns(4)
m1.metric(f"{best_maturity} mean yield", f"{best[yield_col]:,.0f} kg/ha")
if thermal_col and pd.notna(best.get(thermal_col)):
    m2.metric(f"{best_maturity} thermal screening", f"{best[thermal_col]:.1f}%")
else:
    m2.metric(f"{best_maturity} thermal screening","—")
if penalty_col and pd.notna(best.get(penalty_col)):
    m3.metric(f"{best_maturity} yield penalty", f"{best[penalty_col]:.1f}%")
else:
    m3.metric(f"{best_maturity} yield penalty","—")
if scenario == "Irrigated" and irrig_col and pd.notna(best.get(irrig_col)):
    m4.metric(f"{best_maturity} irrigation", f"{best[irrig_col]:.0f} mm")
else:
    m4.metric("Water regime", scenario)

show_cols = [
    "rank","planting_label","maturity_class","producer_score",
    yield_col,
]
for c in [
    thermal_col, penalty_col,
    irrig_col if scenario=="Irrigated" else None,
    iwue_col if scenario=="Irrigated" else None,
    "p_freeze_growing_pct",
    "p_heat35_flowering_pct",
    "p_heat38_flowering_pct",
]:
    if c and c in top.columns and c not in show_cols:
        show_cols.append(c)

st.subheader("Top five producer options")
display_top = top[show_cols].round(2).copy()
display_top = display_top.rename(columns={
    "maturity_class": "Maturity class",
    "planting_label": "Planting date",
    "producer_score": "Producer Score",
    "mean_yield_kg_ha": "Mean yield (kg/ha)",
    "thermal_screening_index_pct": "Thermal screening (%)",
    "yield_penalty_pct": "Yield penalty (%)",
    "irrigation_mean_mm": "Irrigation (mm)",
    "incremental_iwue_mean_kg_m3": "Incremental IWUE (kg/m³)",
    "p_freeze_growing_pct": "Freeze probability (%)",
    "p_heat35_flowering_pct": "Flowering heat ≥35°C (%)",
    "p_heat38_flowering_pct": "Flowering heat ≥38°C (%)",
})
st.dataframe(
    display_top,
    width="stretch",
    hide_index=True,
)

st.subheader("Yield–thermal-risk trade-off")
if thermal_col:
    fig = px.scatter(
        q,
        x=thermal_col,
        y=yield_col,
        color="maturity_class",
        symbol="planting_label",
        size="producer_score",
        color_discrete_map=MATURITY_COLORS,
        hover_data=[c for c in [penalty_col,irrig_col,iwue_col] if c and c in q.columns],
        labels={
            thermal_col:"Thermal screening index (%)",
            yield_col:"Mean yield (kg/ha)",
            "maturity_class":"Maturity class",
            "planting_label":"Planting date",
        },
    )
    fig.update_traces(marker=dict(line=dict(width=1.1,color="#111111")))
    apply_publication_plot_style(
        fig,
        x_title="Thermal screening index (%)",
        y_title="Mean yield (kg/ha)",
        legend_title="Maturity class / planting date",
        height=540,
    )
    st.plotly_chart(fig,width="stretch")

st.caption(
    "Producer Score is a relative decision-support ranking within the selected region and water regime. "
    "It is not an economic optimum, crop-insurance recommendation, or replacement for current local weather "
    "and hybrid-specific management information."
)


st.divider()
st.markdown(
    """
Decision-support ranking for **planting date × maturity class** within a selected Kansas region
and water regime. The optimizer does not change DSSAT outputs; it ranks validated long-term
derivative metrics according to the producer's priorities.
"""
)
