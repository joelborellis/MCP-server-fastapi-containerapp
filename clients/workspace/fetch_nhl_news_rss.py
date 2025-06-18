# filename: fetch_nhl_news_rss.py
import feedparser
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def fetch_nhl_news_rss():
    url = "https://sports.yahoo.com/nfl/news/rss/"  # Yahoo Sports NHL news RSS feed
    feed = feedparser.parse(url)

    if feed.bozo:
        print("Failed to parse feed:", feed.bozo_exception)
    else:
        if len(feed.entries) == 0:
            print("No news entries found.")
        else:
            with open("nhl_news_entries.txt", "w", encoding="utf-8") as file:
                for entry in feed.entries:
                    html = entry.content[0].value
                    soup = BeautifulSoup(html, "html.parser")
                    # Extract only the <p> tag content
                    #paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
                    paragraphs = [" ".join(p.stripped_strings) for p in soup.find_all("p")]

                    text = "\n".join(paragraphs)
                    file.write(str(entry.title) + "\n" + (entry.link) + "\n" + text + "\n\n")

fetch_nhl_news_rss()