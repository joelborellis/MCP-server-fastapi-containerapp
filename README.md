# MCP Server & Client - Azure Samples 

This repository showcases how to deploy an MCP (Model Context Protocol) server using Azure Container Apps. It also provides three example Agents—built with Autogen, Semantic Kernel, and the OpenAI Agent SDK—that demonstrate how to acccess the MCP server.


## Example MCP Server

Implements an SSE-based MCP server that exposes sports news tools (e.g., get latest NFL news) to clients. The server supports API key authentication and can be extended with additional tools or data sources. This server is implemented using fastmcp package and can be deployed locally or using Azure Container Apps. 


See [`server/README.md`](server/README.md) for setup and usage instructions for the server.

## Example Agents with MCP Clients

- **Autogen** 
- **OpenAI Agents SDK** 
- **Semantic Kernel**

See [`clients/README.md`](clients/README.md) for setup and usage instructions for each client.

