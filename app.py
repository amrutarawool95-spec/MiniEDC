"""Streamlit entry point for the synthetic MiniEDC training application."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from miniedc.data_generator import ensure_raw_files, generate_study_data
from miniedc.metrics import completion_metrics, error_rates_by_form, open_queries_by_site
from miniedc.queries import (
    QUERY_COLUMNS,
    QUERY_STATUSES,
    build_query_log,
    load_query_log,
    save_query_log,
)
from miniedc.settings import (
    FORM_FILES,
    OUTPUT_DIR,
    QUERY_LOG_PATH,
    SITE_IDS,
    SYNTHETIC_NOTICE,
    VISITS,
)
from miniedc.validation import run_validation

st.set_page_config(page_title="MiniEDC | Data Cleaning Lab", page_icon="M", layout="wide")


def load_forms() -> dict[str, pd.DataFrame]:
    ensure_raw_files()
    forms = {}
    for form, path in FORM_FILES.items():
        frame = pd.read_csv(path, dtype=str).fillna("")
        forms[form] = frame.reset_index(drop=True)
    return forms


def save_forms(forms: dict[str, pd.DataFrame]) -> None:
    for form, path in FORM_FILES.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        forms[form].to_csv(path, index=False)


def initialize_state() -> None:
    if "forms" not in st.session_state:
        st.session_state.forms = load_forms()
    if "query_log" not in st.session_state:
        current = load_query_log(QUERY_LOG_PATH)
        current = build_query_log(run_validation(st.session_state.forms), current)
        st.session_state.query_log = current
        save_query_log(current, QUERY_LOG_PATH)


def as_iso(value: date) -> str:
    return value.isoformat()


def add_entry(form_name: str, entry: dict[str, object]) -> None:
    forms = st.session_state.forms
    forms[form_name] = pd.concat(
        [forms[form_name], pd.DataFrame([entry])], ignore_index=True
    ).fillna("")
    save_forms(forms)
    refreshed = build_query_log(
        run_validation(forms),
        st.session_state.query_log,
    )
    st.session_state.query_log = refreshed
    save_query_log(refreshed, QUERY_LOG_PATH)


def subject_selector(form_name: str, key: str) -> str:
    subjects = sorted(
        {
            str(subject)
            for subject in st.session_state.forms["DM"].get("subject_id", [])
            if str(subject).strip()
        }
    )
    if form_name == "DM":
        choices = ["Enter subject ID"] + subjects
    else:
        choices = ["Select subject"] + subjects
    selected = st.selectbox("Subject", choices, key=f"{key}_subject_choice")
    if selected in ("Enter subject ID", "Select subject"):
        return st.text_input(
            "Subject ID",
            value="MHP121" if form_name == "DM" else "",
            key=f"{key}_subject_id",
            help="Use a fictional study identifier, not a person's name or real identifier.",
        ).strip()
    return selected


def site_for_subject(subject_id: str) -> str:
    dm = st.session_state.forms["DM"]
    matches = dm.loc[dm.get("subject_id", pd.Series(dtype=str)).astype(str) == subject_id]
    if not matches.empty and str(matches.iloc[0].get("site_id", "")).strip() in SITE_IDS:
        return str(matches.iloc[0]["site_id"])
    return SITE_IDS[0]


def entry_form() -> None:
    st.subheader("Enter a CRF record")
    st.caption(
        "Choose a form and complete the fields. The draft is checked as you edit it; "
        "save appends a synthetic record to that form's CSV."
    )
    form_name = st.selectbox("CRF form", ["DM", "VS", "AE", "CM"], key="entry_form")
    prefix = f"entry_{form_name.lower()}"
    entry: dict[str, object] = {}

    if form_name == "DM":
        subject_id = subject_selector(form_name, prefix)
        site_id = st.selectbox("Site", SITE_IDS, key=f"{prefix}_site")
        col1, col2 = st.columns(2)
        with col1:
            initials = st.text_input("Initials", key=f"{prefix}_initials").strip()
            sex = st.selectbox(
                "Sex", ["Female", "Male", "Other", "Unknown"], key=f"{prefix}_sex"
            )
        with col2:
            birth_date = st.date_input(
                "Date of birth",
                value=date(1970, 1, 1),
                key=f"{prefix}_birth_date",
            )
            consent_date = st.date_input(
                "Informed consent date",
                value=date(2025, 1, 6),
                key=f"{prefix}_consent_date",
            )
        entry = {
            "subject_id": subject_id,
            "site_id": site_id,
            "initials": initials,
            "sex": sex,
            "birth_date": as_iso(birth_date),
            "consent_date": as_iso(consent_date),
        }
    elif form_name == "VS":
        subject_id = subject_selector(form_name, prefix)
        site_id = st.selectbox(
            "Site", SITE_IDS, index=SITE_IDS.index(site_for_subject(subject_id)), key=f"{prefix}_site"
        )
        visit = st.selectbox("Visit", VISITS, key=f"{prefix}_visit")
        visit_date = st.date_input(
            "Visit date", value=date(2025, 1, 20), key=f"{prefix}_visit_date"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            systolic = st.number_input(
                "Systolic BP (mmHg)", min_value=0, max_value=400, value=140, key=f"{prefix}_sbp"
            )
            diastolic = st.number_input(
                "Diastolic BP (mmHg)", min_value=0, max_value=250, value=90, key=f"{prefix}_dbp"
            )
        with col2:
            pulse = st.number_input(
                "Pulse (beats/min)", min_value=0, max_value=300, value=72, key=f"{prefix}_pulse"
            )
            weight = st.number_input(
                "Weight", min_value=0.0, max_value=500.0, value=78.0, step=0.1, key=f"{prefix}_weight"
            )
        with col3:
            weight_unit = st.selectbox(
                "Weight unit", ["kg", "lb"], key=f"{prefix}_weight_unit"
            )
        entry = {
            "subject_id": subject_id,
            "site_id": site_id,
            "visit": visit,
            "visit_date": as_iso(visit_date),
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "pulse": pulse,
            "weight": weight,
            "weight_unit": weight_unit,
        }
    elif form_name == "AE":
        subject_id = subject_selector(form_name, prefix)
        site_id = st.selectbox(
            "Site", SITE_IDS, index=SITE_IDS.index(site_for_subject(subject_id)), key=f"{prefix}_site"
        )
        col1, col2 = st.columns(2)
        with col1:
            visit = st.selectbox("Visit", VISITS, key=f"{prefix}_visit")
            ae_term = st.text_input("Adverse event term", key=f"{prefix}_term").strip()
            start_date = st.date_input(
                "Event start date", value=date(2025, 2, 1), key=f"{prefix}_start"
            )
            ongoing = st.selectbox("Event ongoing?", ["No", "Yes"], key=f"{prefix}_ongoing")
            end_date_value = st.date_input(
                "Event end date",
                value=date(2025, 2, 2),
                disabled=ongoing == "Yes",
                key=f"{prefix}_end",
            )
        with col2:
            severity = st.selectbox(
                "Severity", ["Mild", "Moderate", "Severe"], key=f"{prefix}_severity"
            )
            serious = st.selectbox("Serious?", ["No", "Yes"], key=f"{prefix}_serious")
            relationship = st.selectbox(
                "Relationship", ["Unrelated", "Unlikely", "Possible", "Probable", "Related"],
                key=f"{prefix}_relationship",
            )
            outcome = st.selectbox(
                "Outcome",
                ["Recovered", "Recovered with sequelae", "Not recovered", "Recovering", "Fatal", "Unknown"],
                key=f"{prefix}_outcome",
            )
        ae_id = st.text_input("Adverse event ID", value="New event", key=f"{prefix}_ae_id").strip()
        entry = {
            "ae_id": ae_id or "New event",
            "subject_id": subject_id,
            "site_id": site_id,
            "visit": visit,
            "ae_term": ae_term,
            "start_date": as_iso(start_date),
            "end_date": "" if ongoing == "Yes" else as_iso(end_date_value),
            "ongoing": ongoing,
            "severity": severity,
            "serious": serious,
            "relationship": relationship,
            "outcome": outcome,
        }
    else:
        subject_id = subject_selector(form_name, prefix)
        site_id = st.selectbox(
            "Site", SITE_IDS, index=SITE_IDS.index(site_for_subject(subject_id)), key=f"{prefix}_site"
        )
        col1, col2 = st.columns(2)
        with col1:
            visit = st.selectbox("Visit", VISITS, key=f"{prefix}_visit")
            medication = st.text_input("Medication", key=f"{prefix}_medication").strip()
            dose = st.number_input(
                "Dose", min_value=0.0, max_value=10000.0, value=5.0, step=0.5, key=f"{prefix}_dose"
            )
            dose_unit = st.selectbox(
                "Dose unit", ["mg", "mcg", "g", "mL", "IU"], key=f"{prefix}_dose_unit"
            )
            indication = st.text_input("Indication", key=f"{prefix}_indication").strip()
        with col2:
            start_date = st.date_input(
                "Medication start date", value=date(2024, 12, 1), key=f"{prefix}_start"
            )
            ongoing = st.selectbox("Medication ongoing?", ["Yes", "No"], key=f"{prefix}_ongoing")
            end_date_value = st.date_input(
                "Medication end date",
                value=date(2025, 1, 1),
                disabled=ongoing == "Yes",
                key=f"{prefix}_end",
            )
        cm_id = st.text_input("Medication record ID", value="New medication", key=f"{prefix}_cm_id").strip()
        entry = {
            "cm_id": cm_id or "New medication",
            "subject_id": subject_id,
            "site_id": site_id,
            "visit": visit,
            "medication": medication,
            "dose": dose,
            "dose_unit": dose_unit,
            "indication": indication,
            "start_date": as_iso(start_date),
            "end_date": "" if ongoing == "Yes" else as_iso(end_date_value),
            "ongoing": ongoing,
        }

    existing = st.session_state.forms[form_name]
    draft = pd.concat([existing, pd.DataFrame([entry])], ignore_index=True).fillna("")
    preview_data = {key: frame.copy() for key, frame in st.session_state.forms.items()}
    preview_data[form_name] = draft
    preview_issues = run_validation(preview_data)
    draft_index = len(draft) - 1
    live_issues = [
        issue for issue in preview_issues
        if issue["form"] == form_name and issue["row_index"] == draft_index
    ]
    if live_issues:
        st.warning(f"{len(live_issues)} edit check(s) currently fail for this draft.")
        for issue in live_issues:
            st.error(f'{issue["check_id"]} · {issue["field"]}: {issue["message"]}')
    else:
        st.success("No edit checks currently fail for this draft.")

    if st.button("Save CRF record", type="primary", key=f"{prefix}_save"):
        add_entry(form_name, entry)
        st.success(f"{form_name} record saved to {FORM_FILES[form_name].relative_to(ROOT)}.")
        st.rerun()

    with st.expander(f"Current {form_name} records"):
        st.dataframe(st.session_state.forms[form_name], use_container_width=True, hide_index=True)


def query_log_tab() -> None:
    st.subheader("Query Log")
    query_log = st.session_state.query_log.copy()
    open_count = int((query_log["status"] == "Open").sum()) if not query_log.empty else 0
    answered_count = int((query_log["status"] == "Answered").sum()) if not query_log.empty else 0
    closed_count = int((query_log["status"] == "Closed").sum()) if not query_log.empty else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Open", open_count)
    col2.metric("Answered", answered_count)
    col3.metric("Closed", closed_count)

    if st.button("Re-run checks and add new queries"):
        current = build_query_log(run_validation(st.session_state.forms), query_log)
        st.session_state.query_log = current
        save_query_log(current, QUERY_LOG_PATH)
        st.success("Validation rerun complete. Existing query statuses were preserved.")
        st.rerun()

    if query_log.empty:
        st.info("No queries have been generated yet.")
        return

    edited = st.data_editor(
        query_log,
        use_container_width=True,
        hide_index=True,
        disabled=[column for column in QUERY_COLUMNS if column != "status"],
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status", options=QUERY_STATUSES, required=True
            ),
            "message": st.column_config.TextColumn("Query text", width="large"),
        },
        key="query_log_editor",
    )
    if st.button("Save query status changes", type="primary"):
        edited = edited[QUERY_COLUMNS].fillna("")
        st.session_state.query_log = edited
        save_query_log(edited, QUERY_LOG_PATH)
        st.success(f"Query log saved to {QUERY_LOG_PATH.relative_to(ROOT)}.")
        st.rerun()

    csv_data = st.session_state.query_log.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download queries.csv",
        data=csv_data,
        file_name="queries.csv",
        mime="text/csv",
    )
    st.caption(f"Persistent CSV: `{QUERY_LOG_PATH.relative_to(ROOT)}`")


def metrics_tab() -> None:
    st.subheader("Data Cleaning Metrics")
    forms = st.session_state.forms
    issues = run_validation(forms)
    completion = completion_metrics(forms)
    queries = st.session_state.query_log
    open_count = int((queries["status"] == "Open").sum()) if not queries.empty else 0
    total_rows = sum(len(frame) for frame in forms.values())

    col1, col2, col3 = st.columns(3)
    col1.metric("CRF completion", f'{completion["completion_percent"]:.1f}%')
    col2.metric("Open queries", f"{open_count:,}")
    col3.metric("Raw CRF records", f"{total_rows:,}")
    st.caption(
        f'{completion["completed_required_fields"]:,} of '
        f'{completion["required_fields"]:,} required field instances are populated.'
    )

    left, right = st.columns(2)
    with left:
        st.markdown("#### Open queries by site")
        st.bar_chart(open_queries_by_site(queries).set_index("Site"), y="Open queries")
    with right:
        st.markdown("#### Failed checks by form")
        rates = error_rates_by_form(forms, issues)
        st.bar_chart(rates.set_index("Form"), y="Error rate (%)")
        st.dataframe(rates, hide_index=True, use_container_width=True)
    st.caption(
        "Error rate = failed edit-check instances divided by records × applicable checks for that form. "
        "This is a training metric, not a regulatory quality threshold."
    )

    with st.expander("Validation run details"):
        st.write(f"{len(issues):,} failed check instances across {len(forms)} forms.")
        if issues:
            st.dataframe(pd.DataFrame(issues), hide_index=True, use_container_width=True)


def main() -> None:
    initialize_state()
    st.title("MiniEDC")
    st.caption("Synthetic clinical data entry, edit checks, and query management")
    st.warning(SYNTHETIC_NOTICE)

    with st.sidebar:
        st.markdown("### Study")
        st.write("MHP-201")
        st.write("Phase II · Hypertension")
        st.write("120 enrolled subjects · 6 sites · 5 visits")
        st.divider()
        if st.button("Regenerate synthetic study data"):
            fresh = generate_study_data(output_dir=FORM_FILES["DM"].parent)
            st.session_state.forms = fresh
            st.session_state.query_log = build_query_log(
                run_validation(fresh), st.session_state.query_log
            )
            save_query_log(st.session_state.query_log, QUERY_LOG_PATH)
            st.rerun()

    entry_tab, queries_tab, metrics = st.tabs(
        ["CRF Data Entry", "Query Log", "Data Cleaning Metrics"]
    )
    with entry_tab:
        entry_form()
    with queries_tab:
        query_log_tab()
    with metrics:
        metrics_tab()


if __name__ == "__main__":
    main()