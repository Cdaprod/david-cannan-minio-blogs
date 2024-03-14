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

def sanitize_title(title):
    return re.sub(r'[^\w\-]', '_', title)[:250]

def update_readme_and_store_articles(articles_df):
    if not os.path.exists('articles'):
        os.makedirs('articles')

    # Attempt to load the existing README.md content
    try:
        with open('README.md', 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    # Convert existing README content to a DataFrame for easier comparison
    existing_urls = set(re.findall(r'\[Link\]\((.*?)\)', existing_content))

    # Filter new articles by checking if URL is not in existing URLs
    new_articles = articles_df[~articles_df['url'].isin(existing_urls)]

    if not new_articles.empty:
        # Append new articles to the README.md file
        with open('README.md', 'a') as f:
            for _, row in new_articles.iterrows():
                f.write(f"| {row['title']} | {row['author']} | {row['summary']} | {row['date']} | [Link]({row['url']}) |\n")

        # Save individual article content to /articles directory
        for _, row in new_articles.iterrows():
            # Skip fetching content if URL is invalid (e.g., 'nan' or missing scheme)
            if pd.isna(row['url']) or not re.match(r'^https?:\/\/', row['url']):
                print(f"Skipping invalid URL for article: {row['title']}")
                continue

            response = requests.get(row['url'])
            article_content = BeautifulSoup(response.content, 'html.parser').select_one('article').get_text(separator="\n", strip=True) if BeautifulSoup(response.content, 'html.parser').select_one('article') else 'Content not found'
            sanitized_title = sanitize_title(row['title'])
            filename = f"articles/{sanitized_title}.md"

            # Check if file already exists to avoid duplicates
            if not os.path.exists(filename):
                with open(filename, 'w') as article_file:
                    article_file.write(f"# {row['title']}\n\n{article_content}\n")

        print(f"Added {len(new_articles)} new articles to README.md and /articles/ directory.")
    else:
        print("No new articles found.")

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    update_readme_and_store_articles(articles_df)