import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os

# def fetch_and_parse_articles():
#     url = 'https://blog.min.io/author/david-cannan'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     articles = []
#     for article in soup.select('article.post-card'):
#         title = article.find('h2').text.strip()
#         author = 'David Cannan'
#         summary = article.select_one('div.post__content > p').text.strip() if article.select_one('div.post__content > p') else ''
#         date = article.find('time').text.strip() if article.find('time') else ''
        
#         title_link = article.find('h2').find('a')
#         link = title_link['href'] if title_link else ''
        
#         articles.append((title, author, summary, date, link))

#     return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

# def fetch_and_parse_articles():
#     url = 'https://blog.min.io/author/david-cannan'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     articles = []
#     for article in soup.select('article.post-card'):
#         title = article.find('h2').text.strip()
#         author = 'David Cannan'
#         summary = article.select_one('div.post__content > p').text.strip() if article.select_one('div.post__content > p') else ''
#         date = article.find('time').text.strip() if article.find('time') else ''
        
#         article_link = article.select_one('a.post__more')
#         link = article_link['href'] if article_link else ''
        
#         articles.append((title, author, summary, date, link))

#     return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

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
        
        article_link = article.select_one('a.post__img')
        link = article_link['href'] if article_link else ''
        
        articles.append((title, author, summary, date, link))

    return pd.DataFrame(articles, columns=['title', 'author', 'summary', 'date', 'url'])

def extract_article_content(url):
    if not url:
        print("Empty URL. Skipping article content extraction.")
        return None
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = soup.select_one('section.post__content')
        
        if article_content:
            # Remove navigation elements
            nav_elements = article_content.select('div.post__nav')
            for nav in nav_elements:
                nav.decompose()
            
            return article_content.get_text(separator='\n', strip=True)
        else:
            print(f"Article content not found for: {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content: {url}")
        print(f"Error details: {str(e)}")
        return None

def update_articles_md(new_articles_df):
    try:
        existing_articles_df = pd.read_csv('README.md', sep='|', skiprows=1, names=['title', 'author', 'summary', 'date', 'url'])
    except FileNotFoundError:
        existing_articles_df = pd.DataFrame(columns=['title', 'author', 'summary', 'date', 'url'])

    merged_df = pd.merge(new_articles_df, existing_articles_df, on="title", how="left", indicator=True)
    new_entries = merged_df[merged_df['_merge'] == 'left_only']

    if not new_entries.empty:
        new_entries = new_entries.reindex(columns=['title', 'author', 'summary', 'date', 'url'], fill_value='')

        with open('README.md', 'w') as f:
            f.write("| Title | Author | Summary | Date | URL |\n")
            f.write("|-------|--------|---------|------|-----|\n")
            existing_articles_df.to_csv(f, sep='|', index=False, header=False)
            new_entries.to_csv(f, sep='|', index=False, header=False)

        print(f"Added {len(new_entries)} new articles to README.md")
        
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