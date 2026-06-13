"""Safe accessors for nullable Postgres / API values in the Streamlit dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def val(row: dict[str, Any] | None, key: str, default: Any = 0) -> Any:
    if not row or key not in row or row[key] is None:
        return default
    return row[key]


def text(row: dict[str, Any] | None, key: str, default: str = "", maxlen: int | None = None) -> str:
    """Never raises — safe for NULL DB columns."""
    if not row:
        s = default
    else:
        v = row.get(key)
        if v is None:
            s = default
        elif isinstance(v, str):
            s = v
        else:
            s = str(v)
    return s[:maxlen] if maxlen is not None else s


def trunc(value: Any, maxlen: int, default: str = "") -> str:
    s = default if value is None else (value if isinstance(value, str) else str(value))
    return s[:maxlen]


def fmt_dt(value: Any, fmt: str = "%d %b %H:%M", default: str = "—") -> str:
    if value is None:
        return default
    if isinstance(value, datetime):
        try:
            return value.strftime(fmt)
        except Exception:
            return default
    return default
