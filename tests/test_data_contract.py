from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_pages_exist_without_gallery():
    expected = {
        "home.py",
        "thermal_risk.py",
        "yield_penalty.py",
        "planting_maturity.py",
        "yield_water.py",
        "producer_optimizer.py",
        "methods.py",
    }
    got = {p.name for p in (ROOT / "app_pages").glob("*.py")}
    assert got == expected
    assert not (ROOT / "app_pages" / "maps_gallery.py").exists()


def test_no_visible_validated_source_caption():
    for p in sorted((ROOT / "app_pages").glob("*.py")):
        txt = p.read_text(encoding="utf-8")
        assert "Data source: validated public export from SAFE outputs." not in txt


def test_no_requested_safe_captions():
    for name in [
        "thermal_risk.py",
        "yield_penalty.py",
        "planting_maturity.py",
        "yield_water.py",
    ]:
        txt = (ROOT / "app_pages" / name).read_text(encoding="utf-8")
        assert "SAFE19_FIX05 —" not in txt
        assert "SAFE19_FIX06 —" not in txt
        assert "SAFE19_FIX10 —" not in txt


def test_six_planting_dates_retained():
    import sys
    sys.path.insert(0, str(ROOT))
    from schema_utils import ensure_planting_label

    d = pd.DataFrame({
        "planting_code": ["A1", "A10", "A20", "M1", "M10", "M20"],
    })
    out = ensure_planting_label(d)
    assert out["planting_label"].tolist() == [
        "April 1",
        "April 10",
        "April 20",
        "May 1",
        "May 10",
        "May 20",
    ]


def test_line_style_retained():
    for name in ["yield_water.py", "planting_maturity.py", "yield_penalty.py"]:
        txt = (ROOT / "app_pages" / name).read_text(encoding="utf-8")
        assert "go.Scatter" in txt
        assert "width=5.2" in txt
        assert "size=13" in txt


def test_producer_description_moved_to_bottom():
    txt = (ROOT / "app_pages" / "producer_optimizer.py").read_text(encoding="utf-8")
    desc = "Decision-support ranking for **planting date × maturity class**"
    assert desc in txt
    assert txt.index(desc) > txt.index('st.subheader("Top five producer options")')


def test_overview_larger_dark_climate_fonts():
    txt = (ROOT / "app_pages" / "home.py").read_text(encoding="utf-8")
    assert 'title_font=dict(size=20, color="#000000")' in txt
    assert 'tickfont=dict(size=17, color="#000000")' in txt
    assert "Climate context for the six regions" in txt
    assert "with st.container(border=True):" in txt
    assert "def climate_chart_layout(fig, x_title, y_title, height=440):" in txt


def test_no_download_controls():
    for p in [ROOT / "app.py", *sorted((ROOT / "app_pages").glob("*.py"))]:
        assert "download_button" not in p.read_text(encoding="utf-8")


def test_fix11_launcher():
    p = ROOT / "RUN_BUILD_AND_LAUNCH_FIX12.ps1"
    assert p.exists()
    assert "--server.port 8510" in p.read_text(encoding="utf-8-sig")
