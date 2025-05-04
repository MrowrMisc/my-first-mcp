import asyncio

from fastmcp import Client
from mcp.client.streamable_http import StreamableHTTPTransport
import uvicorn


# def run_api():
#     #  You must pass the application as an import string to enable 'reload' or 'workers'.
#     uvicorn.run(
#         "my_first_mcp.app:app",
#         host="127.0.0.1",
#         port=9000,
#         log_level="info",
#         use_colors=True,
#         workers=1,
#         reload=True,
#     )


# def run_mcp():
#     #  You must pass the application as an import string to enable 'reload' or 'workers'.
#     uvicorn.run(
#         "my_first_mcp.mcp:sse_mcp",
#         host="127.0.0.1",
#         port=8000,
#         log_level="info",
#         use_colors=True,
#         workers=1,
#         reload=True,
#     )


# async def serve(app: str, port: int) -> None:
#     config = uvicorn.Config(app, host="127.0.0.1", port=port, loop="asyncio", reload=True, workers=1)
#     server = uvicorn.Server(config)
#     await server.serve()


# async def run_mcp_and_api():
#     await asyncio.gather(
#         serve("my_first_mcp.mcp:app", 9000),
#         serve("my_first_mcp.mcp:sse_mcp", 8000),
#     )


mcp_server_script = "__main__.py"

transport = StreamableHTTPTransport(
    url="http://127.0.0.1:8000/mcp",
)



# class StreamableHTTPTransport:
#     """StreamableHTTP client transport implementation."""

#     def __init__(
#         self,
#         url: str,
#         headers: dict[str, Any] | None = None,
#         timeout: timedelta = timedelta(seconds=30),
#         sse_read_timeout: timedelta = timedelta(seconds=60 * 5),
#     ) -> None:
#         """Initialize the StreamableHTTP transport.

#         Args:
#             url: The endpoint URL.
#             headers: Optional headers to include in requests.
#             timeout: HTTP timeout for regular operations.
#             sse_read_timeout: Timeout for SSE read operations.
#         """
#         self.url = url
#         self.headers = headers or {}
#         self.timeout = timeout
#         self.sse_read_timeout = sse_read_timeout
#         self.session_id: str | None = None
#         self.request_headers = {
#             ACCEPT: f"{JSON}, {SSE}",
#             CONTENT_TYPE: JSON,
#             **self.headers,
#         }
