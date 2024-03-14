import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os
import re
from minio import Minio
import weaviate
import tempfile
from unstructured.partition.auto import partition
import io

# Constants for Script 1
AUTHOR = 'David Cannan'
BLOG_URL = 'https://blog.min.io/author/david-cannan'

# Constants for Script 2
MINIO_ENDPOINT = "play.min.io:443"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
WEAVIATE_ENDPOINT = "http://localhost:8080"
BUCKET_NAME = "cda-datasets"

# Initialize Minio and Weaviate clients
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=True)
weaviate_client = weaviate.Client(url=WEAVIATE_ENDPOINT, timeout_config=(5, 15))

def fetch_and_parse_articles():
    response = requests.get(BLOG_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for article in soup.select('article.post-card'):
        title = article.find('h2').text.strip() if article.find('h2') else 'No Title Available'
        summary = article.select_one('.post__content').text.strip() if article.select_one('.post__content') else 'Summary not available'
        date = article.find('time').get('datetime', 'Date not available').strip() if article.find('time') else 'Date not available'
        article_link = article.select_one('a[href]')
        link = 'https://blog.min.io' + article_link['href'] if article_link else 'URL not available'
        articles.append((title, AUTHOR, summary, date, link))
    return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

def process_and_store_articles(articles_df):
    if not os.path.exists('articles'):
        os.makedirs('articles')

    for _, row in articles_df.iterrows():
        response = requests.get(row['url'])
        html_content = io.BytesIO(response.content)
        elements = partition(file=html_content, content_type="text/html")
        article_content = "\n".join([e.text for e in elements if hasattr(e, 'text')])
        
        filename = re.sub(r'[^\w\-_\.]', '_', row['title'])[:250] + '.md'
        with open(f'articles/{filename}', 'w') as f:
            f.write(f"# {row['title']}\n\n{article_content}\n")
        
        # Optional: Store in Minio and index in Weaviate
        # Similar process to Script 2 can be added here if necessary

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    process_and_store_articles(articles_df)