import logging

from app.config.config import LoggingSettings


def configure_logging(settings: LoggingSettings) -> None:
    """
    Configure the application's logging system.
    """
    
    logging.basicConfig(
        level=settings.level.value,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Reduce noise from third-party libraries.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)