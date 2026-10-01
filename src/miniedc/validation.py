"""Rule catalogue and row-level clinical data edit checks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from miniedc.settings import SITE_IDS, VISIT_ORDER

YES_NO = {"yes", "no"}
SEX_VALUES = {"female", "male", "other", "unknown"}
SEVERITY_VALUES = {"mild", "moderate", "severe"}
RELATIONSHIP_VALUES = {"unrelated", "unlikely", "possible", "probable", "related"}
OUTCOME_VALUES = {
    "recovered",
    "recovered with sequelae",
    "not recovered",
    "recovering",
    "fatal",
    "unknown",
}
DOSE_UNITS = {"mg", "mcg", "g", "ml", "iu"}


def _spec(
    check_id: str,
    form: str,
    field: str,
    rule: str,
    severity: str,
    query_text: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "form": form,
        "field": field,
        "rule": rule,
        "severity": severity,
        "query_text": query_text,
    }


CHECK_SPECS = [
    _spec("DM001", "DM", "subject_id", "Subject ID is required.", "Critical", "Please confirm the missing subject identifier."),
    _spec("DM002", "DM", "subject_id", "Subject ID must be unique in the Demographics form.", "Major", "Please resolve the duplicate Demographics record for this subject."),
    _spec("DM003", "DM", "site_id", f"Site is required and must be one of {', '.join(SITE_IDS)}.", "Major", "Please confirm the subject's assigned site."),
    _spec("DM004", "DM", "consent_date", "Informed consent date is required.", "Critical", "Please enter the date informed consent was obtained."),
    _spec("DM005", "DM", "birth_date", "Date of birth is required.", "Major", "Please enter the subject's date of birth."),
    _spec("DM006", "DM", "consent_date", "Consent date must be later than the date of birth.", "Critical", "Please verify the consent date and date of birth."),
    _spec("DM007", "DM", "birth_date", "Age at consent must be between 18 and 85 years.", "Major", "Please verify the subject's date of birth and eligibility age."),
    _spec("DM008", "DM", "initials", "Subject initials are required.", "Minor", "Please enter the subject's initials per the CRF guidelines."),
    _spec("DM009", "DM", "sex", "Sex must be Female, Male, Other, or Unknown.", "Minor", "Please select a permitted sex value or correct the entry."),
    _spec("VS001", "VS", "subject_id", "Subject ID is required.", "Critical", "Please confirm the subject identifier for this vital-sign record."),
    _spec("VS002", "VS", "site_id", "Site is required.", "Major", "Please enter the site that collected these vital signs."),
    _spec("VS003", "VS", "visit_date", "Visit date is required and must be a valid date.", "Major", "Please enter a valid date for this visit."),
    _spec("VS004", "VS", "visit_date", "Visit date must be on or after informed consent.", "Critical", "Please verify that this visit occurred after informed consent."),
    _spec("VS005", "VS", "systolic_bp", "Systolic blood pressure is required.", "Major", "Please enter the systolic blood pressure or document why it is missing."),
    _spec("VS006", "VS", "systolic_bp", "Systolic blood pressure must be between 70 and 250 mmHg.", "Major", "Please verify the systolic blood pressure and confirm the value in mmHg."),
    _spec("VS007", "VS", "diastolic_bp", "Diastolic blood pressure is required.", "Major", "Please enter the diastolic blood pressure or document why it is missing."),
    _spec("VS008", "VS", "diastolic_bp", "Diastolic blood pressure must be between 40 and 150 mmHg.", "Major", "Please verify the diastolic blood pressure and confirm the value in mmHg."),
    _spec("VS009", "VS", "systolic_bp", "Systolic blood pressure must be greater than diastolic blood pressure.", "Major", "Please verify the systolic and diastolic blood pressure values."),
    _spec("VS010", "VS", "pulse", "Pulse must be between 30 and 220 beats per minute.", "Major", "Please verify the pulse value and confirm the unit is beats per minute."),
    _spec("VS011", "VS", "weight", "Weight must be between 30 and 250 kilograms.", "Major", "Please verify the weight value and source unit."),
    _spec("VS012", "VS", "weight_unit", "Weight must be recorded in kilograms (kg).", "Minor", "Please convert the source weight to kilograms and update the recorded unit."),
    _spec("VS013", "VS", "visit", f"Visit must be one of: {', '.join(VISIT_ORDER)}.", "Major", "Please select a scheduled visit from the permitted visit list."),
    _spec("VS014", "VS", "visit", "A subject may have only one record per scheduled visit.", "Major", "Please resolve the duplicate subject and visit record."),
    _spec("VS015", "VS", "visit_date", "Scheduled visit dates must not move backward in visit order.", "Major", "Please verify the visit date sequence for this subject."),
    _spec("VS016", "VS", "site_id", "Vital-sign site must match the subject's Demographics site.", "Major", "Please confirm the site against the subject's Demographics record."),
    _spec("VS017", "VS", "subject_id", "Subject must exist in the Demographics form.", "Critical", "Please confirm the subject identifier or add the Demographics record first."),
    _spec("AE001", "AE", "ae_term", "Adverse event term is required.", "Major", "Please enter the adverse event term using the study coding convention."),
    _spec("AE002", "AE", "start_date", "Adverse event start date is required and must be valid.", "Major", "Please enter a valid adverse event start date."),
    _spec("AE003", "AE", "end_date", "Adverse event end date must not precede its start date.", "Major", "Please verify the adverse event start and end dates."),
    _spec("AE004", "AE", "severity", "Severity must be Mild, Moderate, or Severe.", "Major", "Please select a permitted adverse event severity."),
    _spec("AE005", "AE", "serious", "Seriousness must be Yes or No.", "Major", "Please assess and record whether the event meets seriousness criteria."),
    _spec("AE006", "AE", "relationship", "Relationship must be Unrelated, Unlikely, Possible, Probable, or Related.", "Major", "Please assess and record the event's relationship to study treatment."),
    _spec("AE007", "AE", "outcome", "Outcome must be a permitted study outcome.", "Minor", "Please select a permitted adverse event outcome."),
    _spec("AE008", "AE", "ongoing", "Ongoing must be Yes or No.", "Major", "Please indicate whether the adverse event is ongoing."),
    _spec("AE009", "AE", "end_date", "End date is required when the event is not ongoing.", "Major", "Please enter an end date or update the ongoing status."),
    _spec("AE010", "AE", "start_date", "Adverse event start date must be on or after consent.", "Critical", "Please verify the event start date against the informed consent date."),
    _spec("AE011", "AE", "subject_id", "Subject must exist in the Demographics form.", "Critical", "Please confirm the subject identifier or add the Demographics record first."),
    _spec("AE012", "AE", "site_id", "Adverse event site must match the subject's Demographics site.", "Major", "Please confirm the site against the subject's Demographics record."),
    _spec("AE013", "AE", "site_id", "Site is required.", "Major", "Please enter the site that reported this adverse event."),
    _spec("CM001", "CM", "medication", "Concomitant medication name is required.", "Major", "Please enter the medication name or document that no medication was taken."),
    _spec("CM002", "CM", "start_date", "Medication start date is required and must be valid.", "Major", "Please enter a valid medication start date."),
    _spec("CM003", "CM", "end_date", "Medication end date must not precede its start date.", "Major", "Please verify the medication start and end dates."),
    _spec("CM004", "CM", "dose", "Dose must be a positive number.", "Major", "Please verify the medication dose and enter a positive numeric value."),
    _spec("CM005", "CM", "dose_unit", "Dose unit must be mg, mcg, g, mL, or IU.", "Major", "Please correct the dose unit to a permitted value."),
    _spec("CM006", "CM", "indication", "Medication indication is required.", "Minor", "Please enter the reason the medication is being taken."),
    _spec("CM007", "CM", "ongoing", "Ongoing must be Yes or No.", "Major", "Please indicate whether the medication is ongoing."),
    _spec("CM008", "CM", "end_date", "End date is required when medication is not ongoing.", "Major", "Please enter an end date or update the ongoing status."),
    _spec("CM009", "CM", "subject_id", "Subject must exist in the Demographics form.", "Critical", "Please confirm the subject identifier or add the Demographics record first."),
    _spec("CM010", "CM", "site_id", "Concomitant medication site must match the subject's Demographics site.", "Major", "Please confirm the site against the subject's Demographics record."),
    _spec("CM011", "CM", "site_id", "Site is required.", "Major", "Please enter the site that collected this medication history."),
]

SPEC_BY_ID = {spec["check_id"]: spec for spec in CHECK_SPECS}


def _missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if bool(pd.isna(value)):
            return True
    except (TypeError, ValueError):
        pass
    return isinstance(value, str) and not value.strip()


def _text(value: Any) -> str:
    return "" if _missing(value) else str(value).strip()


def _date(value: Any) -> pd.Timestamp | None:
    if _missing(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    return None if pd.isna(parsed) else pd.Timestamp(parsed)


def _number(value: Any) -> float | None:
    if _missing(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if pd.notna(number) else None


def _age_at_consent(birth_date: pd.Timestamp, consent_date: pd.Timestamp) -> int:
    return consent_date.year - birth_date.year - (
        (consent_date.month, consent_date.day) < (birth_date.month, birth_date.day)
    )


def _lookup_dm(data: dict[str, pd.DataFrame]) -> tuple[set[str], dict[str, str], dict[str, pd.Timestamp]]:
    dm = data.get("DM", pd.DataFrame())
    subjects: set[str] = set()
    sites: dict[str, str] = {}
    consents: dict[str, pd.Timestamp] = {}
    for _, row in dm.iterrows():
        subject_id = _text(row.get("subject_id"))
        if not subject_id:
            continue
        subjects.add(subject_id)
        site_id = _text(row.get("site_id"))
        if subject_id not in sites and site_id:
            sites[subject_id] = site_id
        consent = _date(row.get("consent_date"))
        if subject_id not in consents and consent is not None:
            consents[subject_id] = consent
    return subjects, sites, consents


def run_validation(data: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    """Run all edit checks and return one issue record per failed check."""
    issues: list[dict[str, Any]] = []
    subjects, dm_sites, consent_dates = _lookup_dm(data)
    dm_frame = data.get("DM", pd.DataFrame())
    dm_duplicate_flags = (
        dm_frame["subject_id"].fillna("").astype(str).duplicated(keep="first").to_dict()
        if "subject_id" in dm_frame
        else {}
    )
    vs_frame = data.get("VS", pd.DataFrame())
    vs_duplicate_flags = (
        vs_frame.duplicated(subset=["subject_id", "visit"], keep="first").to_dict()
        if {"subject_id", "visit"}.issubset(vs_frame.columns)
        else {}
    )
    vs_prior_dates: dict[Any, pd.Timestamp | None] = {}
    if {"subject_id", "visit", "visit_date"}.issubset(vs_frame.columns):
        for _, subject_rows in vs_frame.groupby("subject_id", dropna=False, sort=False):
            latest_prior: pd.Timestamp | None = None
            for visit_name in VISIT_ORDER:
                same_visit = subject_rows[subject_rows["visit"] == visit_name]
                for row_index in same_visit.index:
                    vs_prior_dates[row_index] = latest_prior
                visit_dates = [_date(value) for value in same_visit["visit_date"]]
                valid_dates = [value for value in visit_dates if value is not None]
                if valid_dates:
                    current_latest = max(valid_dates)
                    latest_prior = (
                        current_latest if latest_prior is None else max(latest_prior, current_latest)
                    )

    def add(check_id: str, index: Any, row: pd.Series, detail: str) -> None:
        spec = SPEC_BY_ID[check_id]
        subject_id = _text(row.get("subject_id"))
        site_id = _text(row.get("site_id"))
        visit = _text(row.get("visit"))
        issues.append(
            {
                "check_id": check_id,
                "form": spec["form"],
                "subject": subject_id,
                "site": site_id,
                "visit": visit,
                "field": spec["field"],
                "severity": spec["severity"],
                "message": f'{spec["query_text"]} Finding: {detail}',
                "row_index": int(index) if str(index).isdigit() else str(index),
                "record_id": f'{spec["form"]}-{index}',
            }
        )

    for check_id, spec in SPEC_BY_ID.items():
        frame = data.get(spec["form"], pd.DataFrame())
        for index, row in frame.iterrows():
            subject_id = _text(row.get("subject_id"))
            if check_id == "DM001" and _missing(row.get("subject_id")):
                add(check_id, index, row, "Subject ID is blank.")
            elif check_id == "DM002" and dm_duplicate_flags.get(index, False):
                add(check_id, index, row, f"Subject ID {subject_id or '(blank)'} already appears in Demographics.")
            elif check_id == "DM003":
                site = _text(row.get("site_id"))
                if site not in SITE_IDS:
                    add(check_id, index, row, f"Recorded site is {site or '(blank)'}.")
            elif check_id == "DM004" and _date(row.get("consent_date")) is None:
                add(check_id, index, row, "Consent date is blank or invalid.")
            elif check_id == "DM005" and _date(row.get("birth_date")) is None:
                add(check_id, index, row, "Date of birth is blank or invalid.")
            elif check_id == "DM006":
                birth, consent = _date(row.get("birth_date")), _date(row.get("consent_date"))
                if birth is not None and consent is not None and consent <= birth:
                    add(check_id, index, row, "Consent is not later than the recorded date of birth.")
            elif check_id == "DM007":
                birth, consent = _date(row.get("birth_date")), _date(row.get("consent_date"))
                if birth is not None and consent is not None:
                    age = _age_at_consent(birth, consent)
                    if not 18 <= age <= 85:
                        add(check_id, index, row, f"Calculated age at consent is {age} years.")
            elif check_id == "DM008" and _missing(row.get("initials")):
                add(check_id, index, row, "Initials are blank.")
            elif check_id == "DM009" and _text(row.get("sex")).lower() not in SEX_VALUES:
                add(check_id, index, row, f"Recorded value is {_text(row.get('sex')) or '(blank)'}.")
            elif check_id == "VS001" and _missing(row.get("subject_id")):
                add(check_id, index, row, "Subject ID is blank.")
            elif check_id == "VS002" and _missing(row.get("site_id")):
                add(check_id, index, row, "Site is blank.")
            elif check_id == "VS003" and _date(row.get("visit_date")) is None:
                add(check_id, index, row, "Visit date is blank or invalid.")
            elif check_id == "VS004":
                visit_date = _date(row.get("visit_date"))
                consent = consent_dates.get(subject_id)
                if visit_date is not None and consent is not None and visit_date < consent:
                    add(check_id, index, row, f"Visit date {visit_date.date()} precedes consent {consent.date()}.")
            elif check_id == "VS005" and _number(row.get("systolic_bp")) is None:
                add(check_id, index, row, "Systolic blood pressure is blank or non-numeric.")
            elif check_id == "VS006":
                systolic = _number(row.get("systolic_bp"))
                if systolic is not None and not 70 <= systolic <= 250:
                    add(check_id, index, row, f"Systolic blood pressure is {systolic:g} mmHg.")
            elif check_id == "VS007" and _number(row.get("diastolic_bp")) is None:
                add(check_id, index, row, "Diastolic blood pressure is blank or non-numeric.")
            elif check_id == "VS008":
                diastolic = _number(row.get("diastolic_bp"))
                if diastolic is not None and not 40 <= diastolic <= 150:
                    add(check_id, index, row, f"Diastolic blood pressure is {diastolic:g} mmHg.")
            elif check_id == "VS009":
                systolic, diastolic = _number(row.get("systolic_bp")), _number(row.get("diastolic_bp"))
                if systolic is not None and diastolic is not None and systolic <= diastolic:
                    add(check_id, index, row, f"Systolic {systolic:g} is not greater than diastolic {diastolic:g}.")
            elif check_id == "VS010":
                pulse = _number(row.get("pulse"))
                if pulse is None or not 30 <= pulse <= 220:
                    add(check_id, index, row, f"Pulse is {pulse if pulse is not None else '(blank or non-numeric)'}.")
            elif check_id == "VS011":
                weight = _number(row.get("weight"))
                if weight is None or not 30 <= weight <= 250:
                    add(check_id, index, row, f"Weight is {weight if weight is not None else '(blank or non-numeric)'} kg.")
            elif check_id == "VS012" and _text(row.get("weight_unit")).lower() != "kg":
                add(check_id, index, row, f"Recorded weight unit is {_text(row.get('weight_unit')) or '(blank)'}.")
            elif check_id == "VS013" and _text(row.get("visit")) not in VISIT_ORDER:
                add(check_id, index, row, f"Recorded visit is {_text(row.get('visit')) or '(blank)'}.")
            elif check_id == "VS014":
                if bool(vs_duplicate_flags.get(index, False)):
                    add(check_id, index, row, f"Subject {subject_id} has more than one record for {_text(row.get('visit'))}.")
            elif check_id == "VS015":
                visit = _text(row.get("visit"))
                visit_date = _date(row.get("visit_date"))
                prior = vs_prior_dates.get(index)
                if visit in VISIT_ORDER and visit_date is not None and prior is not None and visit_date < prior:
                    add(check_id, index, row, f"{visit} date {visit_date.date()} precedes an earlier scheduled visit.")
            elif check_id == "VS016":
                expected = dm_sites.get(subject_id)
                site = _text(row.get("site_id"))
                if expected and site and site != expected:
                    add(check_id, index, row, f"Vital-sign site {site} differs from Demographics site {expected}.")
            elif check_id == "VS017" and subject_id and subject_id not in subjects:
                add(check_id, index, row, f"Subject {subject_id} is not present in Demographics.")
            elif check_id == "AE001" and _missing(row.get("ae_term")):
                add(check_id, index, row, "Adverse event term is blank.")
            elif check_id == "AE002" and _date(row.get("start_date")) is None:
                add(check_id, index, row, "Adverse event start date is blank or invalid.")
            elif check_id == "AE003":
                start, end = _date(row.get("start_date")), _date(row.get("end_date"))
                if start is not None and end is not None and end < start:
                    add(check_id, index, row, f"End date {end.date()} precedes start date {start.date()}.")
            elif check_id == "AE004" and _text(row.get("severity")).lower() not in SEVERITY_VALUES:
                add(check_id, index, row, f"Recorded severity is {_text(row.get('severity')) or '(blank)'}.")
            elif check_id == "AE005" and _text(row.get("serious")).lower() not in YES_NO:
                add(check_id, index, row, "Seriousness is blank or is not Yes/No.")
            elif check_id == "AE006" and _text(row.get("relationship")).lower() not in RELATIONSHIP_VALUES:
                add(check_id, index, row, f"Recorded relationship is {_text(row.get('relationship')) or '(blank)'}.")
            elif check_id == "AE007" and _text(row.get("outcome")).lower() not in OUTCOME_VALUES:
                add(check_id, index, row, f"Recorded outcome is {_text(row.get('outcome')) or '(blank)'}.")
            elif check_id == "AE008" and _text(row.get("ongoing")).lower() not in YES_NO:
                add(check_id, index, row, "Ongoing status is blank or is not Yes/No.")
            elif check_id == "AE009":
                if _text(row.get("ongoing")).lower() == "no" and _date(row.get("end_date")) is None:
                    add(check_id, index, row, "Event is not ongoing but has no valid end date.")
            elif check_id == "AE010":
                start, consent = _date(row.get("start_date")), consent_dates.get(subject_id)
                if start is not None and consent is not None and start < consent:
                    add(check_id, index, row, f"Event start {start.date()} precedes consent {consent.date()}.")
            elif check_id == "AE011" and subject_id and subject_id not in subjects:
                add(check_id, index, row, f"Subject {subject_id} is not present in Demographics.")
            elif check_id == "AE012":
                expected, site = dm_sites.get(subject_id), _text(row.get("site_id"))
                if expected and site and site != expected:
                    add(check_id, index, row, f"AE site {site} differs from Demographics site {expected}.")
            elif check_id == "AE013" and _missing(row.get("site_id")):
                add(check_id, index, row, "Site is blank.")
            elif check_id == "CM001" and _missing(row.get("medication")):
                add(check_id, index, row, "Medication name is blank.")
            elif check_id == "CM002" and _date(row.get("start_date")) is None:
                add(check_id, index, row, "Medication start date is blank or invalid.")
            elif check_id == "CM003":
                start, end = _date(row.get("start_date")), _date(row.get("end_date"))
                if start is not None and end is not None and end < start:
                    add(check_id, index, row, f"Medication end date {end.date()} precedes start date {start.date()}.")
            elif check_id == "CM004":
                dose = _number(row.get("dose"))
                if dose is None or dose <= 0:
                    add(check_id, index, row, f"Dose is {dose if dose is not None else '(blank or non-numeric)'}.")
            elif check_id == "CM005" and _text(row.get("dose_unit")).lower() not in DOSE_UNITS:
                add(check_id, index, row, f"Recorded dose unit is {_text(row.get('dose_unit')) or '(blank)'}.")
            elif check_id == "CM006" and _missing(row.get("indication")):
                add(check_id, index, row, "Medication indication is blank.")
            elif check_id == "CM007" and _text(row.get("ongoing")).lower() not in YES_NO:
                add(check_id, index, row, "Ongoing status is blank or is not Yes/No.")
            elif check_id == "CM008":
                if _text(row.get("ongoing")).lower() == "no" and _date(row.get("end_date")) is None:
                    add(check_id, index, row, "Medication is not ongoing but has no valid end date.")
            elif check_id == "CM009" and subject_id and subject_id not in subjects:
                add(check_id, index, row, f"Subject {subject_id} is not present in Demographics.")
            elif check_id == "CM010":
                expected, site = dm_sites.get(subject_id), _text(row.get("site_id"))
                if expected and site and site != expected:
                    add(check_id, index, row, f"Medication site {site} differs from Demographics site {expected}.")
            elif check_id == "CM011" and _missing(row.get("site_id")):
                add(check_id, index, row, "Site is blank.")

    return issues


def specification_frame() -> pd.DataFrame:
    """Return the human-readable Data Validation Specification table."""
    columns = ["Check ID", "Form", "Field", "Rule", "Severity", "Query Text"]
    return pd.DataFrame(
        [
            {
                "Check ID": spec["check_id"],
                "Form": spec["form"],
                "Field": spec["field"],
                "Rule": spec["rule"],
                "Severity": spec["severity"],
                "Query Text": spec["query_text"],
            }
            for spec in CHECK_SPECS
        ],
        columns=columns,
    )


def write_specification(csv_path: str, markdown_path: str) -> None:
    table = specification_frame()
    table.to_csv(csv_path, index=False)
    headers = list(table.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in table.iterrows():
        values = [str(value).replace("|", "\\|") for value in row.tolist()]
        lines.append("| " + " | ".join(values) + " |")
    markdown = [
        "# MiniEDC Data Validation Specification",
        "",
        f"Rule catalogue: **{len(table)} edit checks** across DM, VS, AE, and CM.",
        "",
        *lines,
        "",
    ]
    with open(markdown_path, "w", encoding="utf-8") as output:
        output.write("\n".join(markdown))