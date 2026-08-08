from pydantic import BaseModel, Field

from app.tools.base import BaseTool
from app.tools.models import ToolResult


class CalculatorArgs(BaseModel):
    """Arguments accepted by the calculator tool."""

    operation: str = Field(description="Arithmetic operation: add, subtract, multiply, or divide.")
    left: float
    right: float


class CalculatorTool(BaseTool[CalculatorArgs]):
    """Perform basic arithmetic operations."""

    name = "calculator"
    description = "Perform basic arithmetic operations."
    args_schema = CalculatorArgs

    def execute(self, args: CalculatorArgs) -> ToolResult:
        """Execute the requested arithmetic operation."""
        operations = {
            "add": lambda: args.left + args.right,
            "subtract": lambda: args.left - args.right,
            "multiply": lambda: args.left * args.right,
            "divide": lambda: args.left / args.right,
        }

        if args.operation not in operations:
            return ToolResult(
                success=False,
                error=f"Unsupported operation: {args.operation}",
            )

        if args.operation == "divide" and args.right == 0:
            return ToolResult(
                success=False,
                error="Cannot divide by zero.",
            )

        return ToolResult(
            success=True,
            output=operations[args.operation](),
        )
