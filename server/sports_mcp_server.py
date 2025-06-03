from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json

# Initialize FastMCP server
mcp_sport_server = FastMCP("sports", streamable_http=True, debug=True)

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

# Define prompts
@mcp_sport_server.prompt()
def news() -> str:
    """Global instructions for News"""
    with open("prompts/news.md", "r") as file:
        template = file.read()
    return template

@mcp_sport_server.tool()
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

@mcp_sport_server.tool()
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

@mcp_sport_server.tool()
async def get_mlb_news() -> str:
    """Get news articles for Baseball (MLB).

    Args:
        NONE
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/baseball/mlb/news"
    data = await make_espn_request(url)
    
    if not data or data.get("articles", []) is None:
        return "Unable to fetch articles or no articles found."

    news = [format_alert(article) for article in data.get("articles", [])]
    return "\n---\n".join(news)

@mcp_sport_server.tool()
async def get_nhl_news() -> str:
    """Get news articles for Hockey (NHL).

    Args:
        NONE
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/hockey/nhl/news"
    data = await make_espn_request(url)
    
    if not data or data.get("articles", []) is None:
        return "Unable to fetch articles or no articles found."

    news = [format_alert(article) for article in data.get("articles", [])]
    return "\n---\n".join(news)

@mcp_sport_server.tool()
async def get_nhl_team_info(team: str) -> str:
    """Get information about a specific NHL team.

    Args:
        team - The NHL team name to get information about.
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/hockey/nhl/teams/toronto"
    data = await make_espn_request(url)
    
    if not data or data.get("team", []) is None:
        return "Unable to fetch articles or no articles found."

    info = json.dumps(data.get("team", []), indent=4)
    print(f"Team info:  {info}")
    return "\n---\n".join(info)

@mcp_sport_server.tool()
async def get_nba_news() -> str:
    """Get news articles for Basketball (NBA).

    Args:
        NONE
    """
    url = f"{ESPN_API_BASE}/apis/site/v2/sports/basketball/nba/news"
    data = await make_espn_request(url)
    
    if not data or data.get("articles", []) is None:
        return "Unable to fetch articles or no articles found."

    news = [format_alert(article) for article in data.get("articles", [])]
    return "\n---\n".join(news)

if __name__ == "__main__":
    # Initialize and run the server
    mcp_sport_server.run(transport='streamable-http')