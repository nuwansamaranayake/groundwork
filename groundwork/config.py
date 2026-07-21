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


def forbid_mock(cfg: BaseConfig, what: str) -> None:
    """Standard 3: no silent mock or fallback outside development. Fail loud."""
    if cfg.app_env is not Env.development:
        raise RuntimeError(
            f"Mock or fallback '{what}' is forbidden in {cfg.app_env.value}. "
            "Surface a typed error instead of fabricating data."
        )
