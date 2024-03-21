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
        date = article.find('time')['datetime'].strip() if article.find('time') else 'Date not available'
        link = article.select_one('a[href]')['href'] if article.select_one('a[href]') else 'URL not available'
        articles.append({"title": title, "author": AUTHOR, "summary": summary, "date": date, "url": link})

    df = pd.DataFrame(articles)
    df['index'] = range(len(df), 0, -1)  # Add a reverse index starting from the total number of articles
    return df

def sanitize_title(title):
    return re.sub(r'[^\w\-]', '_', title)[:250]

def ensure_absolute_url(url):
    if url.startswith('http'):
        return url
    return 'https://blog.min.io' + url

def update_readme_and_articles(articles_df):
    if not os.path.exists('articles'):
        os.makedirs('articles')

    existing_urls = []
    if os.path.exists('README.md'):
        with open('README.md', 'r') as f:
            existing_urls = re.findall(r'\[Link\]\((https?://.*?)\)', f.read())

    articles_df['is_new'] = ~articles_df['url'].isin(existing_urls)
    
    # Update README.md
    with open('README.md', 'w') as f:
        f.write("# David Cannan's MinIO Publications\n\n")
        f.write("| No. | Title | Author | Summary | Date | Link |\n")
        f.write("|-----|-------|--------|---------|------|------|\n")
        for index, row in articles_df.iterrows():
            f.write(f"| {row['index']} | {row['title']} | {row['author']} | {row['summary']} | {row['date']} | [Link]({ensure_absolute_url(row['url'])}) |\n")

            if row['is_new']:
                # Ensure the URL is absolute before making a request
                absolute_url = ensure_absolute_url(row['url'])
                response = requests.get(absolute_url)
                article_content = BeautifulSoup(response.content, 'html.parser').select_one('article').get_text(separator="\n", strip=True) if BeautifulSoup(response.content, 'html.parser').select_one('article') else 'Content not found'
                filename = f"articles/{sanitize_title(row['title'])}.md"
                with open(filename, 'w') as article_file:
                    article_file.write(f"# {row['title']}\n\n{article_content}\n")

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    update_readme_and_articles(articles_df)