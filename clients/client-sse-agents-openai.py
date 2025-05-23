import asyncio
import os

from agents import Agent, Runner, gen_trace_id, trace, OpenAIChatCompletionsModel
from openai import AsyncAzureOpenAI
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv

load_dotenv(".env")

async def get_azure_openai_client():
    return AsyncAzureOpenAI(api_key=os.getenv("AZURE_OPENAI_KEY"), api_version=os.getenv("AZURE_API_VERSION"), azure_endpoint=os.getenv("AZURE_ENDPOINT"))

async def run(mcp_server: MCPServer):
    
    azure_openai_client = await get_azure_openai_client()
    
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.  If there is no tool available, say 'I don't know'.",
        model=OpenAIChatCompletionsModel(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), openai_client=azure_openai_client),
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use one of the sports tools, it sould use get_nhl_news()
    message = "Show news for NHL"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerSse(
        name="SSE Container App Server",
        params={
            "url": os.getenv("MCP_URL"),
            "headers": {
                "x-api-key": os.getenv("MCP_API_KEYS")
            },  # api key this is to connect to the mcp server
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="MCP Container App Demo", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )
            await run(server)


if __name__ == "__main__":
    asyncio.run(main())