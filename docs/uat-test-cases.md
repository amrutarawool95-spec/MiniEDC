# UAT Test Cases — MiniEDC

The cases below were executed against the automated data/validation logic on
**01 October 2026**. “PASS” means the corresponding automated acceptance assertion
passed; this is not a claim of manual user acceptance or regulatory validation.

| ID | Test case / steps | Expected result | Result |
| --- | --- | --- | --- |
| UAT-01 | Generate a clean study dataset and count unique DM subjects and VS rows. | 120 unique subjects and 600 scheduled VS records. | PASS |
| UAT-02 | Inspect the generated clean data for site and visit coverage. | Six site codes and all five scheduled visit names are represented. | PASS |
| UAT-03 | Load the check catalogue and count executable rules. | At least 25 checks are available; each has the required specification columns. | PASS |
| UAT-04 | Set a VS systolic BP to 270 mmHg and run checks. | `VS006` is returned for the affected record. | PASS |
| UAT-05 | Clear a DM consent date and run checks. | `DM004` is returned for the affected record. | PASS |
| UAT-06 | Set a VS visit date before that subject's consent date. | `VS004` is returned for the affected record. | PASS |
| UAT-07 | Set an AE end date earlier than its start date. | `AE003` is returned for the affected record. | PASS |
| UAT-08 | Append a second DM row with an existing subject ID. | `DM002` is returned for the duplicate row. | PASS |
| UAT-09 | Set VS weight unit to lb while retaining the numeric value. | `VS012` is returned for the affected record. | PASS |
| UAT-10 | Build, save, and reload an Open query; calculate completion and error metrics. | Query ID/date/status persist; completion is 0–100%; per-form rates are non-negative. | PASS |

Run the executable cases from the repository root with `python -m pytest`.