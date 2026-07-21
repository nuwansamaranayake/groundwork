import hashlib
import json
import time
from typing import Any, Optional

from openai import OpenAI

from .config import BaseConfig
from .trace import record_call


class LLMGateway:
    """Provider-agnostic gateway. Default provider is OpenRouter, which is OpenAI-compatible.
    Every app calls the LLM through here so model choice, structured output, and tracing are
    centralized and swappable."""

    def __init__(self, cfg: BaseConfig):
        if not cfg.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set. Refusing to run blind.")
        self._cfg = cfg
        self._client = OpenAI(base_url=cfg.openrouter_base_url, api_key=cfg.openrouter_api_key)

    def complete(
        self,
        *,
        model: str,
        messages: list[dict],
        json_schema: Optional[dict] = None,
        temperature: float = 0.0,
    ) -> Any:
        kwargs: dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}
        if json_schema:
            kwargs["response_format"] = {"type": "json_schema", "json_schema": json_schema}
        t0 = time.time()
        resp = self._client.chat.completions.create(**kwargs)
        content = resp.choices[0].message.content
        record_call(
            model=model,
            prompt_hash=hashlib.sha256(
                json.dumps(messages, sort_keys=True).encode()
            ).hexdigest()[:16],
            temperature=temperature,
            latency_s=round(time.time() - t0, 3),
            usage=getattr(resp, "usage", None),
        )
        return json.loads(content) if json_schema else content
