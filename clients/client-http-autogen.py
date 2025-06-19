import asyncio
import os

from dotenv import load_dotenv
from autogen_ext.tools.mcp import mcp_server_tools, StreamableHttpServerParams
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

# Create Rich console for Markdown rendering
console = Console()

async def main():
    # Define server parameters
    news_server_params = StreamableHttpServerParams(
        url=os.getenv("MCP_URL"),
        headers={
            "x-api-key": os.getenv("MCP_API_KEYS")
        }
    )

    # Initialize the MCP tool adapter
    mcp_news_server_tools = await mcp_server_tools(news_server_params)
    print(f"Tools: {[tool.name for tool in mcp_news_server_tools]}")

    # Initialize the Azure OpenAI client
    AZURE_OPENAI_KEY=os.getenv("AZURE_OPENAI_KEY")
    AZURE_API_VERSION=os.getenv("AZURE_API_VERSION")
    AZURE_ENDPOINT=os.getenv("AZURE_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    az_model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_OPENAI_KEY, # For key-based authentication.
        )

    # Create the agent
    # # The system message instructs the agent via natural language.
    agent = AssistantAgent(
        name="sport_news_agent",
        model_client=az_model_client,
        tools=mcp_news_server_tools,
        system_message="You are a helpful assistant.",
        reflect_on_tool_use=True,
        model_client_stream=True,  # Enable streaming tokens from the model client.
    )


    result = await agent.run(task="get NFL news")
    
    # Render the content as Markdown
    md = Markdown(result.messages[-1].content)
    console.print(md)
    print()  # Add an extra line for readability


if __name__ == "__main__":
    asyncio.run(main())