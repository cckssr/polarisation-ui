"""The encoder-diagnostic texts come from the injected configuration."""

from __future__ import annotations

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.controllers.data_controller import _evaluate_encoder


def test_a_healthy_encoder_reports_ok(config: AppConfig) -> None:
    assert _evaluate_encoder({"ocf": True}, "Enc A", config) == (True, "Enc A: OK")


def test_every_fault_flag_is_named_from_the_config(config: AppConfig) -> None:
    ok, text = _evaluate_encoder(
        {"compHigh": True, "compLow": True, "cof": True, "ocf": False}, "Enc B", config
    )
    assert not ok
    expected = "; ".join(
        config.message(f"connection.{key}")
        for key in ("diag_comp_high", "diag_comp_low", "diag_cof", "diag_ocf")
    )
    assert text == f"Enc B: {expected}"


def test_no_answer_is_a_fault(config: AppConfig) -> None:
    ok, text = _evaluate_encoder(None, "Enc A", config)
    assert not ok
    assert text == config.message("connection.diag_no_response", label="Enc A")


def test_a_custom_config_changes_the_texts(config: AppConfig) -> None:
    custom = config.with_overrides({"messages": {"connection": {"diag_cof": "overflow"}}})
    assert _evaluate_encoder({"cof": True, "ocf": True}, "Enc A", custom) == (
        False,
        "Enc A: overflow",
    )
