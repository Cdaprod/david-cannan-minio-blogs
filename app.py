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

def sanitize_title(title):
    return re.sub(r'[^\w\-]', '_', title)[:250]

def ensure_absolute_url(url):
    if url.startswith('http'):
        return url
    return 'https://blog.min.io' + url

def download_image(image_url, save_path):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return save_path
    return None

def clean_article_content(content):
    # Split content by lines
    lines = content.split('\n')
    cleaned_lines = []
    skip_lines = [
        'Share:', 'Follow:', 'Previous Post', 'Next Post', 'LinkedIn',
        'X (Twitter)', 'Reddit', 'Copy Article Link', 'Email Article',
        'MinIO Slack', 'Best Practices', 'Get Started with MinIO', 'Advanced Topics'
    ]
    add_line = True

    for line in lines:
        # Skip lines that contain any of the skip keywords
        if any(skip in line for skip in skip_lines):
            add_line = False
        # If an empty line is encountered, start adding lines again
        if not line.strip():
            add_line = True
        # Add cleaned lines
        if add_line and not any(skip in line for skip in skip_lines):
            cleaned_lines.append(line.strip())

    return '\n'.join(cleaned_lines).strip()

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
            # Ensure the URL is absolute before making a request
            absolute_url = ensure_absolute_url(row['url'])
            response = requests.get(absolute_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            article_content = soup.select_one('article').get_text(separator="\n", strip=True) if soup.select_one('article') else 'Content not found'
            cleaned_content = clean_article_content(article_content)
            filename = f"articles/{sanitize_title(row['title'])}.md"

            if row['image_url']:
                image_url = urljoin(absolute_url, row['image_url'])
                image_path = f"articles/images/{sanitize_title(row['title'])}.jpg"
                download_image(image_url, image_path)
                cleaned_content = f"![Header Image]({image_path})\n\n{cleaned_content}"

            with open(filename, 'w') as article_file:
                article_file.write(f"# {row['title']}\n\n{cleaned_content}\n")

    updated_readme_content = readme_content[:start_index] + '\n' + new_content + '\n' + readme_content[end_index:]

    with open('README.md', 'w') as f:
        f.write(updated_readme_content)

if __name__ == "__main__":
    est = pytz.timezone('US/Eastern')
    print(f"Running update job at {datetime.now(est)} EST")
    articles_df = fetch_and_parse_articles()
    update_readme_and_articles(articles_df)