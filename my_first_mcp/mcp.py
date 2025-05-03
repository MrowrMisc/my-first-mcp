from typing import Any

from fastmcp import FastMCP
from fastmcp.server.openapi import FastMCPOpenAPI
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from my_first_mcp.app import get_app


def _create_sse_server(mcp: FastMCPOpenAPI):
    transport = SseServerTransport("/messages/")

    async def handle_sse(request):  # type: ignore
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as (read_stream, write_stream):  # type: ignore
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )  # type: ignore

    routes: list[Any] = [
        Route("/sse/", endpoint=handle_sse),  # type: ignore
        Mount("/messages/", app=transport.handle_post_message),
    ]
    return Starlette(routes=routes)


def run_stdio():
    mcp.run()

    async def handle_sse(request):  # type: ignore
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:  # type: ignore
            await mcp._mcp_server.run(
                streams, streams, mcp._mcp_server.create_initialization_options()
            )  # type: ignore


app = get_app()
mcp = FastMCP.from_fastapi(app=app, timeout=60)
sse_mcp = _create_sse_server(mcp)
