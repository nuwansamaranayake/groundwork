import json
import logging
import sys

logger = logging.getLogger("groundwork.trace")


def configure_tracing(level: str = "INFO") -> None:
    """Make traces emit by default instead of depending on app-side logging config.

    Attaches a stderr StreamHandler emitting one line per call, sets the level
    (LLMGateway passes BaseConfig.log_level), and stops propagation so lines are
    not duplicated by app root handlers. Idempotent. Apps that want custom routing
    add their own handlers to the 'groundwork.trace' logger.
    """
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False


configure_tracing()


def record_call(**fields) -> None:
    """Every LLM call is a trace. These logs are the raw material for Seismograph."""
    logger.info("llm_call %s", json.dumps(fields, default=str))
