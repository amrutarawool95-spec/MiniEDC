from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from miniedc.data_generator import generate_study_data
from miniedc.queries import build_query_log, load_query_log, save_query_log
from miniedc.settings import QUERY_LOG_PATH, RAW_DATA_DIR
from miniedc.validation import run_validation


if __name__ == "__main__":
    forms = generate_study_data(output_dir=RAW_DATA_DIR)
    query_log = build_query_log(
        run_validation(forms),
        load_query_log(QUERY_LOG_PATH),
    )
    save_query_log(query_log, QUERY_LOG_PATH)
    print(
        "Created synthetic forms: "
        + ", ".join(f"{name}={len(frame)} rows" for name, frame in forms.items())
    )
    print(f"Created/updated {len(query_log)} rows in {QUERY_LOG_PATH.relative_to(ROOT)}")