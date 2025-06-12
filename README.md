# MCP Server & Client - Azure Samples 

This repository showcases how to deploy an MCP (Model Context Protocol) server using Azure Container Apps. It also provides example Agents—built with Autogen, Semantic Kernel, and the OpenAI Agent SDK—that demonstrate how to acccess the MCP server as a Host/Client.


## Example MCP Server

Implements a Streamable-Http MCP server that exposes sports news tools (e.g., get latest NFL news) to clients. The server supports API key authentication and can be extended with additional tools or data sources. This server is implemented using FastMCP package and can be deployed locally or using Azure Container Apps. 

Use uv as the package manager for this project.

## uv Setup
- Install uv - https://docs.astral.sh/uv/  The hyper modern Python package manager.
- Setup environment cp .env.sample .env fill in your environment variables.
- Install dependencies (read from pyproject.toml file) ```uv sync```

See [`server/README.md`](server/README.md) for setup and usage instructions for the server.

## Example Agents with MCP Clients

- **Autogen** 
- **OpenAI Agents SDK** 
- **Semantic Kernel**
- **Responses API**

See [`clients/README.md`](clients/README.md) for setup and usage instructions for each client.

