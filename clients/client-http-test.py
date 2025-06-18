from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    url=os.environ.get("MCP_URL")

    # Connect to a streamable HTTP server

    headers = {
        "x-api-key": os.environ.get("MCP_API_KEYS")
    }  # api key this is to connect to the mcp server

    async with streamablehttp_client(url=url, headers=headers) as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            
            print("getting session")
            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("get_nascar_news")
            print(f"{result.content[0].text}")
            
if __name__ == "__main__":
    asyncio.run(main())