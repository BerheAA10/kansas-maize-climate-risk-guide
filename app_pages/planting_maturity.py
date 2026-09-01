import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dashboard_utils import load_table, source_badge, REGIONS, MATURITIES, SCENARIOS, DATES, FIX05_MATURITY_STYLE, fix05_layout, ensure_planting_label

st.title("Planting date × maturity × thermal exposure")
df,src=load_table("safe14_integrated"); source_badge(src)
if df.empty: st.warning("Export SAFE14 integrated data to activate this page."); st.stop()
c1,c2=st.columns(2); region=c1.selectbox("Region",REGIONS); scenario=c2.selectbox("Water regime",SCENARIOS)
q=df[(df["region"].eq(region))&(df["scenario"].eq(scenario))].copy()

# SAFE20_FIX06_FIX03: planting-date yield penalty is relative to the
# best planting date and therefore cannot be negative.
for _penalty_col in ("yield_penalty_kg_ha", "yield_penalty_pct"):
    if _penalty_col in q.columns:
        q[_penalty_col] = q[_penalty_col].clip(lower=0)
metric_options={"Mean yield (kg/ha)":"mean_yield_kg_ha","Growing-season Tmin ≤0 probability (%)":"p_freeze_growing_pct","Flowering Tmax ≥35 probability (%)":"p_heat35_flowering_pct","Flowering Tmax ≥38 probability (%)":"p_heat38_flowering_pct","Reproductive Tmax ≥35 probability (%)":"p_heat35_reproductive_pct","Yield penalty relative to best planting date (kg/ha)":"yield_penalty_kg_ha","Yield penalty relative to best planting date (%)":"yield_penalty_pct"}
label=st.selectbox("Response",list(metric_options)); metric=metric_options[label]
q["planting_label"]=pd.Categorical(q["planting_label"],categories=DATES,ordered=True); q=q.sort_values(["maturity_class","planting_label"])
fig=go.Figure()
for maturity in MATURITIES:
    s=q[q["maturity_class"].eq(maturity)].copy()
    if s.empty: continue
    sty=FIX05_MATURITY_STYLE[maturity]
    fig.add_trace(go.Scatter(x=s["planting_label"].astype(str),y=s[metric],mode="lines+markers",name=maturity,
        line=dict(color=sty["color"],width=5.2,dash=sty["dash"]),
        marker=dict(color=sty["color"],size=13,symbol=sty["symbol"],line=dict(color="#000000",width=1.8)),
        hovertemplate=f"<b>{maturity}</b><br>Planting date: %{{x}}<br>{label}: %{{y:,.2f}}<extra></extra>"))
fix05_layout(fig,"Planting date",label,"Maturity class",600); fig.update_xaxes(categoryorder="array",categoryarray=DATES)
st.plotly_chart(fig,width="stretch")
st.markdown("**Line key:** LS = red ● solid | MS = blue ■ dashed | SS = green ◆ dotted | VSS = purple ▲ dash-dot")
if {"thermal_screening_index_pct","mean_yield_kg_ha"}.issubset(q.columns):
    st.subheader("Yield versus thermal screening")
    p_symbols={"April 1":"circle","April 10":"square","April 20":"diamond","May 1":"triangle-up","May 10":"triangle-down","May 20":"x"}
    fig2=go.Figure()
    for maturity in MATURITIES:
        s=q[q["maturity_class"].eq(maturity)].copy(); sty=FIX05_MATURITY_STYLE[maturity]
        if s.empty: continue
        for _,r in s.iterrows():
            fig2.add_trace(go.Scatter(x=[r["thermal_screening_index_pct"]],y=[r["mean_yield_kg_ha"]],mode="markers",name=maturity,legendgroup=maturity,showlegend=False,
                marker=dict(color=sty["color"],size=13,symbol=p_symbols.get(str(r["planting_label"]),"circle"),line=dict(color="#000000",width=1.6)),
                hovertemplate=f"<b>{maturity} · {r['planting_label']}</b><br>Thermal screening: %{{x:.2f}}%<br>Mean yield: %{{y:,.0f}} kg/ha<extra></extra>"))
        fig2.add_trace(go.Scatter(x=[None],y=[None],mode="markers",name=maturity,legendgroup=maturity,showlegend=True,marker=dict(color=sty["color"],size=12,symbol=sty["symbol"],line=dict(color="#000000",width=1.5))))
    fix05_layout(fig2,"Thermal screening index (%)","Mean yield (kg/ha)","Maturity class",560)
    st.plotly_chart(fig2,width="stretch")
