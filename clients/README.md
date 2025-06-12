# Azure MCP Sample - Clients

This README provides instructions and details for the client-side scripts in the `clients/` directory.

## Available Clients

- `client-http-test.py`: Simple test to connect to the container app/MCP server and list the tools and call one tool.
- `client-http-openai-agent.py`: Uses OpenAI Agents SDK with MCP tool and Azure OpenAI.
- `client-http-openai-hosted.py`: Uses OpenAI Agents SDK with MCP tool but uses the HostedMCPTool and Azure OpenAI.
- `client-http-responses.py`: Uses the OpenAI responses API and MCP - uses OpenAI model directly.
- `client-http-sk.py`: Uses Semantic Kernel with MCP tool and Azure OpenAI.
- `client-http-autogen.py`: Uses Autogen with MCP tool and Azure OpenAI [Work in Progress]

## Setup

1. Copy `sample.env` to `.env` at the root of this project and fill in your credentials:
   ```cp sample.env .env
   # Edit .env to add your Azure-OpenAI/MCP-Server keys and endpoints
   ```
2. Install dependencies using uv (Only need to do this once and from the root directory of the project, NOT in the clients directory):
   ```uv sync```

## Running a Client

Example (Semantic Kernel client):
```bash
uv run python client-sse-sk-agent.py
```

## Notes
- Ensure the MCP server is running before starting a client. 

For more details, see the comments and docstrings in each client script.
