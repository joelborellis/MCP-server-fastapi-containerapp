import asyncio

from typing import Optional

from contextlib import AsyncExitStack


from mcp import ClientSession

from mcp.client.sse import sse_client

from dotenv import load_dotenv
import json


load_dotenv()  # load environment variables from .env


class MCPClient:

    def __init__(self):

        # Initialize session and client objects

        self.session: Optional[ClientSession] = None

        self.exit_stack = AsyncExitStack()

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""

        # Store the context managers so they stay alive

        self._streams_context = sse_client(url=server_url)

        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)

        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize

        await self.session.initialize()

        # List available tools to verify connection

        print("Initialized SSE client...")

        print("Listing tools...")

        response = await self.session.list_tools()

        tools = response.tools

        print("\nConnected to server with tools:", [tool.name for tool in tools])

        print("Calling tool ....")

        response = await self.session.call_tool(
            name="firecrawl_scrape",
            arguments={
                "url": "https://sports.yahoo.com/nfl/article/cowboys-offensive-lineman-tom-rafferty-who-played-14-seasons-with-dallas-dies-at-70-003824122.html",
                "formats": ["markdown"],
                "onlyMainContent": True,
                "waitFor": 1000,
                "timeout": 30000,
                "mobile": False,
                "includeTags": ["article", "main"],
                "excludeTags": ["nav", "footer"],
                "skipTlsVerification": False,
            },
        )

        print(response.content[0].text)

    async def cleanup(self):
        """Properly clean up the session and streams"""

        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)


async def main():

    if len(sys.argv) < 2:

        print(
            "Usage: uv run client.py <URL of SSE MCP server (i.e. http://localhost:8080/sse)>"
        )

        sys.exit(1)

    client = MCPClient()

    try:

        await client.connect_to_sse_server(server_url=sys.argv[1])

    finally:

        await client.cleanup()


if __name__ == "__main__":

    import sys

    asyncio.run(main())
