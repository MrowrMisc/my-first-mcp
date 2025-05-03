import asyncio
import json
import uuid
from typing import Any, Dict

from fastmcp import FastMCP
from mcp import types
from mcp.shared.message import SessionMessage
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from my_first_mcp.app import get_app

# In-memory session management
SESSIONS: Dict[str, asyncio.Queue[str]] = {}

app = get_app()
mcp = FastMCP.from_fastapi(app=app, timeout=60)


class FakeSessionMessage(SessionMessage):
    def __init__(self, root: dict):
        # Guessing JSON-RPC root is always a `ClientRequest`
        self.root = types.ClientRequest.model_validate(root)


class InMemoryStream:
    def __init__(self) -> None:
        self.in_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.out_queue: asyncio.Queue[str] = asyncio.Queue()
        self._closed = False

    def __aiter__(self) -> "InMemoryStream":
        return self

    async def __anext__(self) -> SessionMessage:
        if self._closed:
            raise StopAsyncIteration
        return await self.read()

    async def read(self) -> SessionMessage:
        message_dict = await self.in_queue.get()
        return SessionMessage(root=types.ClientRequest.model_validate(message_dict))

    async def write(self, message: str) -> None:
        await self.out_queue.put(message)

    async def __aenter__(self) -> "InMemoryStream":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._closed = True

    async def call(self, server: Any, message: dict) -> dict:
        await self.in_queue.put(message)
        async with self:
            await server.run(self, self, server.create_initialization_options())
        raw = await self.out_queue.get()
        return json.loads(raw)


async def mcp_handler(request: Request) -> JSONResponse:
    method = request.method

    if method == "POST":
        body = await request.json()
        rpc_method = body.get("method")
        session_id = request.headers.get("Mcp-Session-Id")

        if rpc_method == "initialize":
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = asyncio.Queue()

            stream = InMemoryStream()
            result = await stream.call(mcp._mcp_server, body)

            response = JSONResponse(result)
            response.headers["Mcp-Session-Id"] = session_id
            return response

        if not session_id or session_id not in SESSIONS:
            return JSONResponse({"error": "Missing or invalid session ID"}, status_code=400)

        stream = InMemoryStream()
        result = await stream.call(mcp._mcp_server, body)
        return JSONResponse(result)

    elif method == "GET":
        session_id = request.query_params.get("session")
        if not session_id or session_id not in SESSIONS:
            return JSONResponse({"error": "Missing or invalid session"}, status_code=400)

        queue = SESSIONS[session_id]

        async def event_stream():
            while True:
                msg = await queue.get()
                yield {"data": msg}

        return EventSourceResponse(event_stream())

    elif method == "DELETE":
        session_id = request.headers.get("Mcp-Session-Id")
        if not session_id or session_id not in SESSIONS:
            return JSONResponse({"error": "Missing or invalid session ID"}, status_code=400)

        del SESSIONS[session_id]
        return JSONResponse({"status": "Session terminated"})

    return JSONResponse({"error": "Method not allowed"}, status_code=405)


# Unified /mcp route
sse_mcp = Starlette(routes=[Route("/mcp", endpoint=mcp_handler, methods=["POST", "GET", "DELETE"])])
