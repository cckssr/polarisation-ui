#!/bin/bash
# Regenerate the ui_<form>.py modules from the Qt Designer .ui files.
#
#   polarisation_ui/pyqt/pyuic.sh                    # every form
#   polarisation_ui/pyqt/pyuic.sh malus_tab brewster_tab   # only these forms (stems without .ui)
#
# First copies the German strings from config.json into the .ui files (see sync_texts.py), then
# runs pyside6-uic and formats the generated modules with ruff. Exits non-zero on any failure.
set -euo pipefail
cd "$(dirname "$0")/../.."

PYQT_DIR=polarisation_ui/pyqt

.venv/bin/python -m polarisation_ui.pyqt.sync_texts

if [ "$#" -gt 0 ]; then
    stems=("$@")
else
    stems=()
    for f in "$PYQT_DIR"/*.ui; do
        stems+=("$(basename "${f%.ui}")")
    done
fi

outputs=()
for stem in "${stems[@]}"; do
    src="$PYQT_DIR/$stem.ui"
    out="$PYQT_DIR/ui_$stem.py"
    if [ ! -f "$src" ]; then
        echo "Error: $src does not exist" >&2
        exit 1
    fi
    .venv/bin/pyside6-uic "$src" -o "$out"
    outputs+=("$out")
    echo "generated $out"
done

.venv/bin/ruff format "${outputs[@]}"
echo "UI files converted successfully"
