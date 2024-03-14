import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import logging
import os

logging.basicConfig(filename='update.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_articles():
    url = 'https://blog.min.io/author/david-cannan'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').text.strip()
        summary = article.find('p', class_='excerpt').text.strip()
        date = article.find('time').text.strip()
        link = article.find('a', class_='article-link')['href']
        articles.append((title, 'David Cannan', summary, date, link))

    return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

def extract_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_content = soup.find('div', class_='article-content')
    
    if article_content:
        return article_content.get_text(separator='\n', strip=True)
    else:
        return None

def update_articles_md(new_articles_df):
    try:
        existing_articles_df = pd.read_csv('articles.md', sep='|', skiprows=1, names=['title', 'author', 'summary', 'date', 'url'])
    except FileNotFoundError:
        existing_articles_df = pd.DataFrame(columns=['title', 'author', 'summary', 'date', 'url'])

    # Check for new articles by comparing titles
    merged_df = pd.merge(new_articles_df, existing_articles_df, on="title", how="left", indicator=True)
    new_entries = merged_df[merged_df['_merge'] == 'left_only']

    if not new_entries.empty:
        # Update the markdown file
        with open('articles.md', 'w') as f:
            f.write("| Title | Author | Summary | Date | URL |\n")
            f.write("| ----- | ------ | ------- | ---- | --- |\n")
            existing_articles_df.to_csv(f, sep='|', index=False, header=False)
            new_entries[['title', 'author', 'summary', 'date', 'url']].to_csv(f, sep='|', index=False, header=False)

        logging.info(f"Added {len(new_entries)} new articles to articles.md")
        
        # Extract article content and generate individual markdown files
        if not os.path.exists('articles'):
            os.makedirs('articles')
        
        for _, row in new_entries.iterrows():
            article_content = extract_article_content(row['url'])
            if article_content:
                filename = f"{row['title'].replace(' ', '-').replace('/', '-')}.md"
                with open(f"articles/{filename}", 'w') as f:
                    f.write(f"# {row['title']}\n\n")
                    f.write(f"{article_content}\n")
                logging.info(f"Generated markdown file for article: {row['title']}")
            else:
                logging.warning(f"Failed to extract content for article: {row['title']}")
    else:
        logging.info("No new articles found")

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    logging.info(f"Running update job at {datetime.now(est)} EST")
    new_articles_df = fetch_articles()
    update_articles_md(new_articles_df)