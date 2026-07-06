# docs/

Technical reference documentation for the main application:

- `scpi-reference.md` — full SCPI command reference for the Arduino firmware.
- `encoder-debugging.md` — AS5048A hardware/software debugging guide.

The remaining files are offline analysis helpers and data from ad-hoc bench
measurements, not part of the installable package:

- `analyze_magnet.py` — standalone script for magnet-strength/symmetry
  analysis from teslameter CSV logs (`magnet_strength.csv`,
  `magnet_strength_mt_analysis.png`).
- `brewster_plot.py` — standalone script plotting a captured Brewster-angle
  measurement (`Brewster-Messung-P.csv`, `Brewster-Messung-S.csv`).
- `magnet_analysis.png`, `magnet_strength.csv`, `magnet_strength_mt_analysis.png`,
  `Brewster-Messung-P.csv`, `Brewster-Messung-S.csv` — the corresponding
  measurement data/plots referenced by the two scripts above.

Run either script directly with `.venv/bin/python docs/<script>.py`; both
expect their CSV inputs in the current working directory.
