import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.mcp import MCPSsePlugin, MCPStreamableHttpPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.streaming_chat_message_content import StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

async def main():
    # Load environment variables from .env file
    current_dir = Path(__file__).parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Initialize the kernel
    kernel = Kernel()
    
    # Add an Azure OpenAI service with function calling enabled
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_API_VERSION")
    
    chat_service = AzureChatCompletion(
        service_id="azure_openai",
        api_key=AZURE_OPENAI_API_KEY,
        deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
        endpoint=AZURE_OPENAI_ENDPOINT
    )
    kernel.add_service(chat_service)
    
    # api key this is to connect to the mcp server
    # Configure and use the MCP plugin using SSE via async context manager
    async with MCPStreamableHttpPlugin(
        name="sport_news_server",
        url=os.getenv("MCP_URL"),  # URL where the MCP SSE server is listening
        headers={"x-api-key": os.getenv("MCP_API_KEYS")}
    ) as mcp_plugin:
        # Register the MCP plugin with the kernel after connecting
        try:
            kernel.add_plugin(mcp_plugin, plugin_name="sport_news_server")
        except Exception as e:
            print(f"Error: Could not register the MCP plugin: {str(e)}")
            return
        
        
        settings = OpenAIChatPromptExecutionSettings()
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        # Create a chat history with system instructions
        history = ChatHistory()
        history.add_system_message(
            "You are a sport news assistant. "
        )
        
        # Define a simple chat function
        chat_function = kernel.add_function(
            plugin_name="chat",
            function_name="respond", 
            prompt="{{$chat_history}}"
        )
        
        # Add the user message to history
        history.add_user_message("latest news for NFL")
        
        # Prepare arguments with history and settings
        arguments = KernelArguments(
            chat_history=history,
            settings=settings
        )
            
        try:
            # Stream the response
            response_chunks = []
            async for message in kernel.invoke_stream(
                chat_function,
                arguments=arguments
            ):
                chunk = message[0]
                if isinstance(chunk, StreamingChatMessageContent) and chunk.role == AuthorRole.ASSISTANT:
                    print(str(chunk), end="", flush=True)
                    response_chunks.append(chunk)
    
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Make sure the MCP SSE server")

if __name__ == "__main__":
    asyncio.run(main())