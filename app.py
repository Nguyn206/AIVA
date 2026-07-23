from __future__ import annotations

from config.settings import Settings
from core.logger import configure_logging, get_logger


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    logger.info("AIVA is starting")
    logger.info("Environment: %s", settings.environment)
    logger.info("LLM provider: %s", settings.llm_provider)
    print("AIVA foundation is ready.")


if __name__ == "__main__":
    main()
