from fastapi import FastAPI, Request, Depends
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from sports_mcp_server import mcp_sport_server
from api_key_auth import ensure_valid_api_key
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import argparse

app = FastAPI(docs_url=None, redoc_url=None, dependencies=[Depends(ensure_valid_api_key)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"] if you want to be strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        init_options = mcp_sport_server._mcp_server.create_initialization_options()

        await mcp_sport_server._mcp_server.run(
            read_stream,
            write_stream,
            init_options,
        )


        if __name__ == "__main__":
            parser = argparse.ArgumentParser(description="Start FastAPI server")
            parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
            parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
            args = parser.parse_args()

            uvicorn.run(app, host=args.host, port=args.port)