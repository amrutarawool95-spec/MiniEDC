from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "data" / "output"
QUERY_LOG_PATH = OUTPUT_DIR / "queries.csv"
SPEC_CSV_PATH = ROOT_DIR / "docs" / "data-validation-spec.csv"
SPEC_MD_PATH = ROOT_DIR / "docs" / "data-validation-spec.md"

FORM_FILES = {
    "DM": RAW_DATA_DIR / "dm.csv",
    "VS": RAW_DATA_DIR / "vs.csv",
    "AE": RAW_DATA_DIR / "ae.csv",
    "CM": RAW_DATA_DIR / "cm.csv",
}

SITE_IDS = [f"S{i:02d}" for i in range(1, 7)]
VISITS = ["Screening", "Baseline", "Week 2", "Week 4", "Week 8"]
VISIT_ORDER = {visit: position for position, visit in enumerate(VISITS)}
STUDY_NAME = "MHP-201 — Fictional Phase II Hypertension Trial"
SYNTHETIC_NOTICE = (
    "Training portfolio only. Every record is synthetic; this is not a clinical "
    "system and must not be used for patient care or real trial decisions."
)