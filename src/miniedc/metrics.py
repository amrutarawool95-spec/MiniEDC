"""Data-cleaning summary calculations used by the Streamlit dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd

from miniedc.settings import SITE_IDS
from miniedc.validation import CHECK_SPECS

REQUIRED_FIELDS = {
    "DM": ["subject_id", "site_id", "initials", "sex", "birth_date", "consent_date"],
    "VS": [
        "subject_id",
        "site_id",
        "visit",
        "visit_date",
        "systolic_bp",
        "diastolic_bp",
        "pulse",
        "weight",
        "weight_unit",
    ],
    "AE": [
        "subject_id",
        "site_id",
        "ae_term",
        "start_date",
        "ongoing",
        "severity",
        "serious",
        "relationship",
        "outcome",
    ],
    "CM": [
        "subject_id",
        "site_id",
        "medication",
        "dose",
        "dose_unit",
        "indication",
        "start_date",
        "ongoing",
    ],
}


def _present(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    return bool(str(value).strip())


def completion_metrics(data: dict[str, pd.DataFrame]) -> dict[str, float | int]:
    required = 0
    completed = 0
    rows = 0
    for form, fields in REQUIRED_FIELDS.items():
        frame = data.get(form, pd.DataFrame())
        rows += len(frame)
        required += len(frame) * len(fields)
        for field in fields:
            if field not in frame:
                continue
            completed += int(frame[field].map(_present).sum())
    return {
        "completion_percent": round(100 * completed / required, 1) if required else 100.0,
        "completed_required_fields": completed,
        "required_fields": required,
        "raw_records": rows,
    }


def error_rates_by_form(
    data: dict[str, pd.DataFrame], issues: list[dict[str, Any]]
) -> pd.DataFrame:
    failure_counts: dict[str, int] = {form: 0 for form in REQUIRED_FIELDS}
    for issue in issues:
        form = str(issue.get("form", ""))
        if form in failure_counts:
            failure_counts[form] += 1
    rows = []
    for form in REQUIRED_FIELDS:
        check_count = sum(spec["form"] == form for spec in CHECK_SPECS)
        opportunities = len(data.get(form, pd.DataFrame())) * check_count
        errors = failure_counts[form]
        rows.append(
            {
                "Form": form,
                "Failed checks": errors,
                "Check opportunities": opportunities,
                "Error rate (%)": round(100 * errors / opportunities, 2) if opportunities else 0.0,
            }
        )
    return pd.DataFrame(rows)


def open_queries_by_site(query_log: pd.DataFrame) -> pd.DataFrame:
    counts = {site: 0 for site in SITE_IDS}
    if not query_log.empty and {"site", "status"}.issubset(query_log.columns):
        open_rows = query_log[query_log["status"].fillna("").astype(str) == "Open"]
        for site, count in open_rows.groupby("site").size().items():
            site_name = str(site).strip() or "Unassigned"
            counts[site_name] = int(count)
    return pd.DataFrame([{"Site": site, "Open queries": count} for site, count in counts.items()])