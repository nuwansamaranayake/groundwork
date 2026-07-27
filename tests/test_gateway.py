from types import SimpleNamespace

import pytest

import groundwork.gateway as gateway_mod
from groundwork import BaseConfig, GatewayError, LLMGateway


@pytest.fixture
def traces(monkeypatch):
    calls: list[dict] = []
    monkeypatch.setattr(gateway_mod, "record_call", lambda **fields: calls.append(fields))
    return calls


def _gateway() -> LLMGateway:
    return LLMGateway(BaseConfig(openrouter_api_key="test-key"))


def _stub_client(result, seen_kwargs: dict | None = None):
    def create(**kwargs):
        if seen_kwargs is not None:
            seen_kwargs.update(kwargs)
        if isinstance(result, Exception):
            raise result
        return result

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def _response(content="hello", with_choices=True, with_usage=True):
    usage = (
        SimpleNamespace(
            model_dump=lambda: {
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15,
            }
        )
        if with_usage
        else None
    )
    choice = SimpleNamespace(message=SimpleNamespace(content=content), finish_reason="stop")
    return SimpleNamespace(id="resp-1", choices=[choice] if with_choices else [], usage=usage)


def test_client_is_bounded_by_config():
    cfg = BaseConfig(openrouter_api_key="test-key", llm_timeout_s=12.5, llm_max_retries=1)
    gw = LLMGateway(cfg)
    assert gw._client.timeout == 12.5
    assert gw._client.max_retries == 1


def test_per_call_timeout_override_reaches_the_sdk(traces):
    gw = _gateway()
    seen: dict = {}
    gw._client = _stub_client(_response(), seen_kwargs=seen)
    gw.complete(model="m", messages=[{"role": "user", "content": "hi"}], timeout=5.0)
    assert seen["timeout"] == 5.0


def test_failed_call_is_traced_then_reraised(traces):
    """Original defect: any raise from create() skipped record_call entirely,
    giving a success-only trace stream during outages."""
    gw = _gateway()
    gw._client = _stub_client(RuntimeError("boom 429"))
    with pytest.raises(RuntimeError, match="boom 429"):
        gw.complete(model="m", messages=[{"role": "user", "content": "hi"}])
    assert len(traces) == 1
    assert traces[0]["status"] == "error"
    assert "boom 429" in traces[0]["error"]


def test_null_content_raises_typed_gateway_error(traces):
    """Original defect: content=None with json_schema raised TypeError from
    json.loads(None) with no model/provider context."""
    gw = _gateway()
    gw._client = _stub_client(_response(content=None))
    with pytest.raises(GatewayError) as excinfo:
        gw.complete(
            model="m",
            messages=[{"role": "user", "content": "hi"}],
            json_schema={"name": "s", "schema": {}},
        )
    assert excinfo.value.model == "m"
    assert excinfo.value.finish_reason == "stop"
    assert excinfo.value.response_id == "resp-1"
    assert traces[-1]["status"] == "error"


def test_empty_choices_raises_typed_gateway_error(traces):
    """Original defect: empty choices raised a bare IndexError."""
    gw = _gateway()
    gw._client = _stub_client(_response(with_choices=False))
    with pytest.raises(GatewayError):
        gw.complete(model="m", messages=[{"role": "user", "content": "hi"}])


def test_usage_is_traced_as_structured_json(traces):
    """Original defect: usage was flattened to a Python repr string by
    json.dumps(default=str) instead of structured token fields."""
    gw = _gateway()
    gw._client = _stub_client(_response())
    out = gw.complete(model="m", messages=[{"role": "user", "content": "hi"}])
    assert out == "hello"
    assert traces[-1]["status"] == "ok"
    assert traces[-1]["usage"] == {
        "prompt_tokens": 5,
        "completion_tokens": 10,
        "total_tokens": 15,
    }


def test_json_schema_result_is_parsed(traces):
    gw = _gateway()
    gw._client = _stub_client(_response(content='{"a": 1}'))
    out = gw.complete(
        model="m",
        messages=[{"role": "user", "content": "hi"}],
        json_schema={"name": "s", "schema": {}},
    )
    assert out == {"a": 1}
