import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import List, Optional
from contextlib import AsyncExitStack
from openai import AsyncOpenAI, RateLimitError
import json


# A single stack to hold all our async contexts
exit_stack: AsyncExitStack = AsyncExitStack()

# setup the OpenAI Client
openai_client = AsyncOpenAI()

# Global session handle
session: Optional[ClientSession] = None

async def connect_to_server(url: str, headers: dict) -> None:
    """
    Establish and retain a global MCP ClientSession over SSE using AsyncExitStack.

    Args:
        url: The full SSE endpoint URL (including any query params).
        headers: A dict of HTTP headers to include in the SSE handshake.
    """
    global session

    # Enter the SSE client context (opens the read/write streams)
    read_stream, write_stream = await exit_stack.enter_async_context(
        sse_client(url, headers=headers)
    )

    # Enter the MCP ClientSession context
    session = await exit_stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )

    # Perform the handshake
    await session.initialize()

    # (Optional) List tools on connect
    #tools_result = await session.list_tools()
    #print("\nConnected to server with tools:")
    #for tool in tools_result.tools:
    #    print(f"  - {tool.name}: {tool.description}")

async def get_mcp_tools() -> List[str]:
    """
    Return the list of available MCP tool names from the global session.

    Raises:
        RuntimeError: if not connected yet.
    """
    if session is None:
        raise RuntimeError("MCP session is not initialized—call connect_to_server() first.")
    

    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]

async def shutdown_server() -> None:
    """
    Cleanly close all contexts (SSE + MCP session) via the AsyncExitStack.
    """
    global session
    await exit_stack.aclose()
    session = None
    

async def process_query(query: str) -> None:
    """
    For demonstration: fetch and print the list of MCP tools.
    """
    print(f"\nProcessing query: {query!r}")
    tools = await get_mcp_tools()
    print("Available tools:")
    for name in tools:
        print(f"  - {name}")
    print()
    
    # Initial OpenAI API call
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto",
    )

    # Get assistant's response
    assistant_message = response.choices[0].message
    
    # Initialize conversation with user query and assistant response
    messages = [
        {"role": "user", "content": query},
        assistant_message,
    ]

    # Handle tool calls if present
    if assistant_message.tool_calls:
        # Process each tool call
        for tool_call in assistant_message.tool_calls:
            # Execute tool call
            print(f"AI decided that you need tool:  {tool_call.function.name}")
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

            # Add tool response to conversation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text,
                }
            )

        # Get final response from OpenAI with tool results
        final_response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="none",  # Don't allow more tool calls
        )

        print(f"Final Output:  {final_response.choices[0].message.content}")
        return final_response.choices[0].message.content

    # No tool calls, just return the direct response
    print(f"AI decided that you DO NOT need tools")
    return assistant_message.content
         
async def main():
    """Main entry point for the client."""
    
    url = (
        "https://weather-mcp.delightfultree-4793c2ae.eastus2.azurecontainerapps.io/sse"
    )
    # url="http://localhost:8000/sse"

    headers = {"x-api-key": "5e3069a7c37c0f791ebe6b7591c2d8a3"}  # weather api key

    # 1) Connect once
    await connect_to_server(url, headers)

    # 2) Loop reading user input
    while True:
        # Use run_in_executor so input() doesn't block the event loop
        query = await asyncio.get_event_loop().run_in_executor(
            None, input, "Enter query (or 'quit' to exit): "
        )
        if query.strip().lower() in ("quit", "exit"):
            break

        # 3) Process each query
        try:
            await process_query(query)
        except Exception as e:
            print(f"⚠️ Error processing query: {e}")

    # 4) Clean up
    await shutdown_server()


if __name__ == "__main__":
    asyncio.run(main())
