import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Optional

import httpx


@dataclass
class JsonRpcRequest:
    jsonrpc: str
    id: str
    method: str
    params: Dict[str, Any]


class HttpStreamClient:
    def __init__(self, post_url: str, stream_url: str) -> None:
        self.post_url: str = post_url
        self.stream_url: str = stream_url
        self.session_id: Optional[str] = None
        self._event_task: Optional[asyncio.Task[None]] = None
        self._client = httpx.AsyncClient()
        self._stop_event = asyncio.Event()

    async def initialize(self) -> None:
        init_request = JsonRpcRequest(
            jsonrpc="2.0", id=f"init-{int(time.time() * 1000)}", method="initialize", params={}
        )

        print("Init headers:", {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})

        response = await self._client.post(
            self.post_url,
            json=init_request.__dict__,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                # DO NOT send Mcp-Session-Id yet
            },
        )

        print("Init response status:", response.status_code)
        print("Init response text:", await response.aread())

        self.session_id = response.headers.get("Mcp-Session-Id")
        print(f"Session established: {self.session_id}")

        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            asyncio.create_task(self._process_stream_response(response))
        else:
            result = response.json()
            print("Initialization result:", result)

        self._event_task = asyncio.create_task(self._open_event_stream())

    async def _open_event_stream(self) -> None:
        if not self.session_id:
            return

        url = f"{self.stream_url}?session={self.session_id}"

        print("Opening SSE stream...")

        try:
            async with self._client.stream("GET", url, timeout=None) as response:
                async for message in self._parse_sse_stream(response.aiter_lines()):
                    print("Received SSE message:", message)
        except Exception as e:
            print("SSE error:", e)
            await asyncio.sleep(1)
            if not self._stop_event.is_set():
                self._event_task = asyncio.create_task(self._open_event_stream())

    async def _process_stream_response(self, response: httpx.Response) -> None:
        async for message in self._parse_sse_stream(response.aiter_lines()):
            print("Received streaming message:", message)

    async def _parse_sse_stream(self, lines: AsyncGenerator[str, None]) -> AsyncGenerator[Dict[str, Any], None]:
        buffer = ""

        async for line in lines:
            if line == "":
                if buffer.startswith("data:"):
                    data = buffer[5:].strip()
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError as e:
                        print("Failed to parse JSON:", e)
                buffer = ""
            else:
                buffer += line + "\n"

    async def send_request(self, method: str, params: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
        if not self.session_id:
            raise RuntimeError("Session not initialized")

        request = JsonRpcRequest(jsonrpc="2.0", id=f"{method}-{int(time.time() * 1000)}", method=method, params=params)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Mcp-Session-Id": self.session_id,
        }

        response = await self._client.post(self.post_url, json=request.__dict__, headers=headers)

        content_type = response.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            asyncio.create_task(self._process_stream_response(response))
            return None

        return response.json()

    async def terminate(self) -> None:
        if self.session_id:
            self._stop_event.set()
            if self._event_task:
                await asyncio.sleep(0.1)

            try:
                await self._client.delete(self.post_url, headers={"Mcp-Session-Id": self.session_id})
                print("Session terminated")
            except Exception as e:
                print("Error terminating session:", e)

        await self._client.aclose()
        self.session_id = None


def main():
    client = HttpStreamClient(post_url="http://127.0.0.1:8000/messages/", stream_url="http://127.0.0.1:8000/sse/")
    asyncio.run(client.initialize())


if __name__ == "__main__":
    main()
