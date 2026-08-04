import pytest

from zk_utils.presentation.mcp.server import mcp


@pytest.mark.integration
@pytest.mark.asyncio
async def test_path_inputs_should_use_plain_string_json_schema() -> None:
    tools = await mcp.list_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    for tool_name in (
        "get_note_content",
        "get_link_to_notes",
        "get_linked_by_notes",
        "get_related_notes",
        "create_note",
    ):
        path_schema = tools_by_name[tool_name].input_schema["properties"]["path"]

        assert path_schema["type"] == "string"
        assert "format" not in path_schema
