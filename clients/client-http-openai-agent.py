import asyncio
import os

from agents import Agent, Runner, gen_trace_id, trace, OpenAIResponsesModel
from openai import AsyncAzureOpenAI
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from dotenv import load_dotenv

load_dotenv()

async def run(mcp_server: MCPServer, query: str):

    azure_openai_client = await get_azure_openai_client()

    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.  If there is no tool available, say 'I don't know'.",
        model=OpenAIResponsesModel(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_client=azure_openai_client,
        ),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use one of the sports tools
    message = query
    tool_calls = []
    print(f"\n\nRunning: {message}")
    result =  Runner.run_streamed(starting_agent=agent, input=message, max_turns=30)
    async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"Got event of type {event.item.__class__.__name__}")
                if hasattr(event.item, "raw_item") and hasattr(event.item.raw_item, "name"):
                    tool_name = event.item.raw_item.name
                    tool_calls.append(tool_name)
                    print(f"Tool called: {tool_name}")

    print(f"All tools called during run: {tool_calls}")
    print(f"Done streaming; final result: \n{result.final_output}")


async def get_azure_openai_client():
    return AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    )


async def main():
    async with MCPServerStreamableHttp(
        name="StreamableHttp Container App Server",
        params={
            "url": os.environ.get("MCP_URL"),
            "headers": {
                "x-api-key": os.environ.get("MCP_API_KEYS")
            },  # api key this is to connect to the mcp server
        },
    ) as server:
        while True:
            query = input("Enter your query (or press Enter to quit): ").strip()
            if not query or query.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            trace_id = gen_trace_id()
            with trace(workflow_name="MCP Container App Demo", trace_id=trace_id):
                print(
                    f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
                )
                await run(server, query)


if __name__ == "__main__":
    asyncio.run(main())