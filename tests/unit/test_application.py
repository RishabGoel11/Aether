from app.bootstrap.application import Application
from app.config.config import Settings


def test_application_stores_components(
    engine,
):
    settings = Settings()

    app = Application(
        settings=settings,
        engine=engine,
    )

    assert app.settings is settings
    assert app.engine is engine


def test_application_chat_delegates_to_engine(
    engine,
):
    settings = Settings()

    app = Application(
        settings=settings,
        engine=engine,
    )

    response = app.chat("Hello")

    assert response.content == "Fake response"