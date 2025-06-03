# filename: fetch_nhl_news_rss.py
import feedparser

def fetch_nhl_news_rss():
    url = "https://sports.yahoo.com/nhl/rss"  # Yahoo Sports NHL news RSS feed
    feed = feedparser.parse(url)
    
    if feed.bozo:
        print("Failed to parse feed:", feed.bozo_exception)
    else:
        if len(feed.entries) == 0:
            print("No news entries found.")
        else:
            for entry in feed.entries:
                print(entry.title)
                print(entry.link)
                print()

fetch_nhl_news_rss()