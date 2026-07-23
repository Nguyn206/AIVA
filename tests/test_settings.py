from config.settings import Settings


def test_settings_use_defaults(monkeypatch) -> None:
    monkeypatch.delenv("AIVA_ENVIRONMENT", raising=False)
    monkeypatch.delenv("AIVA_LOG_LEVEL", raising=False)
    monkeypatch.delenv("AIVA_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = Settings.from_env(env_file="missing.env")

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.llm_provider == "openai"
    assert settings.openai_api_key is None
