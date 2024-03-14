import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os

def fetch_and_parse_articles():
    url = 'https://blog.min.io/author/david-cannan'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for article in soup.select('article.post-card'):
        title = article.find('h2').text.strip()
        author = 'David Cannan'
        summary = article.select_one('div.post__content > p').text.strip() if article.select_one('div.post__content > p') else ''
        date = article.find('time').text.strip() if article.find('time') else ''
        link = article.find('a', class_='post__more')['href'] if article.find('a', class_='post__more') else ''
        articles.append((title, author, summary, date, link))

    return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

def extract_article_content(url):
    base_url = 'https://blog.min.io'
    full_url = base_url + url
    response = requests.get(full_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_content = soup.find('section', class_='post-full-content')
    
    if article_content:
        return article_content.get_text(separator='\n', strip=True)
    else:
        return None

def update_articles_md(new_articles_df):
    try:
        existing_articles_df = pd.read_csv('articles.md', sep='|', skiprows=1, names=['title', 'author', 'summary', 'date', 'url'])
    except FileNotFoundError:
        existing_articles_df = pd.DataFrame(columns=['title', 'author', 'summary', 'date', 'url'])

    merged_df = pd.merge(new_articles_df, existing_articles_df, on="title", how="left", indicator=True)
    new_entries = merged_df[merged_df['_merge'] == 'left_only']

    if not new_entries.empty:
        new_entries = new_entries.reindex(columns=['title', 'author', 'summary', 'date', 'url'], fill_value='')

        with open('articles.md', 'w') as f:
            f.write("| Title | Author | Summary | Date | URL |\n")
            f.write("| ----- | ------ | ------- | ---- | --- |\n")
            existing_articles_df.to_csv(f, sep='|', index=False, header=False)
            new_entries.to_csv(f, sep='|', index=False, header=False)

        print(f"Added {len(new_entries)} new articles to articles.md")
        
        if not os.path.exists('articles'):
            os.makedirs('articles')
        
        for _, row in new_entries.iterrows():
            article_content = extract_article_content(row['url'])
            if article_content:
                filename = f"{row['title'].replace(' ', '-').replace('/', '-')}.md"
                with open(f"articles/{filename}", 'w') as f:
                    f.write(f"# {row['title']}\n\n")
                    f.write(f"{article_content}\n")
                print(f"Generated markdown file for article: {row['title']}")
            else:
                print(f"Failed to extract content for article: {row['title']}")
    else:
        print("No new articles found")

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    new_articles_df = fetch_and_parse_articles()
    update_articles_md(new_articles_df)