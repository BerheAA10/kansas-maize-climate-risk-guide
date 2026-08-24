import pandas as pd
import re

CULTIVAR_ID_TO_MATURITY = {
    "990001": "LS",
    "990002": "MS",
    "990003": "SS",
    "990004": "VSS",
}

def ensure_maturity_class(df):
    """Return a copy with canonical maturity_class (LS/MS/SS/VSS)."""
    out = df.copy()

    if "maturity_class" in out.columns:
        s = out["maturity_class"].astype(str).str.strip()
        long_map = {
            "Long Season": "LS",
            "Medium Season": "MS",
            "Short Season": "SS",
            "Very Short Season": "VSS",
            "V. Short Season": "VSS",
        }
        out["maturity_class"] = s.replace(long_map)
        return out

    if "cultivar_id" in out.columns:
        cid = (
            out["cultivar_id"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.extract(r"(99000[1-4])", expand=False)
        )
        out["maturity_class"] = cid.map(CULTIVAR_ID_TO_MATURITY)

    if "cultivar_label" in out.columns:
        lab = out["cultivar_label"].astype(str).str.strip()
        label_map = {
            "LS": "LS", "MS": "MS", "SS": "SS", "VSS": "VSS",
            "Long Season": "LS", "Medium Season": "MS",
            "Short Season": "SS", "Very Short Season": "VSS",
            "V. Short Season": "VSS",
        }
        mapped = lab.map(label_map)
        lower = lab.str.lower()
        mapped = mapped.fillna(
            lower.map(
                lambda x: (
                    "VSS" if ("very short" in x or "v. short" in x) else
                    "LS" if "long season" in x else
                    "MS" if "medium season" in x else
                    "SS" if "short season" in x else
                    None
                )
            )
        )
        if "maturity_class" not in out.columns:
            out["maturity_class"] = mapped
        else:
            out["maturity_class"] = out["maturity_class"].fillna(mapped)

    if "maturity_class" not in out.columns:
        out["maturity_class"] = pd.NA

    return out


CANONICAL_PLANTING_DATES = [
    "April 1", "April 10", "April 20",
    "May 1", "May 10", "May 20",
]

PLANTING_CODE_TO_LABEL = {
    "A1": "April 1",
    "A01": "April 1",
    "APR1": "April 1",
    "APR01": "April 1",
    "A10": "April 10",
    "APR10": "April 10",
    "A20": "April 20",
    "APR20": "April 20",
    "M1": "May 1",
    "M01": "May 1",
    "MAY1": "May 1",
    "MAY01": "May 1",
    "M10": "May 10",
    "MAY10": "May 10",
    "M20": "May 20",
    "MAY20": "May 20",
}

def _canonical_date_from_text(value):
    """Map common planting-date spellings/codes to the six canonical labels."""
    if pd.isna(value):
        return None

    raw = str(value).strip()
    if not raw:
        return None

    # Already canonical.
    if raw in CANONICAL_PLANTING_DATES:
        return raw

    # Compact code normalization.
    compact = re.sub(r"[^A-Za-z0-9]", "", raw).upper()
    if compact in PLANTING_CODE_TO_LABEL:
        return PLANTING_CODE_TO_LABEL[compact]

    # Human-readable month variants.
    low = raw.lower().replace(",", " ")
    low = re.sub(r"\s+", " ", low).strip()

    month_match = re.search(
        r"\b(apr(?:il)?|may)\s*0?(1|10|20)\b",
        low,
        flags=re.IGNORECASE,
    )
    if month_match:
        month = month_match.group(1).lower()
        day = int(month_match.group(2))
        if month.startswith("apr") and day in {1, 10, 20}:
            return f"April {day}"
        if month == "may" and day in {1, 10, 20}:
            return f"May {day}"

    # Numeric month/day variants such as 04-01, 4/1, 05_20.
    numeric = re.search(
        r"(?<!\d)(0?4|0?5)[\-/_. ]+0?(1|10|20)(?!\d)",
        low,
    )
    if numeric:
        month = int(numeric.group(1))
        day = int(numeric.group(2))
        if month == 4 and day in {1, 10, 20}:
            return f"April {day}"
        if month == 5 and day in {1, 10, 20}:
            return f"May {day}"

    return None


def ensure_planting_label(df):
    """
    Return a copy with canonical planting_label values:
    April 1, April 10, April 20, May 1, May 10, May 20.

    The function does not modify source files. It preferentially uses
    planting_code when present and falls back to planting_label text.
    """
    out = df.copy()

    canonical = pd.Series(pd.NA, index=out.index, dtype="object")

    if "planting_code" in out.columns:
        from_code = out["planting_code"].map(_canonical_date_from_text)
        canonical = canonical.fillna(from_code)

    if "planting_label" in out.columns:
        from_label = out["planting_label"].map(_canonical_date_from_text)
        canonical = canonical.fillna(from_label)

    out["planting_label"] = canonical
    return out
