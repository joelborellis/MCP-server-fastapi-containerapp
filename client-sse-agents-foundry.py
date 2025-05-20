import asyncio

import os
import sys
import logging
from azure.ai.projects.models import Agent
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
    )
logger = logging.getLogger("azure_agent_mcp")

# Global variables for client and agent cache
ai_client = None
agent_cache = {}
default_agent_id = os.getenv("DEFAULT_AGENT_ID")
credential = None


async def initialize_client():
    """Initialize the Azure AI Agent client asynchronously."""
    global ai_client, credential
    
    # Load environment variables
    project_connection_string = os.getenv("PROJECT_CONNECTION_STRING")
    
    # Validate essential environment variables
    if not project_connection_string:
        logger.error("Missing required environment variable: PROJECT_CONNECTION_STRING")
        return False

    try:
        credential = DefaultAzureCredential()
        
        ai_client = AIProjectClient.from_connection_string(
            credential=credential,
            conn_str=project_connection_string,
            user_agent="mcp-azure-ai-agent",
        )
        return True
    except Exception as e:
        logger.error(f"Failed to initialize AIProjectClient: {str(e)}")
        return False

async def get_agent(agent_id: str) -> Agent:
    """Get an agent by ID with simple caching."""
    global agent_cache

    # Check cache first
    if agent_id in agent_cache:
        return agent_cache[agent_id]

    # Fetch agent if not in cache
    try:
        agent = await ai_client.agents.get_agent(agent_id)
        #agent = await ai_client.agents.create_agent()
        agent_cache[agent_id] = agent
        return agent
    except Exception as e:
        logger.error(f"Agent retrieval failed - ID: {agent_id}, Error: {str(e)}")
        raise ValueError(f"Agent not found or inaccessible: {agent_id}")

async def main():
    server_initialized = await initialize_client()
    status = "successfully initialized" if server_initialized else "initialization failed"
    print(status)
    
    agent = await get_agent(agent_id=default_agent_id)
    print(agent.name)
    
    try:
        await ai_client.close()
        await credential.close()
    except Exception as e:
        logger.error(f"Failed to close session - Error: {str(e)}")
    

if __name__ == "__main__":
    asyncio.run(main())