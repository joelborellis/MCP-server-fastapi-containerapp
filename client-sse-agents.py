import asyncio

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.  If there is no tool available, say 'I don't know'.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    # Use one of the sports tools, there is none for soccer so this should say it caan't find a tool
    message = "Show news for soccer"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Use one of the sports tools, it sould use get_nhl_news()
    message = "Show news for NHL"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerSse(
        name="SSE Container App Server",
        params={
            "url": "https://sports-mcp.orangeocean-ab857605.eastus2.azurecontainerapps.io/sse",
            "headers": {
                "x-api-key": "eff69e24c8f84195a522e7b5df8a0bbc"
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