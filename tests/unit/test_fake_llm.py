import pytest

from app.llm.models import Message, Role
from tests.fakes.fake_llm import FakeLLM


def test_fake_llm_returns_configured_response():
    fake = FakeLLM(response="Hello Aether!")

    response = fake.generate(
        [
            Message(
                role=Role.USER,
                content="Hi",
            )
        ]
    )

    assert response.content == "Hello Aether!"


def test_fake_llm_records_messages():
    fake = FakeLLM()

    messages = [
        Message(
            role=Role.USER,
            content="Hello",
        )
    ]

    fake.generate(messages)

    assert fake.call_count == 1
    assert fake.received_messages == [messages]


def test_fake_llm_raises_configured_exception():
    fake = FakeLLM(exception=RuntimeError("Boom!"))

    with pytest.raises(RuntimeError):
        fake.generate([])
