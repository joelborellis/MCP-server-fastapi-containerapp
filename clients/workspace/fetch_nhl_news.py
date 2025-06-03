# filename: fetch_nhl_news.py
import requests

def fetch_nhl_news():
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'NHL',
        'apiKey': 'YOUR_API_KEY',  # Replace with your NewsAPI key
        'pageSize': 5,              # Number of articles to fetch
        'sortBy': 'publishedAt'     # Sort articles by publication date
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']['name']}")
            print(f"Published At: {article['publishedAt']}")
            print(f"URL: {article['url']}\n")
    else:
        print("Failed to fetch news")

fetch_nhl_news()