import hashlib
import json
import time
from typing import Any, Optional

from openai import OpenAI

from .config import BaseConfig
from .trace import configure_tracing, record_call


class GatewayError(RuntimeError):
    """Typed error for a call that reached the provider but yielded no usable
    completion (empty choices, null content, refusal). Carries model and provider
    context instead of leaking a bare IndexError/TypeError."""

    def __init__(
        self,
        message: str,
        *,
        model: str,
        finish_reason: Optional[str] = None,
        response_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.model = model
        self.finish_reason = finish_reason
        self.response_id = response_id


class LLMGateway:
    """Provider-agnostic gateway. Default provider is OpenRouter, which is OpenAI-compatible.
    Every app calls the LLM through here so model choice, structured output, and tracing are
    centralized and swappable."""

    def __init__(self, cfg: BaseConfig):
        if not cfg.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set. Refusing to run blind.")
        self._cfg = cfg
        configure_tracing(cfg.log_level)
        self._client = OpenAI(
            base_url=cfg.openrouter_base_url,
            api_key=cfg.openrouter_api_key,
            timeout=cfg.llm_timeout_s,
            max_retries=cfg.llm_max_retries,
        )

    def complete(
        self,
        *,
        model: str,
        messages: list[dict],
        json_schema: Optional[dict] = None,
        temperature: float = 0.0,
        timeout: Optional[float] = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}
        if json_schema:
            kwargs["response_format"] = {"type": "json_schema", "json_schema": json_schema}
        if timeout is not None:
            kwargs["timeout"] = timeout
        prompt_hash = hashlib.sha256(
            json.dumps(messages, sort_keys=True).encode()
        ).hexdigest()[:16]
        t0 = time.time()
        try:
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            record_call(
                model=model,
                prompt_hash=prompt_hash,
                temperature=temperature,
                latency_s=round(time.time() - t0, 3),
                status="error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        latency_s = round(time.time() - t0, 3)
        usage = resp.usage.model_dump() if getattr(resp, "usage", None) else None
        choice = resp.choices[0] if resp.choices else None
        content = choice.message.content if choice else None
        if content is None:
            finish_reason = getattr(choice, "finish_reason", None)
            response_id = getattr(resp, "id", None)
            record_call(
                model=model,
                prompt_hash=prompt_hash,
                temperature=temperature,
                latency_s=latency_s,
                status="error",
                error="empty completion (no choices or null content)",
                finish_reason=finish_reason,
                response_id=response_id,
                usage=usage,
            )
            raise GatewayError(
                f"Model '{model}' returned no usable completion "
                f"(finish_reason={finish_reason!r}, response_id={response_id!r}).",
                model=model,
                finish_reason=finish_reason,
                response_id=response_id,
            )
        record_call(
            model=model,
            prompt_hash=prompt_hash,
            temperature=temperature,
            latency_s=latency_s,
            status="ok",
            usage=usage,
        )
        return json.loads(content) if json_schema else content
