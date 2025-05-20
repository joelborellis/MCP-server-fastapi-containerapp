import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import List, Optional
from contextlib import AsyncExitStack
from openai import AsyncAzureOpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI variables from .env file
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
AZURE_API_VERSION = os.environ.get("AZURE_API_VERSION")


# A single stack to hold all our async contexts
exit_stack: AsyncExitStack = AsyncExitStack()

# setup the OpenAI Client
openai_client = AsyncAzureOpenAI(azure_endpoint=AZURE_ENDPOINT, api_key=AZURE_OPENAI_KEY, api_version=AZURE_API_VERSION)  # api_version must be 2025-03-01-preview or later to use responses API

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
            "name": tool.name,  
            "description": tool.description,  
            "parameters": tool.inputSchema,  
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

    # 1️⃣ First call – let the model decide on tools
    response = await openai_client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "user", "content": query}],
            tools=tools,
            tool_choice="auto",
        )

    #print(response.output)
    #print(f"Output text:  {response.output_text}")
    
    conversation = [{"role": "user", "content": query}] + response.output
    tool_calls = [e for e in response.output if e.type == "function_call"]
    
    # If there are no tool calls we’re done – pull out the text and return
    if not tool_calls:
        #print(f"AI decided that you DO NOT need tools")
        print(response.output_text)
        return response.output_text or ""
    
    # Execute every tool call from that first turn
    for tc in tool_calls:
        # Execute tool call
        print(f"AI decided that you need tool:  {tc.name} with args: {tc.arguments}")
        result = await session.call_tool(tc.name, arguments=json.loads(tc.arguments))
        conversation.append({
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": result.content[0].text,
        })


    prompt = await session.get_prompt("news", arguments={})
    instructions = prompt.messages[0].content.text
    
    #print(conversation)
    
    # ===== 3. Ask for the final answer (no more tools allowed) =====
    final_resp = await openai_client.responses.create(
            instructions=instructions,
            model="gpt-4o-mini",
            input=conversation,
            tool_choice="none",    # explicitly disallow further tool calls
            store=False,
        )

    print(f"Final Output:  {final_resp.output_text}")
    return final_resp.output_text


async def main():
    """Main entry point for the client."""
    
    url = "https://sports-mcp.orangeocean-ab857605.eastus2.azurecontainerapps.io/sse" # Joel work subscription
    #url = "https://mcp-server.redground-70426cdf.eastus2.azurecontainerapps.io/sse"
    #url="http://localhost:8000/sse"

    headers = {
        "x-api-key": "eff69e24c8f84195a522e7b5df8a0bbc"
    }  # api key this is to connect to the mcp server
    
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