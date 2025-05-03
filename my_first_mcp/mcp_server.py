# my_first_mcp/mcp_server.py

import types as mcp_types

from fastapi import FastAPI, Request
from mcp.server import Server

# from mcp.shared.transports.streamable_http_server import StreamableHTTPServerTransport
from mcp.server.streamable_http import StreamableHTTPServerTransport
from mcp.shared.message import SessionMessage
from mcp.types import JSONRPCMessage, JSONRPCNotification
from starlette.responses import Response

app = FastAPI()

# Global MCP Server instance
mcp_server = Server("MyMCPServer")

from mcp import types as mcp_types  # the real one, not Python's built-in types!


@mcp_server.list_prompts()
async def list_prompts() -> list[mcp_types.Prompt]:
    return [
        mcp_types.Prompt(
            name="say_hello",
            displayName="Say Hello",
            description="Just returns a greeting",
            inputs=[],
        )
    ]


@mcp_server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> mcp_types.GetPromptResult:
    return mcp_types.GetPromptResult(messages=[mcp_types.TextContent(type="text", text="Hello world!")])


@mcp_server.list_tools()
async def handle_list_tools() -> list[mcp_types.Tool]:
    print("⚙️ Listing tools")
    return []


original_handler = mcp_server._handle_request


async def debug_handle_request(req: mcp_types.ServerRequest) -> mcp_types.ServerResult:
    print("📥 MCP Server received request method:", getattr(req.root, "method", "<no method>"))
    return await original_handler(req)


mcp_server._handle_request = debug_handle_request


# Set up tools (example)
@(mcp_server.call_tool())
async def echo_tool(ctx, arguments: dict[str, str]) -> dict[str, str]:
    print(f"Echo tool called with arguments: {arguments}")
    return {"echo": arguments.get("message", "")}


init_options = mcp_server.create_initialization_options()
print("Initialization options:", init_options.model_dump())


# This is the handler that connects the server transport to FastAPI
@app.api_route("/mcp", methods=["GET", "POST", "DELETE"])
async def mcp_entrypoint(request: Request) -> Response:
    print(f"Received request: {request.method} {request.url}")

    # Grab session ID from headers (optional for now)
    session_id = request.headers.get("mcp-session-id")
    print(f"Session ID: {session_id}")

    transport = StreamableHTTPServerTransport(
        mcp_session_id=session_id,
        is_json_response_enabled=True,
    )

    async with transport.connect() as (read_stream, write_stream):
        print("Connected to transport")

        # Send a quick "hello" log notification to confirm activity

        notif = JSONRPCNotification(
            method="notifications/message",
            params={
                "level": "info",
                "data": "🔌 Hello from MCP server!",
            },
            jsonrpc="2.0",
        )

        wrapped = JSONRPCMessage(root=notif)
        await write_stream.send(SessionMessage(message=wrapped))

        # Start processing
        await mcp_server.run(read_stream, write_stream, stateless=True, initialization_options=init_options)

    print("Transport closed, returning response")
    return Response(status_code=204)
