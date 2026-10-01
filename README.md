# MiniEDC

MiniEDC is a portfolio project that simulates clinical data cleaning for a fictional
Phase II hypertension study. It creates synthetic DM, VS, AE, CM, and visit-date
records for 120 subjects across six sites and five scheduled visits; applies more
than 25 edit checks; generates a CSV query log; and provides a Streamlit interface
for CRF entry, query review, and data-cleaning metrics.

> **Synthetic data only.** This project is not a clinical EDC system and must not be
> used for patient care, real trial decisions, or storage of identifiable data.

## Features

- Reproducible synthetic forms generated with Faker and NumPy.
- Approximately 8% affected raw records, including out-of-range BP, missing fields,
  pre-consent visits, invalid AE date sequences, duplicate subjects, and inconsistent
  weight units.
- 50 edit checks covering requiredness, ranges, cross-form checks, allowed values,
  uniqueness, visit sequence, and date logic.
- Automated query generation with ID, check, form, subject, site, visit, field,
  message, status, opened date, and source-row key.
- Three Streamlit tabs: CRF Data Entry with live edit-check feedback, Query Log,
  and Data Cleaning Metrics.
- Supporting documents and a machine-readable Data Validation Specification.

## Screenshots

Capture screenshots from the running app and add them under `screenshots/` before
publishing the repository. Suggested files:

| Screen | Suggested file |
| --- | --- |
| CRF Data Entry with a live edit-check message | `screenshots/crf-data-entry.png` |
| Query Log with status choices | `screenshots/query-log.png` |
| Data Cleaning Metrics | `screenshots/data-cleaning-metrics.png` |

## Repository structure

```text
miniedc/
├── app.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── src/
│   └── miniedc/
│       ├── __init__.py
│       ├── data_generator.py
│       ├── metrics.py
│       ├── queries.py
│       ├── settings.py
│       └── validation.py
├── scripts/
│   ├── export_validation_spec.py
│   └── generate_data.py
├── data/
│   ├── raw/
│   │   ├── ae.csv
│   │   ├── cm.csv
│   │   ├── dm.csv
│   │   └── vs.csv
│   └── output/
│       └── queries.csv
├── docs/
│   ├── crf-completion-guidelines.md
│   ├── data-management-plan.md
│   ├── data-validation-plan.md
│   ├── data-validation-spec.csv
│   ├── data-validation-spec.md
│   └── uat-test-cases.md
└── tests/
    └── test_miniedc.py
```

The raw CSV files and query log are generated locally if absent; they may also be
checked into GitHub for a self-contained demo. They contain only fabricated records.

## Run locally

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_data.py
python scripts/export_validation_spec.py
streamlit run app.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.
The data-generation command also creates/updates `data/output/queries.csv` from the
failed validation checks. The app creates missing raw form files automatically.

## Tests

```bash
python -m pytest
```

The automated tests cover the study dimensions, rule catalogue, key injected
anomalies, query persistence, and metrics.

## Publish to GitHub

1. Create a new GitHub repository.
2. From the project root, initialize Git if needed, commit the project files, and
   push the `main` branch:

   ```bash
   git init
   git add .
   git commit -m "Build MiniEDC synthetic data cleaning demo"
   git branch -M main
   git remote add origin https://github.com/YOUR-USER/miniedc.git
   git push -u origin main
   ```

3. Replace `YOUR-USER` with your GitHub account name and use your repository URL.

## Deploy with Streamlit Community Cloud

1. Push the code to GitHub as described above.
2. In Streamlit Community Cloud, create an app and select the repository, branch
   (`main`), and main file path (`app.py`).
3. Deploy. `requirements.txt` contains the Python dependencies.
4. The CSV query log is stored in the app's local `data/output/` directory. Treat
   this as temporary demo storage; use a durable external data store for any
   persistent multi-user deployment.

## Limitations

- **All data are synthetic.** Subjects, sites, dates, measurements, events, and
  medications are fabricated for a software portfolio exercise.
- This is not a validated EDC, clinical database, medical device, or source of
  medical advice.
- No authentication, role-based access, audit trail, electronic signatures,
  eCRF version control, coding dictionaries, medical review, database lock,
  backup/restore, or validated disaster recovery is implemented.
- Streamlit Community Cloud local files may be ephemeral. Query statuses may not
  survive restart/redeployment; use a durable database for persistence.
- The example edit checks and their severity/text are illustrative. They need
  protocol, medical, and quality review before any clinical use.
- The app's CRF entry flow appends records to CSVs. It does not provide a complete
  source-data correction workflow or a production-grade audit trail.