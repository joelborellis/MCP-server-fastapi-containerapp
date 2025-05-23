# Azure MCP Sample - Server

This README provides instructions and details for the server-side code in the `server/` directory.

## Files
- `sports_mcp_server.py`: Main MCP server implementation for sports news.
- `start_server.py`: Script to start the MCP server.
- `api_key_auth.py`: API key authentication for the server.
- `prompts/news.md`: Prompt template for news responses.
- `sample.env`: Example environment file for server configuration.

## Setup

1. Copy `sample.env` to `.env` and fill in your server configuration:
   ```bash
   cp sample.env .env
   # Edit .env to add your API keys and other settings
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the server with:
```bash
uv run fastapi dev start_server.py
```

## Notes
- The server must be running before clients can connect.
- Ensure your `.env` file is properly configured.

For more details, see comments and docstrings in each server script.
