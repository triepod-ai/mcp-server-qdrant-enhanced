import pytest

from src.mcp_server_qdrant.custom_server import QdrantMCPServer


def test_register_tool_decorator():
    """Test that the register_tool method works as a decorator and correctly parses parameters."""
    server = QdrantMCPServer()

    @server.register_tool(description="Test function with different parameter types")
    def test_function(text_param: str, number_param: int, flag_param: bool = False):
        """
        A test function with different parameter types.

        :param text_param: A string parameter
        :param number_param: An integer parameter
        :param flag_param: A boolean parameter with default
        """
        return f"{text_param} {number_param} {flag_param}"

    # Check that the function was registered in tool_handlers
    assert "test_function" in server._tool_handlers
    assert server._tool_handlers["test_function"] == test_function

    # Check that the tool was added to tools list
    assert len(server._tools) == 1
    tool = server._tools[0]
    assert tool.name == "test_function"
    assert tool.description == "Test function with different parameter types"

    # Check the generated schema
    schema = tool.inputSchema
    assert schema["type"] == "object"

    # Check properties
    properties = schema["properties"]
    assert "text_param" in properties
    assert properties["text_param"]["type"] == "string"
    assert "description" in properties["text_param"]

    assert "number_param" in properties
    assert properties["number_param"]["type"] == "number"

    assert "flag_param" in properties
    assert properties["flag_param"]["type"] == "boolean"
    assert "default" in properties["flag_param"]
    assert properties["flag_param"]["default"] is False

    # Check required fields
    assert "required" in schema
    assert "text_param" in schema["required"]
    assert "number_param" in schema["required"]
    assert "flag_param" not in schema["required"]  # Has default value


@pytest.mark.asyncio
async def test_handle_list_tool():
    """Test that handle_list_tool returns all registered tools."""
    server = QdrantMCPServer()

    # Register multiple tools
    @server.register_tool(description="First test tool")
    def tool_one(param1: str):
        """First tool."""
        return param1

    @server.register_tool(description="Second test tool")
    def tool_two(param1: int, param2: bool = True):
        """Second tool."""
        return param1, param2

    @server.register_tool(name="custom_name", description="Tool with custom name")
    def tool_three(param1: str):
        """Third tool with custom name."""
        return param1

    # Get the list of tools
    tools = await server.handle_list_tool()

    # Check that all tools are returned
    assert len(tools) == 3

    # Check tool names
    tool_names = [tool.name for tool in tools]
    assert "tool_one" in tool_names
    assert "tool_two" in tool_names
    assert "custom_name" in tool_names
    assert "tool_three" not in tool_names  # Should use custom name instead

    # Check tool descriptions
    descriptions = {tool.name: tool.description for tool in tools}
    assert descriptions["tool_one"] == "First test tool"
    assert descriptions["tool_two"] == "Second test tool"
    assert descriptions["custom_name"] == "Tool with custom name"

    # Check schemas are properly generated
    for tool in tools:
        assert tool.inputSchema is not None
        assert tool.inputSchema["type"] == "object"
        assert "properties" in tool.inputSchema
