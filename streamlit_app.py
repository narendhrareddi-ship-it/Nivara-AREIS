"""
NIVARA AREIS — Streamlit Community Cloud entrypoint.

Deploy settings (if the UI dropdowns are empty, paste this GitHub URL):
https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py

Or enter manually:
  Repository: narendhrareddi-ship-it/Nivara-AREIS
  Branch: main
  Main file: streamlit_app.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_DASHBOARD = _ROOT / "dashboard"

if str(_DASHBOARD) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD))

runpy.run_path(str(_DASHBOARD / "app.py"), run_name="__main__")
