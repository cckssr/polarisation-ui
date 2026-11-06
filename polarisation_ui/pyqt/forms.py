"""Locations of the Designer forms; shared by ``sync_texts`` and ``preview`` (PySide6-free)."""

from __future__ import annotations

from pathlib import Path

PYQT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PYQT_DIR.parent / "config.json"

# .ui file stem -> sections of the ``ui`` config that the code applies to it; the default is
# the stem itself (e.g. ``"a_scan_tab": ("a_scan_actions",)``).
SECTIONS: dict[str, tuple[str, ...]] = {}


def form_names() -> list[str]:
    """Stems of every ``.ui`` file, sorted."""
    return sorted(path.stem for path in PYQT_DIR.glob("*.ui"))
