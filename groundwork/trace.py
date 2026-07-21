import json
import logging

logger = logging.getLogger("groundwork.trace")


def record_call(**fields) -> None:
    """Every LLM call is a trace. These logs are the raw material for Seismograph."""
    logger.info("llm_call %s", json.dumps(fields, default=str))
