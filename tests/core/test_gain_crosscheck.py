"""Tests for polarisation_ui.core.gain_crosscheck."""

import pytest

from polarisation_ui.core.gain_crosscheck import (
    GainCrossCheckLevel,
    evaluate_gain_crosscheck,
)


class TestEvaluateGainCrosscheck:
    def test_perfect_agreement_passes(self):
        levels = [
            GainCrossCheckLevel(
                level=10.0,
                pm_power_W=1e-5,
                per_gain={1: (0.1, 1e-5), 2: (0.5, 1e-5)},
            ),
        ]
        result = evaluate_gain_crosscheck(levels, tolerance_pct=1.0)
        assert result.worst_spread_pct == pytest.approx(0.0)
        assert result.worst_pm_deviation_pct == pytest.approx(0.0)
        assert result.passed is True

    def test_detects_spread_between_gains(self):
        levels = [
            GainCrossCheckLevel(
                level=10.0,
                pm_power_W=1e-5,
                per_gain={1: (0.1, 1.1e-5), 2: (0.5, 0.9e-5)},
            ),
        ]
        result = evaluate_gain_crosscheck(levels, tolerance_pct=5.0)
        # spread = (1.1e-5 - 0.9e-5) / 1.0e-5 * 100 = 20%
        assert result.worst_spread_pct == pytest.approx(20.0, abs=0.1)
        assert result.passed is False

    def test_detects_deviation_from_reference(self):
        levels = [
            GainCrossCheckLevel(
                level=10.0,
                pm_power_W=1.0e-5,
                per_gain={1: (0.1, 1.0e-5), 2: (0.5, 1.0e-5)},
            ),
            GainCrossCheckLevel(
                level=20.0,
                pm_power_W=1.0e-6,
                per_gain={1: (0.01, 1.3e-6), 2: (0.05, 1.3e-6)},
            ),
        ]
        result = evaluate_gain_crosscheck(levels, tolerance_pct=5.0)
        assert result.worst_spread_pct == pytest.approx(0.0, abs=1e-9)
        assert result.worst_pm_deviation_pct == pytest.approx(30.0, abs=0.1)
        assert result.passed is False

    def test_worst_case_across_multiple_levels(self):
        levels = [
            GainCrossCheckLevel(level=1.0, pm_power_W=1e-5, per_gain={1: (0.1, 1.0e-5)}),
            GainCrossCheckLevel(
                level=2.0,
                pm_power_W=1e-6,
                per_gain={1: (0.01, 1.05e-6), 2: (0.05, 0.95e-6)},
            ),
        ]
        result = evaluate_gain_crosscheck(levels, tolerance_pct=100.0)
        # only the second level has 2+ gains -> spread computed from it alone
        assert result.worst_spread_pct == pytest.approx(10.0, abs=0.5)

    def test_level_with_saturated_stage_still_evaluated(self):
        # Gain 2 saturated at this level and is simply absent.
        levels = [
            GainCrossCheckLevel(level=1.0, pm_power_W=1e-5, per_gain={1: (0.1, 1.0e-5)}),
        ]
        with pytest.raises(ValueError):
            # Only one gain reading total -> nothing to compare.
            evaluate_gain_crosscheck(levels)

    def test_raises_on_empty_levels(self):
        with pytest.raises(ValueError):
            evaluate_gain_crosscheck([])

    def test_to_json_dict_has_expected_keys(self):
        levels = [
            GainCrossCheckLevel(
                level=10.0, pm_power_W=1e-5, per_gain={1: (0.1, 1e-5), 2: (0.5, 1e-5)}
            ),
        ]
        result = evaluate_gain_crosscheck(levels)
        d = result.to_json_dict()
        assert set(d) == {
            "worst_spread_pct",
            "worst_pm_deviation_pct",
            "tolerance_pct",
            "passed",
            "levels",
        }
        assert d["levels"][0]["per_gain"]["1"] == {"voltage_V": 0.1, "power_W": 1e-5}
