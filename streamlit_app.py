"""
NIVARA AREIS — Streamlit Community Cloud entrypoint.

Deploy: https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_DASHBOARD = _ROOT / "dashboard"
_AGENTS_SRC = _ROOT / "agents" / "src"

for path in (_DASHBOARD, _AGENTS_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

runpy.run_path(str(_DASHBOARD / "app.py"), run_name="__main__")
