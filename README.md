# MCP Server & Client on Azure

This repository demonstrates how to use Azure Container Apps & Azure OpenAI to build MCP (Model Context Protocol) server and client components.


## Example Server

Implements an SSE-based MCP server that exposes sports news tools (e.g., get latest NFL news) to clients. The server supports API key authentication and can be extended with additional tools or data sources. This server is implemented using fastmcp package and can be deployed locally or using Azure Container Apps. 


See [`server/README.md`](server/README.md) for setup and usage instructions for the server.

## Example Clients

- **Autogen**: Uses [Autogen](https://github.com/microsoft/autogen) agents with the MCP tool and Azure OpenAI as the LLM backend. 
- **OpenAi Agents SDK**: Uses the OpenAI Agents SDK with the MCP tool and Azure OpenAI. 
- **Semantic Kernel**: Uses [Semantic Kernel](https://github.com/microsoft/semantic-kernel) with the MCP tool and Azure OpenAI.

See [`clients/README.md`](clients/README.md) for setup and usage instructions for each client.

