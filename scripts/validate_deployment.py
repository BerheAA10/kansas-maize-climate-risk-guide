from pathlib import Path
import py_compile
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
errors = []

for p in [
    ROOT / "app.py",
    ROOT / "dashboard_utils.py",
    ROOT / "schema_utils.py",
    *sorted((ROOT / "app_pages").glob("*.py")),
    *sorted((ROOT / "scripts").glob("*.py")),
]:
    try:
        py_compile.compile(str(p), doraise=True)
    except Exception as e:
        errors.append(f"Syntax error in {p.name}: {e}")

expected_pages = {
    "home.py",
    "thermal_risk.py",
    "yield_penalty.py",
    "planting_maturity.py",
    "yield_water.py",
    "producer_optimizer.py",
    "methods.py",
}
got_pages = {p.name for p in (ROOT / "app_pages").glob("*.py")}
if expected_pages != got_pages:
    errors.append(f"Page set mismatch: {sorted(got_pages)}")

app = (ROOT / "app.py").read_text(encoding="utf-8")
if 'APP_BUILD = "SAFE19_FIX13"' not in app:
    errors.append("FIX13 build marker missing.")
if "maps_gallery.py" in app or "Maps & figures" in app:
    errors.append("Maps & figures navigation must be removed.")

if (ROOT / "app_pages" / "maps_gallery.py").exists():
    errors.append("maps_gallery.py must not exist in FIX11.")

# No visible development captions or validated-source captions on research pages.
for p in sorted((ROOT / "app_pages").glob("*.py")):
    txt = p.read_text(encoding="utf-8")
    if "Data source: validated public export from SAFE outputs." in txt:
        errors.append(f"Visible validated-source caption remains in {p.name}")
    if "SAFE19_FIX05 —" in txt or "SAFE19_FIX06 —" in txt or "SAFE19_FIX10 —" in txt:
        errors.append(f"Visible SAFE caption remains in {p.name}")

# No user-facing downloads.
for p in [ROOT / "app.py", *sorted((ROOT / "app_pages").glob("*.py"))]:
    txt = p.read_text(encoding="utf-8")
    if "download_button" in txt:
        errors.append(f"Download control prohibited in {p.name}")

# Source badge must be silent for validated export.
utils = (ROOT / "dashboard_utils.py").read_text(encoding="utf-8")
if 'st.caption("Data source: validated public export from SAFE outputs.")' in utils:
    errors.append("source_badge still renders validated-source text.")

# Six-date display retained.
yw = (ROOT / "app_pages" / "yield_water.py").read_text(encoding="utf-8")
for token in ["ensure_planting_label(df)", "tickvals=DATES", "ticktext=DATES"]:
    if token not in yw:
        errors.append(f"Yield & Water six-date contract missing: {token}")

# Explicit high-contrast line styling retained.
for name in ["yield_water.py", "planting_maturity.py", "yield_penalty.py"]:
    txt = (ROOT / "app_pages" / name).read_text(encoding="utf-8")
    if "go.Scatter" not in txt or "width=5.2" not in txt or "size=13" not in txt:
        errors.append(f"High-contrast line styling missing in {name}")

# Producer description must be at bottom.
opt = (ROOT / "app_pages" / "producer_optimizer.py").read_text(encoding="utf-8")
desc = "Decision-support ranking for **planting date × maturity class**"
if desc not in opt:
    errors.append("Producer Optimizer description missing.")
if opt.index(desc) < opt.index('st.subheader("Top five producer options")'):
    errors.append("Producer Optimizer description must be below the results.")

# Overview climate figures and larger/dark text.
home = (ROOT / "app_pages" / "home.py").read_text(encoding="utf-8")
for token in [
    "Climate context for the six regions",
    "Mean seasonal rainfall (mm)",
    "Mean crop evapotranspiration, ETCM (mm)",
    "Temperature (°C)",
    'title_font=dict(size=20, color="#000000")',
    'tickfont=dict(size=17, color="#000000")',
    "with st.container(border=True):",
    "def climate_chart_layout(fig, x_title, y_title, height=440):",
]:
    if token not in home:
        errors.append(f"Overview climate readability token missing: {token}")

for asset in [
    ROOT / "assets" / "overview" / "overview_rainfall_vs_et_scatter.png",
    ROOT / "assets" / "overview" / "overview_rainfall_et_bars.png",
    ROOT / "assets" / "overview" / "overview_tmax_tmin_bars.png",
]:
    if not asset.exists():
        errors.append(f"Overview fallback asset missing: {asset.name}")

launcher = ROOT / "RUN_BUILD_AND_LAUNCH_FIX13.ps1"
if not launcher.exists():
    errors.append("RUN_BUILD_AND_LAUNCH_FIX13.ps1 missing.")
else:
    ltxt = launcher.read_text(encoding="utf-8-sig")
    if "--server.port 8511" not in ltxt:
        errors.append("FIX13 launcher must use port 8511.")


# FIX13 Heat & freeze layout.
thermal = (ROOT / "app_pages" / "thermal_risk.py").read_text(encoding="utf-8")
for token in [
    "Thermal-risk threshold summary",
    '["Heat", "Cold / freeze"]',
    "with st.container(border=True):",
    "height=390",
    "height=455",
    "Two filters per row",
]:
    if token not in thermal:
        errors.append(f"FIX13 thermal layout token missing: {token}")

if "Kansas Maize Climate-Risk Atlas" in (ROOT / "app.py").read_text(encoding="utf-8"):
    errors.append("Atlas title must not remain in app.py.")
if "Kansas Maize Climate-Risk Atlas" in (ROOT / "app_pages" / "home.py").read_text(encoding="utf-8"):
    errors.append("Atlas title must not remain in home.py.")

if errors:
    print("VALIDATION FAILED")
    print("\n".join(errors))
    sys.exit(2)

print("SAFE19_FIX11 deployment validation: PASS")
