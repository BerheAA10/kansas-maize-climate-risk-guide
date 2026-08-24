from pathlib import Path
from datetime import datetime
import shutil, json, sys, os

# READ ONLY validated roots / preferred exact outputs.
H = Path(r"H:\\")

PREFERRED = {
    "sixdate": Path(r"H:\Kansas_Maize_4Cultivars_6Date_Regional_Analysis_SAFE02"),
    "safe13": Path(r"H:\Kansas_Maize_ThermalRisk_SAFE13_20260823_123650"),
    "safe14": Path(r"H:\Kansas_Maize_ThermalYield_Synthesis_SAFE14_FIX01_20260824_073646"),
    "safe16": Path(r"H:\Kansas_Maize_HeatAssociatedYieldPenalty_SAFE16_FIX01_20260824_111336"),
    "safe17": Path(r"H:\Kansas_Maize_HeatVsCold_YieldPenalty_SAFE17_FIX01_20260824_115305"),
}

TABLES = [
    ("sixdate/02_Tables/regional_longterm_paired_metrics.csv","regional_longterm_paired_metrics.csv"),
    ("sixdate/02_Tables/regional_longterm_yield_water.csv","regional_longterm_yield_water.csv"),
    ("safe13/04_Regional_Statewide/regional_thermal_risk_summary_long.csv","regional_thermal_risk_summary_long.csv"),
    ("safe14/02_Integrated/regional_yield_water_thermal_integrated_SAFE14.csv","regional_yield_water_thermal_integrated.csv"),
    ("safe16/03_Penalties/regional_date_total_and_heat_associated_penalty_SAFE16_FIX01.csv","regional_date_heat_associated_penalty.csv"),
    ("safe17/03_Models/regional_aligned_heat_cold_FE_penalties_SAFE17_FIX01.csv","regional_aligned_heat_cold_FE_penalties.csv"),
    ("safe17/04_Tables/heat_vs_cold_threshold_overall_summary_SAFE17_FIX01.csv","heat_vs_cold_threshold_overall_summary.csv"),
    ("safe17/04_Tables/TOP30_regional_temperature_penalties_kg_ha_SAFE17_FIX01.csv","top30_temperature_penalties_kg_ha.csv"),
    ("safe17/04_Tables/TOP30_regional_temperature_penalties_pct_SAFE17_FIX01.csv","top30_temperature_penalties_pct.csv"),
]

IMAGE_ROOTS = []

def resolve(spec):
    key,rel=spec.split("/",1)
    return PREFERRED[key]/Path(rel)

stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
repo=Path(__file__).resolve().parents[1]
out=repo.parent/f"{repo.name}_PUBLIC_BUNDLE_{stamp}"
if out.exists():
    raise SystemExit(f"Refusing to overwrite: {out}")
shutil.copytree(repo,out)

public=out/"data/public"
public.mkdir(parents=True,exist_ok=True)
copied=[]; missing=[]

for spec,name in TABLES:
    src=resolve(spec)
    if src.exists():
        shutil.copy2(src,public/name)
        copied.append(str(src))
    else:
        missing.append(str(src))

# Copy publication images only; never source masters.
for spec,destrel in IMAGE_ROOTS:
    src=resolve(spec)
    dest=out/"assets"/destrel
    if not src.exists():
        missing.append(str(src))
        continue
    dest.mkdir(parents=True,exist_ok=True)
    for p in src.rglob("*.png"):
        shutil.copy2(p,dest/p.name)


# Optional overview climate summary — use actual validated regional climate data when available.
climate_root = PREFERRED["sixdate"] / "Climate_Rainfall_ET_Temperature_SAFE01"
climate_dest = public / "regional_climate_overview.csv"

def _find_overview_climate_csv(root):
    if not root.exists():
        return None
    required = {
        "region",
        "mean_seasonal_rainfall_mm",
        "mean_crop_et_mm",
        "mean_tmax_c",
        "mean_tmin_c",
    }
    candidates = []
    for p in root.rglob("*.csv"):
        try:
            import pandas as pd
            cols = set(pd.read_csv(p, nrows=0).columns)
            if required.issubset(cols):
                candidates.append(p)
        except Exception:
            pass
    if not candidates:
        return None
    # Prefer files whose names suggest a regional means/summary product.
    candidates.sort(
        key=lambda p: (
            0 if any(k in p.name.lower() for k in ["regional", "mean", "summary"]) else 1,
            len(str(p)),
            p.name.lower(),
        )
    )
    return candidates[0]

climate_src = _find_overview_climate_csv(climate_root)
if climate_src is not None:
    shutil.copy2(climate_src, climate_dest)
    copied.append(str(climate_src))

manifest={
    "created":datetime.now().isoformat(),
    "source_projects_modified":False,
    "copied_sources":copied,
    "missing_optional_or_expected_sources":missing,
    "policy":"Only derivative tables and publication graphics were copied. No report/provenance download assets are exported."
}
(out/"data/public/PUBLIC_EXPORT_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

print("="*110)
print("KANSAS MAIZE STREAMLIT PUBLIC BUNDLE")
print("Output:",out)
print("Derivative tables copied:",len(copied))
print("Missing paths:",len(missing))
print("Source projects modified: NO")
print("STATUS: PASS_PUBLIC_BUNDLE")
print("="*110)
