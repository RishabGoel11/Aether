from app.tools.models import ToolDefinition
from app.tools.policy import ToolPolicy


def create_tool(name: str) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description=f"{name} tool",
        input_schema={
            "type": "object",
            "properties": {},
        },
    )


def test_policy_allows_all_tools_by_default():
    policy = ToolPolicy()

    assert policy.is_allowed(create_tool("calculator"))
    assert policy.is_allowed(create_tool("filesystem"))


def test_policy_allows_configured_tool():
    policy = ToolPolicy(
        allowed_tools={"calculator"},
    )

    assert policy.is_allowed(create_tool("calculator"))


def test_policy_denies_unconfigured_tool():
    policy = ToolPolicy(
        allowed_tools={"calculator"},
    )

    assert not policy.is_allowed(create_tool("filesystem"))
