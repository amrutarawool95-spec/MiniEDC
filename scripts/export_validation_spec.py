from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from miniedc.settings import SPEC_CSV_PATH, SPEC_MD_PATH
from miniedc.validation import write_specification


if __name__ == "__main__":
    SPEC_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_specification(str(SPEC_CSV_PATH), str(SPEC_MD_PATH))
    print(f"Wrote {SPEC_CSV_PATH.relative_to(ROOT)} and {SPEC_MD_PATH.relative_to(ROOT)}")