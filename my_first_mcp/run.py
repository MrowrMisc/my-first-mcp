import asyncio

import uvicorn


def run_api():
    #  You must pass the application as an import string to enable 'reload' or 'workers'.
    uvicorn.run(
        "my_first_mcp.app:app",
        host="127.0.0.1",
        port=9000,
        log_level="info",
        use_colors=True,
        workers=1,
        reload=True,
    )


def run_mcp():
    #  You must pass the application as an import string to enable 'reload' or 'workers'.
    uvicorn.run(
        "my_first_mcp.mcp:sse_mcp",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        use_colors=True,
        workers=1,
        reload=True,
    )


async def serve(app: str, port: int) -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, loop="asyncio", reload=True, workers=1)
    server = uvicorn.Server(config)
    await server.serve()


async def run_mcp_and_api():
    await asyncio.gather(
        serve("my_first_mcp.mcp:app", 9000),
        serve("my_first_mcp.mcp:sse_mcp", 8000),
    )
