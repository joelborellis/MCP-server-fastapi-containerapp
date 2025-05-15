# MCP Client/Server Demo with OpenAI Models

This repository contains both a client and server to demonstrate how to use an MCP (Model Context Protocol) client/server setup with OpenAI models.

---

## 🔍 Overview

- **Server**  
  - Exposes several tools that call ESPN APIs to fetch the latest news for NFL, NBA, College Football, NHL, and MLB.  
  - Hosts an `@mcp.prompt` template (a Markdown file in `prompts/`) which the client can retrieve and use as instructions for the final output.  
  - Built using Anthropic Python SDK and FastMCP, wrapped in a FastAPI app that serves SSE (Server-Sent Events).  
  - Deploys via `main.py` as an Azure Container App.

- **Client**  
  - Uses the Anthropic SDK’s `sse_client` to connect to the server.  
  - Can list available resources, fetch prompts, and invoke tools over SSE.
  - Is a basic chatbot that calls the MCP server tools based on the determination of tool use by an LLM

---

## ⚙️ Features

1. **Remote MCP server** running as an Azure Container App  
2. **Tool invocation** for real-time sports news via ESPN APIs  
3. **Prompt templating** with an editable Markdown prompt  
4. **SSE transport** between client and server  
5. **Protected endpoints** via a simple API key scheme  
5. **Responses API** using the Reaponses API to call LLM  

---

## 📦 Prerequisites

