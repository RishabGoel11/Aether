from time import perf_counter

from app.debug.models import DebugEvent, DebugInfo


class DebugCollector:
    """
    Collects diagnostic information during a request.
    """

    def __init__(self) -> None:
        self.debug_info = DebugInfo()
        self._start_time: float | None = None

    def start(self) -> None:
        """
        Start timing the request.
        """
        self._start_time = perf_counter()

    def set_provider(self, provider: str) -> None:
        self.debug_info.provider = provider

    def set_model(self, model: str) -> None:
        self.debug_info.model = model

    def set_message_count(self, count: int) -> None:
        self.debug_info.message_count = count

    def set_prompt_length(self, length: int) -> None:
        self.debug_info.prompt_length = length

    def add_event(
        self,
        name: str,
        **metadata,
    ) -> None:
        """
        Record a debug event.
        """
        self.debug_info.events.append(
            DebugEvent(
                name=name,
                metadata=metadata,
            )
        )

    def finish(self) -> None:
        """
        Stop timing and record the response time.
        """
        if self._start_time is None:
            return

        elapsed = perf_counter() - self._start_time
        self.debug_info.response_time_ms = elapsed * 1000
