import requests
import pandas as pd
from datetime import datetime
import math
from time import sleep
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Example API endpoint for retrieving all blogs
SHOP_NAME = '8-oclock-ranch-ny'
ACCESS_TOKEN = getenv("API_ACCESS_TOKEN") 

BLOGS_URL = "https://" + SHOP_NAME + ".myshopify.com/admin/api/2024-10/blogs.json"

# Load the CSV file
csv_file_path = 'Posts-Export-2024-December-11-1202.csv'
df = pd.read_csv(csv_file_path)

# Shopify API credentials
API_KEY = getenv("API_KEY") 
BLOG_ID = '81304879240'  # ID of the blog where you want to post

# Shopify API endpoint
api_url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2024-10"

headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

def create_blog(created_at):
    year = created_at[:4] # first 4 digits of iso date is year
    response = requests.post(f"{api_url}/blogs.json", json={"Content-Type": "application/json", "blog": { "title": year, "created_at": created_at }}, headers=headers) # the blog field is the title which we use year for
    if response.status_code == 201:
        print(f"Created Blog: {year}")
        return response.json()['blog']['id']
    else:
        print(f"Failed to create: ", response.json())
        return None

# Helper function to create an article
def create_article(blog_id, author, title, content, published_at, updated_at, tags, excerpt, image_url=None):
    image_data = {
        "src": image_url,
        "created_at": published_at 
    }

    print(image_data)
    article_data = {
        "article": {
            "author": author,
            "title": title,
            "body_html": content,
            "published_at": published_at,
            "updated_at": updated_at,
            "tags": tags,
            "summary_html": excerpt,
            "image": image_data
        }
    }
    
    response = requests.post(f"{api_url}/blogs/{blog_id}/articles.json", json=article_data, headers=headers)
    if response.status_code == 201:
        print(f"Created: {title}")
    else:
        print(f"Failed to create: ", response.json())
    return response.json()

# Process each row in the CSV and create articles
for index, row in df.iterrows():
    first_name = row['Author First Name']

    if pd.isnull(first_name):
        first_name = ""

    last_name = row['Author Last Name']

    if pd.isnull(last_name):
        last_name = ""

    author = first_name + " " + last_name

    title = row['Title']
    if pd.isnull(title):
        title = ""

    content = row['Content']
    if pd.isnull(content):
        print("Empty blog post! What's going on?!")
        content = ""

    published_at = datetime.strptime(row['Date'], '%Y-%m-%d')

    if pd.isnull(published_at):
        published_at = None
    else:
        if published_at.year < 2009:
            published_at = datetime.now().isoformat()
        else:
            published_at = published_at.isoformat()

    
    year = published_at[:4]
    blogs = requests.get(BLOGS_URL, headers=headers).json()
    sleep(0.5)
    blog_id = None
    for blog in blogs['blogs']:
        if blog['title'] == year:
            blog_id = blog['id']
            break
        else:
            blog_id = None

    if blog_id is None: 
        blog_id = create_blog(published_at) # first 4 digits of iso is year
        sleep(0.5)

    if blog_id is None:
        print("Failed to create blog. Skipping post.")
        continue

    tags = row['Tags']
    if pd.isnull(tags):
        tags = ""

    tags = tags.replace("|", ",")

    image_url = row['Image Featured']
    print(image_url)
    if pd.isnull(image_url):
        image_url = None

    excerpt = row['Excerpt']
    if pd.isnull(excerpt):
        excerpt = ""

    updated_at = row['Post Modified Date']
    if pd.isnull(updated_at):
        updated_at = None
    else:
        updated_at = datetime.strptime(updated_at, '%Y-%m-%d')
        if updated_at.year < 2009:
            updated_at = datetime.now().isoformat()
        else:
            updated_at = updated_at.isoformat()
    
    # Create the article in Shopify
    result = create_article(blog_id, author, title, content, published_at, updated_at, tags, excerpt, image_url)
    sleep(0.5)

'''
TODO: Upload images to Shopify, then parse blog post contents and replace image URLs,
handle image captions and look for other inconsistencies to fix, then finally blogs are ready to be uploaded
'''
print("All posts have been uploaded.")
