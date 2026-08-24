import streamlit as st

st.title("Methods & definitions")

st.subheader("Study design")
st.markdown("""
- 2,776 Kansas DSSAT/CERES-Maize sites
- 1981–2018 (38 years)
- planting dates: April 1, April 10, April 20, May 1, May 10, May 20
- maturity classes: LS, MS, SS, VSS
- water regimes: Rainfed and Irrigated
""")

st.subheader("Thermal exposure")
st.markdown("""
**Flowering heat:** anthesis-centered flowering/silking proxy (ADAT ±7 days, clipped to the crop cycle).
Thresholds: Tmax ≥30, ≥35, ≥38°C.

**Late-season cold/freeze:** threshold reached after July 1 and before/on DSSAT physiological maturity.
Thresholds: Tmin ≤0, ≤−2.2, ≤−4°C.
""")

st.subheader("Planting-date yield penalty")
st.latex(r"P_{planting}=Y_{best\ date}-Y_{current\ date}")

st.subheader("SAFE16 heat-associated penalty")
st.latex(r"P_{heat}=\hat Y_{low\ heat}-\hat Y_{observed\ flowering\ heat}")
st.write(
    "SAFE16 used continuous flowering EDD35 and a low-heat counterfactual. "
    "It is a model-based heat-associated component, not direct DSSAT tissue-damage simulation."
)

st.subheader("SAFE17 aligned heat-versus-cold penalty")
st.write(
    "For every binary temperature threshold, treatment-year yield was analyzed using the same "
    "site + year fixed-effects estimand. Positive penalty means yield was lower when the temperature event occurred."
)
st.latex(r"P_{temperature}=-\beta_{event}")
st.latex(r"P_{\%}=100\times P_{temperature}/\bar Y_{no-event}")

st.subheader("Interpretation safeguards")
st.markdown("""
- Native DSSAT yield is never overwritten or thermally adjusted in the main analyses.
- Temperature-associated penalties are statistical associations, not experimental causal damage coefficients.
- Event/no-event overlap matters. Cells with near-universal or very rare exposure should be interpreted cautiously.
- Best-planting-date maps interpolate each date-specific continuous surface first, then choose the best date per cell; categorical date codes are never interpolated.
""")
