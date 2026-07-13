from app.bootstrap.application import Application
from app.config.loader import ConfigLoader
from app.core.engine import ConversationEngine
from app.core.session import Session
from app.llm.factory import LLMFactory
from app.logger.config import configure_logging


class ApplicationBuilder:
    """
    Builds and configures an Aether application.
    """

    def build(self) -> Application:
        settings = ConfigLoader().load()

        configure_logging(settings.logging)

        llm = LLMFactory.create(settings.llm)

        session = Session()

        engine = ConversationEngine(
            llm=llm,
            session=session,
        )

        return Application(
            settings=settings,
            engine=engine,
        )