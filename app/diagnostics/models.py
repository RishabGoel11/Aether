from pydantic import BaseModel, Field


class DiagnosticResult(BaseModel):
    """
    Represents the result of a single diagnostic check.
    """

    name: str
    success: bool
    message: str


class DiagnosticReport(BaseModel):
    """
    Represents the complete diagnostics report.
    """

    results: list[DiagnosticResult] = Field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(result.success for result in self.results)

    @property
    def failed(self) -> int:
        return sum(not result.success for result in self.results)

    @property
    def healthy(self) -> bool:
        return self.failed == 0
