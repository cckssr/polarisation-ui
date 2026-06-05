"""Lightweight session-state persistence.

Saves UI settings (group, team, suffix, calibration profile, gain stage,
acquisition settings) and tab data points to a single JSON file so they
can be restored after a crash or unexpected shutdown on the same day.

    ~/.polarisation-ui/last_session.json

The file is written on every meaningful settings change (debounced by
MainWindow).  On startup MainWindow calls load_session_state() and, if
the saved_date matches today, offers to restore.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

SESSION_STATE_PATH = Path.home() / ".polarisation-ui" / "last_session.json"


@dataclass
class SessionState:
    """All restorable UI state for one working session."""

    saved_date: str  # ISO date, e.g. "2026-06-05"
    saved_at: str  # ISO datetime, e.g. "2026-06-05T14:30:00.123456"
    group_letter: str = ""
    team_name: str = ""
    suffix: str = ""
    profile_name: str = ""  # stem of calibration profile; "" = none loaded
    gain_stage: int = 0  # active PDTIA stage (1–4); 0 = not set
    acq_settings: dict = field(default_factory=dict)
    # keys are tab_id strings; values are lists of serialised point dicts
    tab_points: dict = field(default_factory=dict)


def save_session_state(state: SessionState, path: Path = SESSION_STATE_PATH) -> None:
    """Serialise *state* to *path* (overwrites any previous file)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, indent=2, ensure_ascii=False)


def load_session_state(
    path: Path = SESSION_STATE_PATH,
) -> Optional[SessionState]:
    """Return the persisted SessionState, or None if missing / corrupt."""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SessionState(**data)
    except Exception:
        return None


def is_from_today(state: SessionState) -> bool:
    """Return True iff state.saved_date matches the current calendar day."""
    try:
        return date.fromisoformat(state.saved_date) == date.today()
    except ValueError:
        return False
