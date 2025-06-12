from openai import AsyncOpenAI, RateLimitError
from dotenv import load_dotenv
import os
from halo import Halo
import asyncio
import backoff
import time

load_dotenv()

# setup the OpenAI Client
client = AsyncOpenAI()

# Azure OpenAI variables from .env file
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")


def open_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as infile:
        return infile.read()


###  OpenAI chat completions call with backoff for rate limits
@backoff.on_exception(backoff.expo, RateLimitError)
async def chat(**kwargs):
    try:
        spinner = Halo(text="Calling responses API...", spinner="dots")
        spinner.start()
        # print(kwargs)

        start_time = time.time()  # Record the start time
        response = await client.responses.create(**kwargs)

        end_time = time.time()  # Record the end time

        elapsed_time = end_time - start_time  # Calculate the elapsed time in seconds
        minutes, seconds = divmod(
            elapsed_time, 60
        )  # Convert seconds to minutes and seconds
        formatted_time = (
            f"{int(minutes)} minutes and {seconds:.2f} seconds"  # Format the time
        )

        response_id = response.id
        text = response.output_text
        model = response.model
        tokens = response.usage  # get the usage details

        spinner.stop()

        return response_id, text, model, tokens, formatted_time
    except Exception as yikes:
        print(f'\n\nError communicating with OpenAI: "{yikes}"')
        exit(0)


async def main():
    response_id = ""
    while True:
        # Get user query
        query = input(f"\nAsk Responses API (using model: {OPENAI_MODEL}): ")
        if query.lower() == "exit":
            exit(0)

        # Create conversation
        conversation = list()
        conversation.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": query}],
            }
        )

        tools = [
            {
                "type": "mcp",
                "server_label": "sports",
                "server_url": "https://sports-mcp.blackisland-e262cc09.eastus2.azurecontainerapps.io/mcp/",
                "require_approval": "never",
                "headers": {"x-api-key": "eff69e24c8f84195a522e7b5df8a0bbc"},
            }
        ]

        # Build the kwargs for the chat call
        chat_kwargs = {
            "input": conversation,
            "model": OPENAI_MODEL,
            "instructions": "Use the tools to answer the questions.  If there is no tool available, say 'I don't know'.",
            "tools": tools,
            "tool_choice": "auto",
        }

        # Only include previous_response_id if we already have a valid one
        if response_id:
            chat_kwargs["previous_response_id"] = response_id

        response_id, text, model, tokens, formatted_time = await chat(**chat_kwargs)

        print(f"{text}\n")
        print(f"Model used: {model}")
        print(f"Your question took a total of: {tokens.total_tokens} tokens")
        print(
            f"Your question took: {tokens.output_tokens_details.reasoning_tokens} reasoning tokens"
        )
        print(f"Your question prompt used: {tokens.input_tokens}")
        print(f"Time elapsed: {formatted_time}")


if __name__ == "__main__":
    asyncio.run(main())