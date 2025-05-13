from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("sports")

# Constants
ESPN_API_BASE = "https://site.api.espn.com"
USER_AGENT = "sports-app/1.0"

async def make_espn_request(url: str) -> dict[str, Any] | None:
    """Make a request to ESPN API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(news: dict) -> str:
    """Format news to a readable string."""
    return f"""
        Type: {news.get("type")}
        Headline: {news.get("headline")}
        Description: {news.get("description")}
        Link: {news.get("links", {}).get("web", "No link available").get("href", "No link available")}
        """

@mcp.tool()
async def get_cfb_news() -> str:
    """Get news articles for college (NCAA) football.

    Args:
        NONE
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/football/college-football/news"
    data = await make_espn_request(url)
    
    if not data or data.get("articles", []) is None:
        return "Unable to fetch articles or no articles found."

    news = [format_alert(article) for article in data.get("articles", [])]
    return "\n---\n".join(news)

@mcp.tool()
async def get_nfl_news() -> str:
    """Get news articles for the National Football League (NFL).

    Args:
        NONE
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/football/nfl/news"
    data = await make_espn_request(url)
    
    if not data or data.get("articles", []) is None:
        return "Unable to fetch articles or no articles found."

    news = [format_alert(article) for article in data.get("articles", [])]
    return "\n---\n".join(news)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')