"""
Tests for llama.pylib.log argument logging.

Log lines are read by humans (and kept for record-keeping), so anything
credential-like must be masked before it reaches the log file.
"""

import argparse
import logging
from typing import TYPE_CHECKING

from llama.pylib import log

if TYPE_CHECKING:
    import pytest


def test_log_args_redacts_url_credentials(caplog: pytest.LogCaptureFixture) -> None:
    ns = argparse.Namespace(api_host="http://user:secret@example.com/v1", model_id="m")
    with caplog.at_level(logging.INFO):
        log.log_args(ns)

    assert "secret" not in caplog.text
    assert "user:[redacted]@" in caplog.text


def test_log_args_keeps_plain_urls(caplog: pytest.LogCaptureFixture) -> None:
    ns = argparse.Namespace(api_host="http://localhost:9931/v1", model_id="m")
    with caplog.at_level(logging.INFO):
        log.log_args(ns)

    assert "http://localhost:9931/v1" in caplog.text
    assert "[redacted]" not in caplog.text


def test_log_args_skips_api_key(caplog: pytest.LogCaptureFixture) -> None:
    ns = argparse.Namespace(api_key="sk-123", model_id="m")
    with caplog.at_level(logging.INFO):
        log.log_args(ns)

    assert "sk-123" not in caplog.text


def test_redact_plain_values() -> None:
    assert log.redact("plain text") == "plain text"
    assert log.redact(42) == "42"
