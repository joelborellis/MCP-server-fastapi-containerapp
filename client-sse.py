import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

nest_asyncio.apply()  # Needed to run interactive python

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use SSE transport.
3. The server is listening on port 8050.

To run the server:
uv run server.py
"""


async def main():
    
    url="https://weather-mcp.delightfultree-4793c2ae.eastus2.azurecontainerapps.io/sse"
    #url="http://localhost:8000/sse"
    
    
    headers = {
    'x-api-key': '5e3069a7c37c0f791ebe6b7591c2d8a3'  # weather api key
    }
    # Connect to the server using SSE
    async with sse_client(headers=headers, url=url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("get_alerts", arguments={"state": "TX"})
            print(f"Weather = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())