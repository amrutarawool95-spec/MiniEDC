# Data Management Plan — MHP-201

**Document type:** Portfolio training document  
**Study:** Fictional Phase II hypertension study  
**Version:** 1.0  
**Effective date:** 01 October 2026

## 1. Purpose and scope

This plan describes how MiniEDC generates, validates, queries, and reports synthetic
clinical data for a fictional study with 120 subjects, six sites, and five scheduled
visits. The simulated forms are Demographics (DM), Vital Signs (VS), Adverse Events
(AE), and Concomitant Medications (CM). Visit dates are captured on the VS form.

MiniEDC is a portfolio demonstration, not an electronic data capture system for a
real clinical investigation. It has no validated production controls, identifiable
participant data, or clinical decision-making purpose.

## 2. Data flow and file inventory

1. `scripts/generate_data.py` creates reproducible sample records using Faker and
   NumPy. A fixed seed makes the generated study repeatable.
2. The generator writes one CSV per form under `data/raw/`.
3. `src/miniedc/validation.py` applies the documented edit checks to the form data.
4. Failed checks are converted to query records and persisted in
   `data/output/queries.csv`.
5. The Streamlit app reads and updates the raw CSVs and query log. The specification
   is exported to `docs/data-validation-spec.csv` and
   `docs/data-validation-spec.md`.

All values are fictional. The generator intentionally introduces approximately 8%
affected raw records, including out-of-range blood pressure, missing mandatory data,
pre-consent visit dates, invalid AE date sequences, duplicate DM records, and
inconsistent weight units.

## 3. Roles and responsibilities (simulation)

| Role | Simulated responsibility |
| --- | --- |
| Site user | Enters source-derived values and responds to data queries. |
| Clinical data manager | Reviews edit-check output, issues/updates queries, and monitors metrics. |
| Study data lead | Approves the validation specification and the final database-cleaning approach. |
| Developer | Maintains reproducible generation, validation, CSV handling, and app behavior. |

These are workflow examples only. The app does not implement role-based access,
review sign-off, or separation of duties.

## 4. Data conventions

- Subject IDs use `MHP` followed by a three-digit number.
- Sites are `S01` through `S06`.
- Scheduled visits are Screening, Baseline, Week 2, Week 4, and Week 8.
- Dates use ISO 8601 date strings (`YYYY-MM-DD`).
- Blood pressure is recorded in mmHg, pulse in beats per minute, and weight in kg.
- AE and CM ongoing fields use `Yes` or `No`; a blank end date is appropriate only
  when the record is ongoing.
- Blank values are not silently imputed by validation. A failed mandatory check is
  surfaced for review.

## 5. Query management

Each failed check generates a query with a stable Query ID, check ID, form,
subject, site, visit, field, message, status, opening date, and source-row key.
New queries start as **Open**. Users may move a query to **Answered** or **Closed**
in the Query Log tab. Query status and opening date are preserved when checks are
rerun. Historical query rows remain in the CSV after the underlying record is
corrected; a reviewer must explicitly close them.

This simulation does not implement a full audit trail, investigator response text,
query aging/escalation, or controlled database lock.

## 6. Data review and outputs

The data manager should:

1. Review the Data Validation Specification before running checks.
2. Review and resolve critical/major findings before minor findings.
3. Confirm that source data, units, visit dates, and cross-form consistency are
   appropriate before closing a query.
4. Review completion and error-rate metrics as descriptive monitoring measures,
   not as protocol-defined acceptance limits.
5. Retain a copy of the raw input and query log before any manual CSV change.

## 7. Privacy, security, and retention

No real personal or health information should be entered. This demo does not provide
encryption-at-rest controls, user authentication, access logging, backup/restore,
retention scheduling, or a validated audit trail. CSV files are local demonstration
artifacts. A hosted Streamlit deployment may use ephemeral local storage; changes
should not be treated as durable records after a redeploy or restart.

## 8. Limitations and change control

The data, study, sites, subjects, and events are synthetic. Edit checks are
illustrative and require protocol-specific review before any real use. Changes to
fields or check rules should be reflected in the data dictionary, Data Validation
Specification, tests, and this plan. There is no formal computerized-system
validation or regulatory compliance claim.