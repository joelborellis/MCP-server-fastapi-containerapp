import argparse
import asyncio
import os
from dotenv import load_dotenv

from agents import Agent, HostedMCPTool, Runner, OpenAIResponsesModel
from openai import AsyncAzureOpenAI

"""This example demonstrates how to use the hosted MCP support in the OpenAI Responses API, with
approvals not required for any tools. You should only use this for trusted MCP servers."""

load_dotenv()

async def get_azure_openai_client():
    return AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    )

async def main(verbose: bool, stream: bool):
    
    azure_openai_client = await get_azure_openai_client()
    
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.  If there is no tool available, say 'I don't know'.",
        model=OpenAIResponsesModel(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_client=azure_openai_client,
        ),
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "sports",
                    "server_url": os.environ.get("MCP_URL"),
                    "require_approval": "never",
                }
            )
        ],
    )

    if stream:
        result = Runner.run_streamed(agent, "Show news for MLB?")
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"Got event of type {event.item.__class__.__name__}")
        print(f"Done streaming; final result: \n{result.final_output}")
    else:
        res = await Runner.run(agent, "Show news for MLB?")
        print(res.final_output)

    if verbose:
        for item in res.new_items:
            print(item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--stream", action="store_true", default=False)
    args = parser.parse_args()

    asyncio.run(main(args.verbose, args.stream))