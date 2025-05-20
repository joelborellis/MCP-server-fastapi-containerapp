import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    
    #url = "https://sports-mcp.orangeocean-ab857605.eastus2.azurecontainerapps.io/sse" # Joel work subscription
    url = "https://mcp-server.redground-70426cdf.eastus2.azurecontainerapps.io/sse"
    #url="http://localhost:8000/sse"
    
    
    headers = {
    'x-api-key': 'eff69e24c8f84195a522e7b5df8a0bbc'  # weather api key
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
            result = await session.call_tool("get_cfb_news", arguments={})
            print(f"News = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())