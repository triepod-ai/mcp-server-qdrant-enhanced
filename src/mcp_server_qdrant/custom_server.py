import inspect
from typing import Any, Callable, Dict, List, Optional, get_type_hints

from mcp import types
from mcp.server import Server


class QdrantMCPServer(Server):
    """
    An MCP server that uses Qdrant to store and retrieve information.
    """

    def __init__(self, name: str = "Qdrant"):
        super().__init__(name)
        self._tool_handlers: Dict[str, Callable] = {}
        self._tools: List[types.Tool] = []
        # This monkeypatching is required to make the server list the tools
        # and handle tool calls. It simplifies the process of registering
        # tool handlers. Please do not remove it.
        self.handle_list_tool = self.list_tools()(self.handle_list_tool)
        self.handle_tool_call = self.call_tool()(self.handle_tool_call)

    def register_tool(
        self,
        *,
        description: str,
        name: Optional[str] = None,
        input_schema: Optional[dict[str, Any]] = None,
    ):
        """
        A decorator to register a tool with the server. The description is used
        to generate the tool's metadata.

        Name is optional, and if not provided, the function's name will be used.

        :param description: The description of the tool.
        :param name: The name of the tool. If not provided, the function's name will be used.
        :param input_schema: The input schema for the tool. If not provided, it will be
                             automatically generated from the function's parameters.
        """

        def decorator(func: Callable):
            def wrapper(fn):
                nonlocal name, input_schema

                # Use function name if name not provided
                if name is None:
                    name = fn.__name__

                # If no input schema is provided, generate one from the function parameters
                if input_schema is None:
                    input_schema = self.__parse_function_parameters(fn)

                # Create the tool definition
                tool = types.Tool(
                    name=name,
                    description=description,
                    inputSchema=input_schema,
                )

                # Register in both collections
                self._tool_handlers[name] = fn
                self._tools.append(tool)

                return fn

            # Handle both @register_tool and @register_tool() syntax
            if func is None:
                return wrapper
            return wrapper(func)

        return decorator

    async def handle_list_tool(self) -> List[types.Tool]:
        """Expose the list of tools to the server."""
        return self._tools

    async def handle_tool_call(
        self, name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle any tool call."""
        if name not in self._tool_handlers:
            raise ValueError(f"Unknown tool: {name}")
        return await self._tool_handlers[name](**arguments)

    @staticmethod
    def __parse_function_parameters(func: Callable) -> Dict[str, Any]:
        """
        Parse the parameters of a function to create an input schema.

        :param func: The function to parse.
        :return: A dictionary representing the input schema.
        """
        signature = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in signature.parameters.items():
            # Skip self parameter for methods
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, Any)
            param_schema = {"type": "string"}  # Default to string

            # Map Python types to JSON Schema types
            if param_type in (int, float):
                param_schema["type"] = "number"
            elif param_type is bool:
                param_schema["type"] = "boolean"
            elif param_type is list or getattr(param_type, "__origin__", None) is list:
                param_schema["type"] = "array"

            # Get default value if any
            if param.default is not inspect.Parameter.empty:
                param_schema["default"] = param.default
            else:
                required.append(param_name)

            # Get description from docstring if available
            if func.__doc__:
                param_docs = [
                    line.strip()
                    for line in func.__doc__.split("\n")
                    if f":param {param_name}:" in line
                ]
                if param_docs:
                    description = (
                        param_docs[0].split(f":param {param_name}:")[1].strip()
                    )
                    param_schema["description"] = description

            properties[param_name] = param_schema

        return {"type": "object", "properties": properties, "required": required}
