import io
import json
import logging

from groundwork.trace import configure_tracing, logger, record_call


def test_record_call_emits_by_default():
    """Original defect: fresh interpreter, no app-side logging config, record_call
    emitted nothing (handler-less logger under the WARNING+ lastResort handler)."""
    assert logger.handlers, "trace logger must attach a default handler at import"
    buf = io.StringIO()
    handler = logger.handlers[0]
    old_stream = handler.setStream(buf)
    try:
        record_call(model="m1", prompt_hash="abc")
    finally:
        handler.setStream(old_stream)
    line = buf.getvalue()
    assert "llm_call" in line
    payload = json.loads(line.split("llm_call ", 1)[1])
    assert payload["model"] == "m1"


def test_configure_tracing_is_idempotent_and_honors_level():
    n_handlers = len(logger.handlers)
    configure_tracing("WARNING")
    assert logger.level == logging.WARNING
    assert len(logger.handlers) == n_handlers
    configure_tracing("INFO")
    assert logger.level == logging.INFO
    assert logger.propagate is False
