# Azure MCP Sample - Server

This README provides instructions and details for the server-side code in the `server/` directory.

## Files
- `sports_mcp_server.py`: Main MCP server implementation for sports news.
- `start_server_http.py`: Script to start the MCP server.
- `api_key_auth.py`: API key authentication for the server.
- `prompts/news.md`: Prompt template for news responses.

## Setup


## Running the Server


### Deploying Locally
1. Copy `sample.env` to `.env` from the root of the project and fill in your server configuration:
   ```bash
   cp sample.env .env
   # Edit .env to add your API keys and other settings
   ```
2. Install dependencies using uv (Only need to do this once and from the root directory of the project, NOT in the server directory):
   ```bash
   uv sync
   ```

3. Start the server with:
   ```bash
   uv run fastapi dev start_server_http.py
   ```


### ☁️ Deploying as an Azure Container App

The easiest way to deploy to Azure is by using the Azure CLI command `az containerapp up`.
See: [Get started with Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/get-started?tabs=bash)

```bash
   az login --tenant YOUR_TENANT_ID
   sh deploy_server_aca_ssh.sh
```

Check the output message to get the MCP Server's KEY and URL. 


## Notes
- The server must be running before clients can connect.
- Use the client-http-test.py to test the connection
- Ensure your `.env` file is properly configured with Azure OpenAI endpoint and MCP Server info and other variables.

For more details, see comments and docstrings in each server script.
