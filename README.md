# Kansas Maize Climate-Risk Atlas — SAFE19

GitHub-ready Streamlit dashboard for the validated Kansas DSSAT planting-date, maturity, water, heat/freeze, and yield-penalty analyses.

## What the app showcases

- Heat probability at flowering/silking proxy: Tmax ≥30, ≥35, ≥38°C
- Late-season cold/freeze before physiological maturity: Tmin ≤0, ≤−2.2, ≤−4°C
- Temperature-associated yield penalties in kg/ha and %
- Event probability versus consequence
- Planting date × maturity × region × water-regime interactions
- Rainfed and irrigated yield
- irrigation requirement, irrigation benefit, incremental IWUE, gross irrigation productivity
- yield gap and planting-date yield penalty
- publication maps, heatmaps, and figures
- methods and scientific definitions

## Important data architecture

Streamlit Community Cloud cannot access the local Windows `H:\` drive.
Therefore the app uses compact derivative tables and publication graphics copied into the repository.

The full DSSAT masters remain local/read-only.

## Local test

PowerShell:

```powershell
.\RUN_LOCAL_SAFE19.ps1
```

The repository opens immediately in **demo mode** using the validated SAFE17 summary embedded under `data/demo/`.

## Build a public bundle from validated H-drive outputs

```powershell
.\RUN_PREPARE_PUBLIC_BUNDLE_SAFE19.ps1
```

This creates a **new timestamped folder** beside the repository. It never overwrites or modifies the validated SAFE source projects.

Inspect that timestamped folder before publishing.

## GitHub

Create a new repository, for example:

`kansas-maize-climate-risk-atlas`

Then from the reviewed SAFE19 public bundle:

```powershell
git init
git add .
git commit -m "Initial Kansas maize climate-risk atlas"
git branch -M main
git remote add origin https://github.com/YOUR-USER/kansas-maize-climate-risk-atlas.git
git push -u origin main
```

## Streamlit Community Cloud

Deploy `app.py` from the GitHub repository.

Recommended:
- keep `requirements.txt` in the repository root
- keep `.streamlit/config.toml` at repository root
- never commit `.streamlit/secrets.toml`
- use the same Python major/minor version locally and in deployment when possible

## Citation and scientific interpretation

The app distinguishes:
- native DSSAT outputs
- thermal exposure metrics
- planting-date yield penalties
- SAFE16 heat-associated counterfactual penalties
- SAFE17 aligned binary-event heat/cold fixed-effects penalties

Temperature-associated penalties are statistical associations and should not be described as direct experimental causal damage coefficients.


## SAFE19_FIX01 deployment repair

Validated local deployment exposed a schema mismatch in the Yield & Water page:
`regional_longterm_paired_metrics.csv` contains `cultivar_id` and `cultivar_label`
rather than `maturity_class`.

FIX01 derives canonical LS/MS/SS/VSS labels without changing the source CSV.
It also replaces deprecated Streamlit `use_container_width` arguments with
the current width API and adds a schema-compatibility validation gate.

No DSSAT, thermal, yield, or penalty calculations were changed.


## SAFE19_FIX02

Requested presentation/privacy changes:
- Publication gallery is filter-driven.
- No more than four maps/figures can be selected and displayed at one time.
- Added Producer Optimizer for region × water-regime planting-date/maturity ranking.
- Removed Downloads & provenance navigation page.
- Removed all Streamlit download buttons.
- Removed SAFE18 report files from the deployment bundle.
- Added no-download deployment guidance.

Important: if the GitHub repository is public, GitHub itself allows repository
files to be downloaded. Use a private GitHub repository if repository file
downloads are not acceptable.


## SAFE19_FIX03

Visualization and optimizer clarity improvements:
- Line charts now use high-contrast publication colors.
- LS/MS/SS/VSS use unique marker shapes and sharply separated colors.
- Planting-date penalty lines use six unique planting-date colors and symbols.
- Line widths and marker sizes were increased.
- Plot text, axis labels, ticks, and legends use dark/black text and larger fonts.
- Producer Optimizer explicitly displays the recommended maturity class and planting date
  beside yield, thermal screening, yield penalty, and irrigation metrics.

No validated DSSAT, heat/freeze, yield, or penalty calculations were changed.


## SAFE19_FIX04

User-visible corrections:
- Publication gallery now displays exactly one selected map/figure at a time.
- Line charts use strong red/blue/green/purple/orange/black colors.
- Maturity classes and planting dates use different marker shapes.
- Line dash patterns are also different, providing a third visual distinction.
- Line widths increased to ~4.6 px and markers to ~12 px.
- Chart text is black, with larger axis, tick, and legend fonts.
- Producer Optimizer explicitly identifies the recommended maturity class and
  planting date for all displayed performance metrics and in the top-five table.

No validated scientific calculations were changed.


## SAFE19_FIX05

This release rebuilds the affected pages rather than relying on inherited Plotly Express styling.

- Global sidebar badge: `Running SAFE19_FIX05`
- Gallery uses a single `selectbox` and displays exactly ONE image.
- Yield & Water uses explicit `go.Scatter` traces:
  - LS red circle solid
  - MS blue square dashed
  - SS green diamond dotted
  - VSS purple triangle dash-dot
- Planting date × maturity × thermal exposure uses the same explicit maturity encoding.
- Temperature-associated yield penalties use six explicit planting-date encodings.
- Lines are 5.2 px and markers are 13 px with black outlines.
- Chart fonts are larger and black.
- Producer Optimizer includes `Maturity class to consider` and explains that priority controls are weights applied across candidate classes.
- Result cards explicitly identify the selected maturity class and planting date.

No validated scientific calculations were changed.


## SAFE19_FIX06

- Overview begins with a Kansas map and compact key climate-risk information.
- The long study description, design cards, and source note are at the bottom of Overview.
- Heat & freeze risk is the final page in the Research atlas navigation group.
- Thermal threshold bars are narrow and compact with larger black text.
- Heat/cold stage definitions are below the charts.
- An interactive SAFE17 yield-impact explorer compares:
  planting date, maturity class, region, water regime, and temperature threshold.
- Available responses:
  associated yield penalty (kg/ha), associated yield penalty (%), and event probability (%).

No validated scientific calculations were changed.


## SAFE19_FIX07

- Overview now shows Kansas divided into the six study regions.
- Two climate-context panels are shown beside the map:
  - regional mean Tmax/Tmin when those validated columns are available
  - crop ET versus seasonal rainfall when those validated columns are available
- The gallery no longer relies on broad Any/Any/Any selection.
- A topic selection is now required before any map or figure is displayed.
- Users can refine by series, region, water regime, maturity class, and planting date.
- Candidate images are ranked and the gallery asks for refinement when too many remain.

No validated scientific calculations were changed.


## SAFE19_FIX08

Gallery selection was simplified to scientific criteria only.

- Removed the `Select ONE map or figure` filename selector.
- Required first choice: **Topic**.
- The app then detects which of **Region, Water regime, Maturity, Planting date** are actually encoded in that topic's available images.
- If multiple values exist for a dimension, the user must select one before any image is displayed.
- Once the scientific selection is sufficiently specific, the app automatically displays the best matching exported image.
- If multiple files match the same exact scientific selection, the highest-priority SAFE output is displayed automatically; filenames are not exposed as a selection control.

A one-command launcher, `RUN_BUILD_AND_LAUNCH_FIX08.ps1`, validates the package, creates a fresh public bundle, validates that bundle, and launches Streamlit on port 8505.

No validated scientific calculations were changed.


## SAFE19_FIX08_FIX01 launcher repair

The SAFE19_FIX08 dashboard itself was valid, and the exporter successfully created
the public bundle. The launcher failed because it treated `$Here` (a string path)
as if it were a FileInfo/DirectoryInfo object and used `$Here.Directory.FullName`.

FIX01:
- uses `$Parent = Split-Path -Parent $Here`;
- captures the exact `Output:` path printed by the exporter;
- falls back to a safe parent-directory search;
- uses ASCII console text to avoid dash/encoding artifacts;
- includes `RUN_EXISTING_FIX08_PUBLIC_BUNDLE.ps1` for public bundles already created.

No scientific data, models, calculations, figures, or source projects are changed.


## SAFE19_FIX09

- The overview now uses the supplied regional climate figures as static overview panels.
- A corrected Kansas state-outline map replaces the earlier approximate region-block map.
- The six study regions are shown as labeled representative locations within Kansas.
- New launchers are included: `RUN_BUILD_AND_LAUNCH_FIX09.ps1` and `RUN_EXISTING_FIX09_PUBLIC_BUNDLE.ps1`.
- Scientific calculations and data tables are unchanged.


## SAFE19_FIX10

The Yield & Water page previously converted `planting_label` directly to a fixed
Pandas categorical. Exported labels such as `April 01`, `May 01`, compact codes,
or other equivalent forms did not exactly equal the dashboard's canonical labels,
so they became missing values and rendered as `nan`.

FIX10:
- normalizes `planting_code` / `planting_label` into:
  `April 1`, `April 10`, `April 20`, `May 1`, `May 10`, `May 20`;
- never renders `NaN` as a planting date;
- explicitly fixes the x-axis to all six dates;
- leaves a visible gap only if a validated value is genuinely absent;
- applies the same normalization to other planting-date-sensitive pages.

No validated DSSAT or statistical calculations are changed.


## SAFE19_FIX11

Public-facing cleanup:
- removed the visible SAFE captions from Heat & Freeze, Yield Penalties,
  Planting Date × Maturity, and Yield & Water;
- suppressed the visible validated-public-export source caption;
- removed the Maps & Figures / Publication Gallery page and navigation;
- moved the Producer Optimizer introductory description to the bottom;
- increased Overview climate-chart axis titles to 20 px and tick labels to 17 px,
  using black text;
- the public-bundle exporter now attempts to locate the actual validated regional
  rainfall, crop ET, Tmax, and Tmin summary and uses it to render readable Plotly
  charts; supplied overview PNGs remain as fallback assets;
- no scientific calculations or validated source files were changed.


## SAFE19_FIX12

Overview climate-panel presentation refinement:
- increased the chart size for the three Overview climate panels;
- made the rainfall-vs-crop-ET panel less tight;
- placed each climate panel inside a rectangular bordered container for consistency;
- strengthened the plot frame using mirrored axis lines on all sides;
- no scientific calculations or validated source files were changed.
