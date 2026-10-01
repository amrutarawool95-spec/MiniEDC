from datetime import date

import pandas as pd
import pytest

from miniedc.data_generator import generate_study_data
from miniedc.metrics import completion_metrics, error_rates_by_form
from miniedc.queries import build_query_log, load_query_log, save_query_log
from miniedc.settings import SITE_IDS, VISITS
from miniedc.validation import CHECK_SPECS, run_validation, specification_frame


@pytest.fixture
def clean_forms():
    return generate_study_data(seed=42, include_errors=False)


def test_clean_dataset_has_120_unique_subjects_and_600_vs_rows(clean_forms):
    assert clean_forms["DM"]["subject_id"].nunique() == 120
    assert len(clean_forms["DM"]) == 120
    assert len(clean_forms["VS"]) == 120 * 5


def test_clean_dataset_covers_six_sites_and_five_visits(clean_forms):
    assert set(clean_forms["DM"]["site_id"]) == set(SITE_IDS)
    assert set(clean_forms["VS"]["visit"]) == set(VISITS)
    assert clean_forms["VS"].groupby("subject_id")["visit"].nunique().eq(5).all()


def test_specification_has_required_columns_and_more_than_25_checks():
    table = specification_frame()
    assert len(CHECK_SPECS) >= 25
    assert list(table.columns) == [
        "Check ID",
        "Form",
        "Field",
        "Rule",
        "Severity",
        "Query Text",
    ]
    assert table["Check ID"].is_unique


def test_out_of_range_systolic_bp_is_flagged(clean_forms):
    clean_forms["VS"].loc[0, "systolic_bp"] = 270
    check_ids = {issue["check_id"] for issue in run_validation(clean_forms)}
    assert "VS006" in check_ids


def test_missing_consent_date_is_flagged(clean_forms):
    clean_forms["DM"].loc[0, "consent_date"] = ""
    check_ids = {issue["check_id"] for issue in run_validation(clean_forms)}
    assert "DM004" in check_ids


def test_visit_before_consent_is_flagged(clean_forms):
    subject_id = clean_forms["VS"].loc[0, "subject_id"]
    consent = pd.Timestamp(
        clean_forms["DM"].loc[clean_forms["DM"]["subject_id"] == subject_id, "consent_date"].iloc[0]
    )
    clean_forms["VS"].loc[0, "visit_date"] = (consent - pd.Timedelta(days=1)).date().isoformat()
    check_ids = {
        issue["check_id"]
        for issue in run_validation(clean_forms)
        if issue["subject"] == subject_id and issue["form"] == "VS"
    }
    assert "VS004" in check_ids


def test_ae_end_before_start_is_flagged(clean_forms):
    row = clean_forms["AE"].iloc[0]
    start = pd.Timestamp(row["start_date"])
    clean_forms["AE"].loc[0, "end_date"] = (start - pd.Timedelta(days=1)).date().isoformat()
    check_ids = {issue["check_id"] for issue in run_validation(clean_forms)}
    assert "AE003" in check_ids


def test_duplicate_demographics_subject_is_flagged(clean_forms):
    clean_forms["DM"] = pd.concat(
        [clean_forms["DM"], clean_forms["DM"].iloc[[0]]],
        ignore_index=True,
    )
    issues = run_validation(clean_forms)
    assert any(issue["check_id"] == "DM002" and issue["row_index"] == 120 for issue in issues)


def test_weight_unit_inconsistency_is_flagged(clean_forms):
    clean_forms["VS"].loc[0, "weight_unit"] = "lb"
    check_ids = {issue["check_id"] for issue in run_validation(clean_forms)}
    assert "VS012" in check_ids


def test_query_csv_status_and_metrics_round_trip(clean_forms, tmp_path):
    clean_forms["VS"].loc[0, "systolic_bp"] = 270
    issues = run_validation(clean_forms)
    bp_issue = next(issue for issue in issues if issue["check_id"] == "VS006")
    query_log = build_query_log([bp_issue], opened_on=date(2026, 10, 1))
    query_id = query_log.iloc[0]["query_id"]
    assert query_log.iloc[0]["status"] == "Open"

    query_log.loc[0, "status"] = "Answered"
    path = tmp_path / "queries.csv"
    save_query_log(query_log, path)
    reloaded = load_query_log(path)
    assert reloaded.iloc[0]["query_id"] == query_id
    assert reloaded.iloc[0]["opened_date"] == "2026-10-01"
    assert reloaded.iloc[0]["status"] == "Answered"
    assert 0 <= completion_metrics(clean_forms)["completion_percent"] <= 100
    rates = error_rates_by_form(clean_forms, issues)
    assert (rates["Error rate (%)"] >= 0).all()