- Python 3.9+  
- [uv](https://pypi.org/project/uv/) (for task management)  
- An OpenAI API key  
- Azure CLI (for container app deployment)

---

## Getting Started

1. **Clone the repo**

   ```bash
   git clone https://github.com/joelborellis/MCP-server-fastapi-containerapp
   ```

2. **Install dependencies**

   ```bash
   cd MCP-server-fastapi-containerapp
   uv sync
   ```

   This will install the Python packages specified in `pyproject.toml`.

3. **Local testing**

   * Start the FastAPI (uvicorn) server locally:

     ```bash
     uv run fastapi dev main.py
     ```
   * Edit the `client-sse-llm.py` file and ensure the URL points to:

     ```text
     http://localhost:8000/sse
     ```
   * Run the client script:

     ```bash
     python client-sse-llm.py
     ```

## ☁️ Deploying as an Azure Container App

The easiest way to deploy to Azure is by using the Azure CLI command `az containerapp up`.
See: [Get started with Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/get-started?tabs=bash)

### Option 1: Deploy from local code

```bash
az containerapp up \
  -g <YOUR_RESOURCE_GROUP> \
  -n <APP_NAME> \
  --environment <ENV_NAME> \
  -l <REGION> \
  --env-vars API_KEYS=<YOUR_API_KEY> \
  --source .
```

### Option 2: Deploy from a container registry

1. Build a Docker image using the included `Dockerfile` and push it to your container registry.
2. Deploy:

   ```bash
   az containerapp up \
     -g <YOUR_RESOURCE_GROUP> \
     -n <APP_NAME> \
     --environment <ENV_NAME> \
     -l <REGION> \
     --env-vars API_KEYS=<YOUR_API_KEY> \
     --image <YOUR_REGISTRY>/<IMAGE_NAME>:<TAG>
   ```

> **Note:** After deployment, you may need to enable external ingress:
>
> ```bash
> az containerapp ingress enable \
>   -n <APP_NAME> \
>   -g <YOUR_RESOURCE_GROUP> \
>   --type external \
>   --target-port 8000 \
>   --transport auto
> ```

## 🎯 Usage Examples

- show me all the sports news
- show me all the latest news for the NFL


# Sports News MCP Server

A minimal FastMCP (Model Context Protocol) server that fetches the latest sports news from ESPN and exposes them as callable tools. Built with FastAPI, `httpx` for async HTTP requests, and the Anthropic Python SDK’s MCP support.

---

## 📋 Contents

- [`sports.py`](#sportspy) – The main MCP server implementation  
- [`prompts/news.md`](#prompt-template) – Markdown template that can be used as instructions to the LLM for final response  

---

## 🏗️ Architecture

1. **FastMCP Server**  
   - Instantiated as `mcp = FastMCP("sports")`.  
   - Exposes one prompt (`@mcp.prompt`) and multiple tools (`@mcp.tool`).

2. **Tools**  
   - `get_cfb_news()`, `get_nfl_news()`, `get_mlb_news()`, `get_nhl_news()`, `get_nba_news()`  
   - Each tool makes an HTTP GET to the appropriate ESPN API endpoint, formats the returned articles, and joins them with separators.

3. **Prompt**  
   - `news()` reads a Markdown file (`prompts/news.md`) and returns its contents as the “news” prompt template.

4. **Transport**  
   - When run directly (`python sports.py`), the server listens on **stdio** for MCP-over-SSE (Server-Sent Events) requests.

---

# FastMCP SSE Server (`main.py`)

A FastAPI-based container application that exposes an MCP (Model Context Protocol) server over Server-Sent Events (SSE), wrapping the `sports` MCP instance behind API-key authentication and CORS middleware.

---

## 📑 Overview

- **Framework**: FastAPI  
- **Transport**: SSE (via `mcp.server.sse.SseServerTransport`)  
- **Auth**: API-key validation on every request  
- **CORS**: Enabled for all origins (customizable)  
- **MCP Instance**: Imported from `sports.py` as `mcp`  
- **Mount Path**: `/messages` for POST messages  
- **SSE Endpoint**: `/sse` for streaming MCP messages  

---

## 🚀 Features

1. **API-Key Protection**  
   - All routes depend on the `ensure_valid_api_key` dependency.  
   - Invalid or missing API-keys result in a `401 Unauthorized`.

2. **CORS Middleware**  
   - Allows cross-origin requests from any origin by default.  
   - Restrict via `allow_origins=[…]` as needed.

3. **SSE Transport**  
   - Mounts a POST handler at `/messages` for client → server tool calls.  
   - Streams MCP responses back to clients on the `/sse` GET endpoint.

4. **FastMCP Integration**  
   - Uses the `mcp` object from `sports.py` (which defines prompts and tools).  
   - Automatically initializes MCP options and runs the server loop per connection.

---

# SSE LLM Client (`client-sse-llm.py`)

An asynchronous Python client that connects to an MCP (Message-Centric Protocol) server over Server-Sent Events (SSE), lets GPT-4o decide which tools to call, executes those tools on the server, and then asks GPT-4.1 for a final answer using a retrieved prompt template.

---

## 📋 Contents

- [`client-sse-llm.py`](#client-sse-llmpy) — Main client script  
- MCP server required (e.g. `sports.py` + FastAPI wrapper)  
- Valid API key for SSE handshake  

---

## 🔍 Overview

1. **Connect to MCP server via SSE**  
   - Uses `sse_client()` to open bidirectional streams.  
   - Wraps streams in an `mcp.ClientSession`.

2. **Retrieve available tools**  
   - Calls `session.list_tools()` to get metadata for each MCP tool.

3. **Two-step LLM interaction**  
   1. **Tool-selection call**:  
      - Sends user query to `openai.responses.create(model="gpt-4o", …, tools=…)`.  
      - GPT-4o may return zero or more `function_call` events.  
   2. **Tool execution**:  
      - For each `function_call`, invokes `session.call_tool(name, args)` on the MCP server.  
      - Appends tool outputs to the conversation.  
   3. **Final answer call**:  
      - Fetches a Markdown prompt template from the server (`session.get_prompt("news")`).  
      - Sends the accumulated conversation + prompt instructions to `openai.responses.create(model="gpt-4.1-mini", tool_choice="none")`.  
      - Prints the final LLM answer.

4. **Interactive REPL loop**  
   - Prompts the user for queries.  
   - Handles `quit`/`exit`.  
   - Gracefully shuts down streams on exit.

---