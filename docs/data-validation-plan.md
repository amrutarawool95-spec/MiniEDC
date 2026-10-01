# Data Validation Plan — MHP-201

**Version:** 1.0  
**Purpose:** Define the test-data validation approach for the MiniEDC portfolio demo.

## Scope

The validation plan covers DM, VS, AE, CM, and visit-date data, including required
fields, allowed values, numeric ranges, date relationships, uniqueness, and
cross-form consistency. The authoritative, executable catalogue is
[`data-validation-spec.md`](data-validation-spec.md), with a machine-readable copy
at [`data-validation-spec.csv`](data-validation-spec.csv).

## Execution

- Run all checks in the Streamlit app during data entry or choose **Re-run checks and
  add new queries** in the Query Log tab.
- For an independent run, use:

  ```bash
  python scripts/generate_data.py
  python scripts/export_validation_spec.py
  python -m pytest
  ```

- Check results are not used to silently alter raw data.
- Failed checks create query-log rows. Open and Answered queries remain visible;
  historical rows are retained after correction until a reviewer closes them.

## Severity

| Severity | Interpretation in this demo |
| --- | --- |
| Critical | Subject identity, consent, or a major cross-form safety/timing concern. |
| Major | Clinically important range, required form content, or consistency issue. |
| Minor | Administrative or lower-impact completion issue. |

Severity is illustrative, not a regulatory classification. A real protocol and
medical review would determine final classifications and query text.

## Data review and acceptance

The check catalogue is accepted for this code exercise when:

1. The study generator creates 120 unique synthetic subject IDs, six site codes,
   and five scheduled visits.
2. Every catalogue row has an executable check ID, form, field, rule, severity,
   and query text.
3. The injected data anomalies produce validation findings and new Open queries.
4. All 10 automated UAT scenarios pass.

This is software verification for a portfolio sample. It is not clinical-system
validation, a database lock, or proof of fitness for use in a real clinical trial.

## Change control

When adding or changing a form field or edit check, update the rule catalogue,
re-export both specification files, adjust synthetic data and tests as needed, and
rerun the automated suite. Review any change to query text or severity for clinical
meaning before use.