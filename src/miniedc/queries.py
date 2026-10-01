"""Create, persist, and reconcile the synthetic clinical query log."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

QUERY_COLUMNS = [
    "query_id",
    "check_id",
    "form",
    "subject",
    "site",
    "visit",
    "field",
    "message",
    "status",
    "opened_date",
    "record_id",
]
QUERY_STATUSES = ["Open", "Answered", "Closed"]


def empty_query_log() -> pd.DataFrame:
    return pd.DataFrame(columns=QUERY_COLUMNS)


def load_query_log(path: Path) -> pd.DataFrame:
    if not path.exists():
        return empty_query_log()
    try:
        frame = pd.read_csv(path, dtype=str).fillna("")
    except (OSError, pd.errors.ParserError):
        return empty_query_log()
    for column in QUERY_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    return frame[QUERY_COLUMNS]


def _signature(row: dict[str, Any] | pd.Series) -> tuple[str, ...]:
    return tuple(str(row.get(key, "") or "") for key in ("check_id", "form", "record_id", "field"))


def build_query_log(
    issues: list[dict[str, Any]],
    existing: pd.DataFrame | None = None,
    opened_on: date | None = None,
) -> pd.DataFrame:
    """Keep query history/statuses and add a new Open query for each new failure."""
    current = existing.copy() if existing is not None else empty_query_log()
    for column in QUERY_COLUMNS:
        if column not in current.columns:
            current[column] = ""
    current = current[QUERY_COLUMNS].fillna("")
    existing_by_signature: dict[tuple[str, ...], pd.Series] = {}
    for _, row in current.iterrows():
        existing_by_signature[_signature(row)] = row

    max_id = 0
    for query_id in current["query_id"].astype(str):
        if query_id.startswith("QRY-"):
            try:
                max_id = max(max_id, int(query_id.split("-")[1]))
            except (ValueError, IndexError):
                continue

    as_of = (opened_on or date.today()).isoformat()
    seen: set[tuple[str, ...]] = set()
    added: list[dict[str, str]] = []
    for issue in issues:
        record_id = str(issue.get("record_id", f'{issue.get("form", "")}-{issue.get("row_index", "")}'))
        row = {
            "check_id": str(issue.get("check_id", "")),
            "form": str(issue.get("form", "")),
            "subject": str(issue.get("subject", "")),
            "site": str(issue.get("site", "")),
            "visit": str(issue.get("visit", "")),
            "field": str(issue.get("field", "")),
            "message": str(issue.get("message", "")),
            "record_id": record_id,
        }
        signature = _signature(row)
        if signature in seen:
            continue
        seen.add(signature)
        previous = existing_by_signature.get(signature)
        if previous is not None:
            added.append({column: str(previous.get(column, "") or "") for column in QUERY_COLUMNS})
            continue
        max_id += 1
        added.append(
            {
                **row,
                "query_id": f"QRY-{max_id:05d}",
                "status": "Open",
                "opened_date": as_of,
            }
        )

    # Preserve historical queries even after data correction; users can close them.
    current_signatures = {_signature(row) for row in added}
    for _, old in current.iterrows():
        if _signature(old) not in current_signatures:
            added.append({column: str(old.get(column, "") or "") for column in QUERY_COLUMNS})
            current_signatures.add(_signature(old))
    result = pd.DataFrame(added, columns=QUERY_COLUMNS)
    if result.empty:
        return empty_query_log()
    return result.sort_values("query_id", kind="stable").reset_index(drop=True)


def save_query_log(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = frame.copy()
    for column in QUERY_COLUMNS:
        if column not in normalized.columns:
            normalized[column] = ""
    normalized[QUERY_COLUMNS].to_csv(path, index=False)