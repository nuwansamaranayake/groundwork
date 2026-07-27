from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: Env = Env.development
    log_level: str = "INFO"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Model pinning: model IDs come from env, never hardcoded. These bind the vars
    # .env.example ships; apps extend BaseConfig with their own AppConfig fields.
    llm_model_extraction: str = ""
    embedding_model: str = ""
    # Bounds for every gateway call. The SDK defaults (600s per attempt, 2 retries,
    # ~30 min worst case) are unusable for the sole sanctioned LLM path.
    llm_timeout_s: float = 30.0
    llm_max_retries: int = 2


def forbid_mock(cfg: BaseConfig, what: str) -> None:
    """Standard 3: no silent mock or fallback outside development. Fail loud."""
    if cfg.app_env is not Env.development:
        raise RuntimeError(
            f"Mock or fallback '{what}' is forbidden in {cfg.app_env.value}. "
            "Surface a typed error instead of fabricating data."
        )
