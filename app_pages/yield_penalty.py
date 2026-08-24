import streamlit as st
import plotly.graph_objects as go
from dashboard_utils import load_table, source_badge, REGIONS, MATURITIES, SCENARIOS, DATES, format_threshold_order, FIX05_PLANTING_STYLE, FIX05_MATURITY_STYLE, fix05_layout, ensure_planting_label

st.title("Temperature-associated yield penalties")
full,src=load_table("safe17_regional_models")
if full.empty:
    demo,dsrc=load_table("water_maturity_summary"); source_badge(dsrc)
    st.info("Full regional model export is not present, so this page is showing the water × maturity summary.")
    if demo.empty: st.stop()
    scenario=st.selectbox("Water regime",SCENARIOS); d=format_threshold_order(demo[demo["scenario"].eq(scenario)].copy())
    metric=st.radio("Penalty metric",["kg/ha","%"],horizontal=True); ycol="median_penalty_kg_ha" if metric=="kg/ha" else "median_penalty_pct"
    fig=go.Figure()
    for maturity in MATURITIES:
        s=d[d["maturity_class"].eq(maturity)]
        if s.empty: continue
        sty=FIX05_MATURITY_STYLE[maturity]
        fig.add_trace(go.Bar(x=s["threshold"],y=s[ycol],name=maturity,marker_color=sty["color"],marker_line_color="#000000",marker_line_width=1.2))
    fig.add_hline(y=0,line_width=1.8,line_color="#000000"); fix05_layout(fig,"Temperature threshold",f"Median penalty ({metric})","Maturity class",560); fig.update_layout(barmode="group")
    st.plotly_chart(fig,width="stretch"); st.dataframe(d,width="stretch",hide_index=True); st.stop()
source_badge(src); d=full.copy()
c1,c2,c3,c4=st.columns(4); region=c1.selectbox("Region",REGIONS); scenario=c2.selectbox("Water regime",SCENARIOS); maturity=c3.selectbox("Maturity",MATURITIES); family=c4.selectbox("Stress",["Heat","Cold"])
q=d[(d["region"].eq(region))&(d["scenario"].eq(scenario))&(d["maturity_class"].eq(maturity))&(d["family"].eq(family))].copy(); q=format_threshold_order(q)
metric=st.radio("Penalty metric",["kg/ha","%"],horizontal=True); ycol="associated_penalty_kg_ha" if metric=="kg/ha" else "associated_penalty_pct"
fig=go.Figure()
for planting in DATES:
    s=q[q["planting_label"].eq(planting)].copy()
    if s.empty: continue
    sty=FIX05_PLANTING_STYLE[planting]
    fig.add_trace(go.Scatter(x=s["threshold_label"],y=s[ycol],mode="lines+markers",name=planting,
        line=dict(color=sty["color"],width=5.2,dash=sty["dash"]),
        marker=dict(color=sty["color"],size=13,symbol=sty["symbol"],line=dict(color="#000000",width=1.8)),
        hovertemplate=f"<b>{planting}</b><br>Threshold: %{{x}}<br>Penalty ({metric}): %{{y:,.2f}}<extra></extra>"))
fig.add_hline(y=0,line_width=1.8,line_color="#000000"); fix05_layout(fig,"Temperature threshold",f"Temperature-associated yield penalty ({metric})","Planting date",610)
st.plotly_chart(fig,width="stretch")
st.markdown("**Planting-date line key:** April 1 red ● solid; April 10 blue ■ dashed; April 20 green ◆ dotted; May 1 purple ▲ dash-dot; May 10 orange ▼ long-dash; May 20 black ✕ long-dash-dot.")
st.subheader("Frequency versus consequence")
fig2=go.Figure(); threshold_colors={"Tmax ≥ 30°C":"#1F77B4","Tmax ≥ 35°C":"#FF7F0E","Tmax ≥ 38°C":"#D62728","Tmin ≤ 0°C":"#17BECF","Tmin ≤ −2.2°C":"#9467BD","Tmin ≤ −4°C":"#111111"}
for planting in DATES:
    s=q[q["planting_label"].eq(planting)].copy(); sty=FIX05_PLANTING_STYLE[planting]
    if s.empty: continue
    for _,r in s.iterrows():
        fig2.add_trace(go.Scatter(x=[r["event_probability_pct"]],y=[r["associated_penalty_kg_ha"]],mode="markers",name=planting,legendgroup=planting,showlegend=False,
            marker=dict(color=threshold_colors.get(str(r["threshold_label"]),sty["color"]),size=13,symbol=sty["symbol"],line=dict(color="#000000",width=1.7)),
            hovertemplate=f"<b>{planting}</b><br>{r['threshold_label']}<br>Event probability: %{{x:.2f}}%<br>Associated penalty: %{{y:,.0f}} kg/ha<extra></extra>"))
    fig2.add_trace(go.Scatter(x=[None],y=[None],mode="markers",name=planting,legendgroup=planting,showlegend=True,marker=dict(color=sty["color"],size=12,symbol=sty["symbol"],line=dict(color="#000000",width=1.5))))
fig2.add_hline(y=0,line_width=1.8,line_color="#000000"); fix05_layout(fig2,"Event probability (%)","Associated yield penalty (kg/ha)","Planting date",590)
st.plotly_chart(fig2,width="stretch")
show=q[[c for c in ["planting_label","threshold_label","event_probability_pct","associated_penalty_kg_ha","associated_penalty_pct","p_value","fe_status"] if c in q.columns]]
st.dataframe(show,width="stretch",hide_index=True)
