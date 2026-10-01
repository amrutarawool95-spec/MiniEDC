# CRF Completion Guidelines — MHP-201

**Training document for synthetic records only**

## General entry conventions

- Use only generated fictional subject IDs. Never enter names, initials, or other
  details from a real person.
- Enter dates as calendar dates in ISO format (`YYYY-MM-DD`) in CSV files.
- Record the value from the simulated source as written; do not guess or silently
  convert a value. Resolve discrepancies through a documented query.
- Leave a field blank only when it is genuinely unknown or not applicable. The
  validation rules will flag blank required fields for review.
- Record units explicitly. The application expects blood pressure in mmHg, pulse in
  beats/min, weight in kg, and CM dose in mg, mcg, g, mL, or IU.
- Use the available scheduled visit names exactly: Screening, Baseline, Week 2,
  Week 4, and Week 8.

## DM — Demographics

| Field | Completion instruction |
| --- | --- |
| `subject_id` | Unique synthetic ID, for example `MHP001`. |
| `site_id` | Select the enrolling site, `S01`–`S06`. |
| `initials` | Fictional initials only; do not use real participant initials. |
| `sex` | Female, Male, Other, or Unknown. |
| `birth_date` | Valid date; the generated eligibility range is 18–85 years at consent. |
| `consent_date` | Date consent was obtained; it must be after birth date. |

## VS — Vital Signs and visit dates

Enter one record for each scheduled visit. Use the correct visit date and subject's
assigned site. Record systolic and diastolic BP in mmHg, pulse in beats/min, and
weight in kilograms. Systolic BP should exceed diastolic BP. The training edit
checks flag values outside SBP 70–250, DBP 40–150, pulse 30–220, or weight 30–250.
These ranges are illustrative and are not medical advice or protocol limits.

## AE — Adverse Events

Create one record per event. Record a concise event term, valid start date, severity
(Mild/Moderate/Severe), seriousness (Yes/No), relationship, outcome, and ongoing
status. An event that is not ongoing needs a valid end date on or after the start
date. An event start date must be on or after consent in this simulation.

## CM — Concomitant Medications

Create one record per medication. Enter the medication name, positive dose, allowed
dose unit, indication, valid start date, and ongoing status. Historical medications
may start before consent. If the medication is not ongoing, enter an end date on or
after the start date.

## Responding to a query

Review the query message and the synthetic CRF row. Correct the source row only when
the simulated source supports the change. Update the query status to Answered when a
response is ready for review, then Closed when the issue is resolved. Do not treat
changing the status alone as proof that the underlying data are correct.