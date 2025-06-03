# Azure MCP Sample - Clients

This README provides instructions and details for the client-side scripts in the `clients/` directory.

## Available Clients

- `client-sse-agents-autogen.py`: Uses Autogen agents with MCP tool and Azure OpenAI.
- `client-sse-agents-openai.py`: Uses OpenAI Agents SDK with MCP tool and Azure OpenAI.
- `client-sse-sk-agent.py`: Uses Semantic Kernel with MCP tool and Azure OpenAI.

## Setup

1. Copy `sample.env` to `.env` and fill in your credentials:
   ```bash
   cp sample.env .env
   # Edit .env to add your Azure-OpenAI/MCP-Server keys and endpoints
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running a Client

Example (Semantic Kernel client):
```bash
python client-sse-sk-agent.py
```

## Notes
- Ensure the MCP server is running before starting a client.

For more details, see the comments and docstrings in each client script.
