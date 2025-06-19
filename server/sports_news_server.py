from typing import Any
from mcp.server.fastmcp import FastMCP
import feedparser
from bs4 import BeautifulSoup

# Initialize FastMCP server
sports_news_server = FastMCP("sports", stateless_http=True, debug=True)

# Constants
YAHOO_API_BASE = "https://sports.yahoo.com/"
USER_AGENT = "sports-app/1.0"


async def make_yahoo_request(url: str) -> dict[str, Any] | None:
    """Make a request to Yahoo Sports rss feed with proper error handling."""
    feed = feedparser.parse(url)

    if feed.bozo:
        print("Failed to parse feed:", feed.bozo_exception)
    else:
        if len(feed.entries) == 0:
            print("No news entries found.")
        else:
            return feed


def format_alert(news: dict) -> str:
    """Format news to a readable string."""
    return f"""
        Type: {news.get("type")}
        Headline: {news.get("headline")}
        Description: {news.get("description")}
        Link: {news.get("links", {}).get("web", "No link available").get("href", "No link available")}
        """


def format_alert_yahoo(entry: dict) -> str:
    """Format news to a readable string."""
    html = entry.content[0].value
    soup = BeautifulSoup(html, "html.parser")
    # Extract only the <p> tag content
    #paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    paragraphs = [" ".join(p.stripped_strings) for p in soup.find_all("p")]
    content = "\n".join(paragraphs)
    
    source_name = getattr(entry.source, "title", None) if entry.source else "Unknown"
        
    return f"""
        Type: "RSS Feed"
        Headline: {entry.title}
        Description: {entry.description}
        Link: {entry.link}
        Content: {content}
        Published: {entry.published}
        Source: {source_name}
        """


# Define prompts
@sports_news_server.prompt()
def news() -> str:
    """Global instructions for News"""
    with open("prompts/prompt.xml", "r") as file:
        template = file.read()
    return template


@sports_news_server.tool()
async def get_cfb_news() -> str:
    """Get news articles for college (NCAA) football.

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/college-football/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)


@sports_news_server.tool()
async def get_nfl_news() -> str:
    """Get news articles for the National Football League (NFL).

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/nfl/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)


@sports_news_server.tool()
async def get_mlb_news() -> str:
    """Get news articles for Baseball (MLB).

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/mlb/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)


@sports_news_server.tool()
async def get_nhl_news() -> str:
    """Get news articles for Hockey (NHL).

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/nhl/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)



@sports_news_server.tool()
async def get_nba_news() -> str:
    """Get news articles for Basketball (NBA).

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/nba/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)

@sports_news_server.tool()
async def get_nascar_news() -> str:
    """Get news articles for Nascar racing.

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/nascar/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)

@sports_news_server.tool()
async def get_golf_news() -> str:
    """Get news articles for the Pro Golfers Association (PGA).

    Args:
        NONE
    """
    url = f"{YAHOO_API_BASE}/golf/rss/"
    feed = await make_yahoo_request(url)

    if not feed:
        return "Unable to fetch articles or no articles found."

    entries = [format_alert_yahoo(entry) for entry in feed.entries]
    return "\n---\n".join(entries)

if __name__ == "__main__":
    # Initialize and run the server
    sports_news_server.run(transport="streamable-http")