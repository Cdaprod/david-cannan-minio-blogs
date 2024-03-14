import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os
import re

# Constants
AUTHOR = 'David Cannan'
BLOG_URL = 'https://blog.min.io/author/david-cannan'

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

def update_readme_and_store_articles(articles_df):
    if not os.path.exists('articles'):
        os.makedirs('articles')

    try:
        existing_articles_df = pd.read_csv('README.md', sep='|', skiprows=2, names=['title', 'author', 'summary', 'date', 'url'])
    except FileNotFoundError:
        existing_articles_df = pd.DataFrame(columns=['title', 'author', 'summary', 'date', 'url'])

    new_articles = pd.concat([articles_df, existing_articles_df]).drop_duplicates(subset=['title'], keep=False)
    
    if not new_articles.empty:
        with open('README.md', 'a') as f:  # Append new articles to README.md
            for _, row in new_articles.iterrows():
                f.write(f"| {row['title']} | {row['author']} | {row['summary']} | {row['date']} | [Link]({row['url']}) |\n")
                
                # Store article content in the /articles/ directory
                response = requests.get(row['url'])
                article_content = BeautifulSoup(response.content, 'html.parser').get_text()
                filename = f"{re.sub(r'[^\\w\\-]', '_', row['title'])[:250]}.md"
                with open(f'articles/{filename}', 'w') as article_file:
                    article_file.write(f"# {row['title']}\n\n{article_content}\n")
        
        print(f"Added {len(new_articles)} new articles to README.md and /articles/ directory.")
    else:
        print("No new articles found.")

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    update_readme_and_store_articles(articles_df)