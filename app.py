import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os
import re
from urllib.parse import urljoin

# Constants
AUTHOR = 'David Cannan'
BLOG_URL = 'https://blog.min.io/author/david-cannan'

# Fetch and parse articles
def fetch_and_parse_articles():
    response = requests.get(BLOG_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for article in soup.select('article.post-card'):
        title = article.find('h2').text.strip() if article.find('h2') else 'No Title Available'
        summary = article.select_one('.post__content').text.strip() if article.select_one('.post__content') else 'Summary not available'
        date = article.find('time')['datetime'].strip() if article.find('time') else 'Date not available'
        link = article.select_one('a[href]')['href'] if article.select_one('a[href]') else 'URL not available'
        image_url = article.select_one('img')['src'] if article.select_one('img') else None
        articles.append({"title": title, "author": AUTHOR, "summary": summary, "date": date, "url": link, "image_url": image_url})

    df = pd.DataFrame(articles)
    df['index'] = range(len(df), 0, -1)  # Add a reverse index starting from the total number of articles
    return df

# Sanitize title to create a valid filename
def sanitize_title(title):
    return re.sub(r'[^\w\-]', '_', title)[:250]

# Ensure the URL is absolute
def ensure_absolute_url(url):
    if url.startswith('http'):
        return url
    return 'https://blog.min.io' + url

# Download image
def download_image(image_url, save_path):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return save_path
    return None

# Clean and extract article content
def clean_article_content(article):
    content_section = article.find('section', class_='post-content')
    if not content_section:
        return "Content not found"
    
    elements = content_section.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'ol', 'pre', 'blockquote', 'figure', 'code'])
    cleaned_lines = []
    
    for element in elements:
        if element.name in ['ul', 'ol']:
            items = [f"* {li.get_text(strip=True)}" for li in element.find_all('li')]
            cleaned_lines.extend(items)
        elif element.name == 'pre':
            code = element.get_text(strip=True)
            cleaned_lines.append(f"```\n{code}\n```")
        elif element.name == 'blockquote':
            quote = element.get_text(strip=True)
            cleaned_lines.append(f"> {quote}")
        elif element.name == 'figure' and element.find('img'):
            img_url = element.find('img')['src']
            cleaned_lines.append(f"![Image]({img_url})")
        elif element.name == 'code':
            code = element.get_text(strip=True)
            cleaned_lines.append(f"`{code}`")
        else:
            cleaned_lines.append(element.get_text(strip=True))
    
    return '\n\n'.join(cleaned_lines).strip()

# Update README and save articles
def update_readme_and_articles(articles_df):
    if not os.path.exists('articles'):
        os.makedirs('articles')

    if not os.path.exists('articles/images'):
        os.makedirs('articles/images')

    existing_urls = []
    if os.path.exists('README.md'):
        with open('README.md', 'r') as f:
            existing_urls = re.findall(r'\[Link\]\((https?://.*?)\)', f.read())

    articles_df['is_new'] = ~articles_df['url'].isin(existing_urls)
    
    # Update README.md
    with open('README.md', 'r') as f:
        readme_content = f.read()

    start_marker = '<!-- START_ARTICLES -->'
    end_marker = '<!-- END_ARTICLES -->'
    start_index = readme_content.find(start_marker) + len(start_marker)
    end_index = readme_content.find(end_marker)

    if start_index == -1 or end_index == -1:
        print("Markers not found in README.md")
        return

    new_content = "| No. | Title | Author | Summary | Date | Link |\n"
    new_content += "|-----|-------|--------|---------|------|------|\n"
    for index, row in articles_df.iterrows():
        new_content += f"| {row['index']} | {row['title']} | {row['author']} | {row['summary']} | {row['date']} | [Link]({ensure_absolute_url(row['url'])}) |\n"

        if row['is_new']:
            absolute_url = ensure_absolute_url(row['url'])
            response = requests.get(absolute_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            article = soup.find('article', class_='post--full')
            article_content = clean_article_content(article) if article else 'Content not found'
            filename = f"articles/{sanitize_title(row['title'])}.md"

            if row['image_url']:
                image_url = urljoin(absolute_url, row['image_url'])
                image_path = f"articles/images/{sanitize_title(row['title'])}.jpg"
                download_image(image_url, image_path)
                article_content = f"![Header Image]({image_path})\n\n{article_content}"

            with open(filename, 'w') as article_file:
                article_file.write(f"# {row['title']}\n\n{article_content}\n")

    updated_readme_content = readme_content[:start_index] + '\n' + new_content + '\n' + readme_content[end_index:]

    with open('README.md', 'w') as f:
        f.write(updated_readme_content)

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    update_readme_and_articles(articles_df)