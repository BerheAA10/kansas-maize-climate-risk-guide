# SAFE19_FIX02 no-download policy

The Streamlit application intentionally provides:
- no `st.download_button`
- no Downloads page
- no downloadable provenance/report controls
- no report assets in the deployment bundle

The app displays selected scientific summaries, charts, maps, and figures only.

## Important GitHub limitation

A PUBLIC GitHub repository makes every committed file downloadable from GitHub.
If the underlying derivative CSVs, scripts, or figures must not be downloadable,
use a PRIVATE GitHub repository for deployment.

No web application can prevent a viewer from manually copying displayed values
or capturing screenshots of information that is visible on screen.
