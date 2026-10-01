"""Build reproducible, wholly synthetic MiniEDC study data."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from faker import Faker
import numpy as np
import pandas as pd

from miniedc.settings import FORM_FILES, SITE_IDS, VISITS

SEED = 20261001
STUDY_START = date(2025, 1, 6)


def _iso(value: date) -> str:
    return value.isoformat()


def _make_clean_forms(seed: int) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    fake = Faker("en_US")
    Faker.seed(seed)
    subject_ids = [f"MHP{i:03d}" for i in range(1, 121)]
    assigned_sites = np.resize(np.array(SITE_IDS), len(subject_ids))
    rng.shuffle(assigned_sites)

    dm_rows: list[dict[str, Any]] = []
    vs_rows: list[dict[str, Any]] = []
    ae_rows: list[dict[str, Any]] = []
    cm_rows: list[dict[str, Any]] = []

    for index, subject_id in enumerate(subject_ids):
        site_id = str(assigned_sites[index])
        age = int(rng.integers(30, 81))
        birth_date = date(2025, 1, 1) - timedelta(days=age * 365 + int(rng.integers(0, 365)))
        consent_date = STUDY_START + timedelta(days=int(rng.integers(0, 70)))
        sex = str(rng.choice(["Female", "Male"]))
        name = fake.name()
        initials = "".join(part[0] for part in name.split()[:2]).upper()
        dm_rows.append(
            {
                "subject_id": subject_id,
                "site_id": site_id,
                "initials": initials,
                "sex": sex,
                "birth_date": _iso(birth_date),
                "consent_date": _iso(consent_date),
            }
        )

        first_visit = consent_date + timedelta(days=int(rng.integers(0, 8)))
        visit_days = [0, 7, 21, 35, 63]
        base_sbp = int(rng.integers(138, 181))
        base_dbp = int(rng.integers(82, 111))
        base_weight = round(float(rng.normal(82, 13)), 1)
        for visit_index, visit in enumerate(VISITS):
            visit_date = first_visit + timedelta(days=visit_days[visit_index])
            reduction = visit_index * int(rng.integers(0, 4))
            systolic = max(105, base_sbp - reduction + int(rng.integers(-5, 6)))
            diastolic = max(62, base_dbp - reduction // 2 + int(rng.integers(-4, 5)))
            vs_rows.append(
                {
                    "subject_id": subject_id,
                    "site_id": site_id,
                    "visit": visit,
                    "visit_date": _iso(visit_date),
                    "systolic_bp": systolic,
                    "diastolic_bp": diastolic,
                    "pulse": int(rng.integers(54, 101)),
                    "weight": round(base_weight + float(rng.normal(0, 1.4)), 1),
                    "weight_unit": "kg",
                }
            )

        if rng.random() < 0.62:
            for event_number in range(1, int(rng.integers(2, 4))):
                start_date = consent_date + timedelta(days=int(rng.integers(1, 70)))
                ongoing = bool(rng.random() < 0.18)
                end_date = "" if ongoing else _iso(
                    start_date + timedelta(days=int(rng.integers(1, 18)))
                )
                ae_rows.append(
                    {
                        "ae_id": f"{subject_id}-AE{event_number:02d}",
                        "subject_id": subject_id,
                        "site_id": site_id,
                        "visit": str(rng.choice(VISITS)),
                        "ae_term": str(
                            rng.choice(
                                [
                                    "Headache",
                                    "Dizziness",
                                    "Peripheral edema",
                                    "Nausea",
                                    "Fatigue",
                                    "Cough",
                                ]
                            )
                        ),
                        "start_date": _iso(start_date),
                        "end_date": end_date,
                        "ongoing": "Yes" if ongoing else "No",
                        "severity": str(rng.choice(["Mild", "Moderate", "Severe"])),
                        "serious": "No",
                        "relationship": str(rng.choice(["Unrelated", "Possible", "Probable"])),
                        "outcome": "Not recovered" if ongoing else "Recovered",
                    }
                )

        if rng.random() < 0.76:
            for medication_number in range(1, int(rng.integers(2, 4))):
                start_date = consent_date - timedelta(days=int(rng.integers(1, 500)))
                ongoing = bool(rng.random() < 0.65)
                end_date = "" if ongoing else _iso(
                    max(start_date, consent_date - timedelta(days=int(rng.integers(0, 20))))
                )
                cm_rows.append(
                    {
                        "cm_id": f"{subject_id}-CM{medication_number:02d}",
                        "subject_id": subject_id,
                        "site_id": site_id,
                        "visit": "Screening",
                        "medication": str(
                            rng.choice(
                                [
                                    "lisinopril",
                                    "amlodipine",
                                    "hydrochlorothiazide",
                                    "metformin",
                                    "atorvastatin",
                                    "acetaminophen",
                                ]
                            )
                        ),
                        "dose": round(float(rng.choice([2.5, 5, 10, 12.5, 25, 50, 500])), 1),
                        "dose_unit": str(rng.choice(["mg", "mcg", "g", "mL", "IU"])),
                        "indication": str(rng.choice(["Hypertension", "Diabetes", "Pain", "Other"])),
                        "start_date": _iso(start_date),
                        "end_date": end_date,
                        "ongoing": "Yes" if ongoing else "No",
                    }
                )

    return {
        "DM": pd.DataFrame(dm_rows),
        "VS": pd.DataFrame(vs_rows),
        "AE": pd.DataFrame(ae_rows),
        "CM": pd.DataFrame(cm_rows),
    }


def _sample_positions(rng: np.random.Generator, frame: pd.DataFrame, count: int) -> list[int]:
    count = min(count, len(frame))
    if count <= 0:
        return []
    return [int(position) for position in rng.choice(len(frame), size=count, replace=False)]


def _inject_errors(forms: dict[str, pd.DataFrame], seed: int) -> dict[str, pd.DataFrame]:
    """Inject roughly 8% affected raw rows, with each requested error type represented."""
    rng = np.random.default_rng(seed + 1)
    result = {name: frame.copy(deep=True) for name, frame in forms.items()}
    raw_row_count = sum(len(frame) for frame in result.values())
    target = max(6, round(raw_row_count * 0.08))

    dm_count = max(1, round(target * 0.20))
    vs_count = max(3, round(target * 0.40))
    ae_count = max(1, round(target * 0.20))
    cm_count = max(1, target - dm_count - vs_count - ae_count)
    # Rebalance if rounding made the allocations exceed the target.
    while dm_count + vs_count + ae_count + cm_count > target:
        if cm_count > 1:
            cm_count -= 1
        elif ae_count > 1:
            ae_count -= 1
        elif dm_count > 1:
            dm_count -= 1
        else:
            vs_count -= 1

    dm_positions = _sample_positions(rng, result["DM"], dm_count)
    missing_fields = ["consent_date", "initials", "site_id", "sex", "birth_date"]
    for offset, position in enumerate(dm_positions):
        result["DM"].at[position, missing_fields[offset % len(missing_fields)]] = ""

    vs_positions = _sample_positions(rng, result["VS"], vs_count)
    vs_groups = np.array_split(np.array(vs_positions, dtype=int), 3)
    for position in vs_groups[0]:
        result["VS"].at[int(position), "systolic_bp"] = int(rng.integers(260, 301))
    for position in vs_groups[1]:
        subject_id = result["VS"].at[int(position), "subject_id"]
        consent = pd.to_datetime(
            result["DM"].loc[result["DM"]["subject_id"] == subject_id, "consent_date"].iloc[0],
            errors="coerce",
        )
        if pd.isna(consent):
            consent = pd.Timestamp(STUDY_START)
        result["VS"].at[int(position), "visit_date"] = _iso(
            (consent - pd.Timedelta(days=int(rng.integers(1, 15)))).date()
        )
    for position in vs_groups[2]:
        # The value remains kilograms while the unit says pounds.
        result["VS"].at[int(position), "weight_unit"] = "lb"

    ae_positions = _sample_positions(rng, result["AE"], ae_count)
    for position in ae_positions:
        start_date = pd.to_datetime(result["AE"].at[position, "start_date"]).date()
        result["AE"].at[position, "ongoing"] = "No"
        result["AE"].at[position, "end_date"] = _iso(
            start_date - timedelta(days=int(rng.integers(1, 8)))
        )

    cm_positions = _sample_positions(rng, result["CM"], cm_count)
    for offset, position in enumerate(cm_positions):
        if offset % 2 == 0:
            result["CM"].at[position, "medication"] = ""
        else:
            result["CM"].at[position, "dose_unit"] = "stone"

    # Append one intentional duplicate DM row while retaining 120 distinct IDs.
    duplicate_source = int(rng.integers(0, len(result["DM"])))
    result["DM"] = pd.concat(
        [result["DM"], result["DM"].iloc[[duplicate_source]].copy()],
        ignore_index=True,
    )
    return result


def generate_study_data(
    seed: int = SEED,
    include_errors: bool = True,
    output_dir: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Return the 120-subject dataset and optionally write form CSVs."""
    forms = _make_clean_forms(seed)
    if include_errors:
        forms = _inject_errors(forms, seed)
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for form_name, frame in forms.items():
            frame.to_csv(output_dir / f"{form_name.lower()}.csv", index=False)
    return forms


def ensure_raw_files() -> None:
    """Create reproducible raw CSVs if any of the expected form files are missing."""
    if not all(path.exists() for path in FORM_FILES.values()):
        generate_study_data(output_dir=next(iter(FORM_FILES.values())).parent)