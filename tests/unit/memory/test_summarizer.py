from app.llm.base import BaseLLM
from app.llm.models import LLMResponse
from app.memory.models import MemoryRecord
from app.memory.summarizer import MemorySummarizer


class FakeLLM(BaseLLM):
    def __init__(self):
        self.call_count = 0
        self.messages = None
        self.response = "Summary"

    def generate(self, messages):
        self.call_count += 1
        self.messages = messages
        return LLMResponse(content=self.response)


def test_summarize_calls_llm():
    llm = FakeLLM()

    summarizer = MemorySummarizer(llm)

    memories = [
        MemoryRecord(content="User likes Python"),
        MemoryRecord(content="User uses Ruff"),
    ]

    try:
        summarizer.summarize(memories)
    except NotImplementedError:
        pass

    assert llm.call_count == 1


def test_summarize_returns_memory_record():
    llm = FakeLLM()

    summarizer = MemorySummarizer(llm)

    memories = [
        MemoryRecord(content="User likes Python"),
    ]

    summary = summarizer.summarize(memories)

    assert isinstance(summary, MemoryRecord)


def test_summary_contains_llm_response():
    llm = FakeLLM()
    llm.response = "The user is a Python developer."

    summarizer = MemorySummarizer(llm)

    memories = [
        MemoryRecord(content="User likes Python"),
    ]

    summary = summarizer.summarize(memories)

    assert summary.content == llm.response


def test_prompt_contains_memory_contents():
    llm = FakeLLM()

    summarizer = MemorySummarizer(llm)

    memories = [
        MemoryRecord(content="User likes Python"),
        MemoryRecord(content="User uses Ruff"),
    ]

    summarizer.summarize(memories)

    prompt = llm.messages[-1].content

    assert "User likes Python" in prompt
    assert "User uses Ruff" in prompt
