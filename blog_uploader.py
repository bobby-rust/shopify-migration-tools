import requests
import pandas as pd
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from os import getenv
from bs4 import BeautifulSoup as bs
from bs4 import Tag
import re

load_dotenv()

# Get environment vars
SHOP_URL = getenv("SHOP_URL") 
ACCESS_TOKEN = getenv("API_ACCESS_TOKEN") 
SHOPIFY_CDN_BASE_URL = getenv("SHOPIFY_CDN_BASE_URL") 
CSV_FILE_PATH = getenv("CSV_FILE_PATH")

try:
    assert SHOP_URL is not None
    assert ACCESS_TOKEN is not None
    assert SHOPIFY_CDN_BASE_URL is not None
    assert CSV_FILE_PATH is not None
except:
    raise ValueError("\033[91mPlease set all required environment variables: \n\
                SHOP_URL, \n\
                API_ACCESS_TOKEN, \n\
                SHOPIFY_CDN_BASE_URL, \n\
                CSV_FILE_PATH \033[0m")

BLOGS_URL = "https://" + SHOP_URL + "/admin/api/2024-10/blogs.json"

# Load the CSV file
df = pd.read_csv(CSV_FILE_PATH)

# Shopify API credentials
API_KEY = getenv("API_KEY") 

# Shopify API endpoint
api_url = f"https://{SHOP_URL}/admin/api/2024-10"

headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

def create_blog(year, created_at):
    response = requests.post(f"{api_url}/blogs.json", json={"Content-Type": "application/json", "blog": { "title": year, "created_at": created_at }}, headers=headers) # the blog field is the title which we use year for
    if response.status_code == 201:
        print(f"Created Blog: {year}")
        return response.json()['blog']['id']
    else:
        print(f"Failed to create: ", response.json())
        return None

def convert_captions(content):
    '''
    Uses regular expressions to parse and convert WordPress [caption]s to modern
    html equivalent
    [caption .*].*[/caption] needs to be replaced with <figure> -> <img /> ->
    <figcaption> -> </figcaption> -> </figure>
    width can be captured from [caption width="<width>"] and placed in <img
    style="width: <width>" />
    '''
    pattern = r'\[caption(.*?)\](.*?)\[/caption\]'

    def replacer(match):
        attrs = match.group(1).strip()

        inner_content = match.group(2)
        caption_pattern = r'(?<=\>).+'

        caption = re.search(caption_pattern, inner_content)
        caption = caption.group(0) if caption is not None else ""
        img_pattern = r'(<img.*/>)'
        img = re.search(img_pattern, inner_content)
        img = img.group(0) if img is not None else ""

        return f'<figure><div>{str(img)}</div><figcaption>{str(caption).strip()}</figcaption></figure>'

    return re.sub(pattern, replacer, content)

def parse_content(content) -> str:
    '''
    Replaces img tags with the new Shopify src, unwraps img tags from <a> tags,
    and converts WordPress [caption][/caption] to modern html equivalent
    <figure>
        <img src={src} />
        <figcaption>{caption}</figcaption>
    </figure>
    '''
    soup = bs(content, "html.parser")
    imgs = soup.find_all("img")
    for img in imgs:
        try:
            del img.attrs["class"]
        except KeyError as e:
            print("KeyError: img does not have attribute 'class'")
        if "8oclockranch" in img.attrs["src"]:
            img.attrs["src"] = SHOPIFY_CDN_BASE_URL + img.attrs["src"].split("/")[-1]

    a_tags = soup.find_all("a")
    for a in a_tags:
        try:
            a.unwrap()
        except:
            print("Cannot unwrap <a> tag")

    # replace return carriage and newline with html breaks
    c = str(soup)
    return convert_captions(c).replace("\r\n", "<br>")


def get_first_image(content):
    ''' 
    Returns the first image found in content, 
    or None if content has no images 
    '''
    soup = bs(content, 'html.parser')
    image = soup.find("img")
    if not isinstance(image, Tag):
        return
    
    return image.attrs['src']


# Helper function to create an article
def create_article(blog_id, author, title, content, published_at, updated_at,
                   tags, excerpt, status, image_url=None):
    image_data = {
        "src": image_url,
        "created_at": published_at 
    }

    article_data = {
        "article": {
            "author": author,
            "title": title,
            "body_html": content,
            "published_at": published_at,
            "updated_at": updated_at,
            "tags": tags,
            "summary_html": excerpt,
            "image": image_data,
            "published": status
        }
    }

    response = requests.post(f"{api_url}/blogs/{blog_id}/articles.json", json=article_data, headers=headers)
    if response.status_code == 201:
        print(f"Created: {title}")
    else:
        print(f"Failed to create: ", title)
        print("Due to error: ",response.json())
    return response.json()

# Process each row in the CSV and create articles
for index, row in df.iterrows():
    status = row["Status"]
    status = False if status == "draft" else True  
    if not status:
        continue

    first_name = row['Author First Name']

    if first_name is None or first_name != first_name:
        first_name = ""

    last_name = row['Author Last Name']

    if last_name is None or last_name != last_name:
        last_name = ""

    author = first_name + " " + last_name

    title = row['Title']
    if title is None or title != title:
        title = "Untitled"
        status = False # if there is no title, do not publish the blog post, but keep it as a draft
        # for now, I can't figure out a way to upload a hidden article, 
        # I don't think shopify lets us do that, so we can't add drafts
        continue 

    # Uncomment to test specific blog posts
    # if title != "It's our News Blog!":
    #     continue

    '''
    TODO: remove class attribute from images
    replace src attribute with SHOPIFY_CDN_BASE_URL +  
    url.split('/')[-1]
    the content section of the csv is just a string, so we need beautifulsoup to
    parse it as html to manipulate it
    ''' 
    content = parse_content(row['Content'])
    if pd.isnull(content):
        print("Empty blog post! What's going on?!")
        content = ""

    date = row["Date"]
    published_at = datetime.strptime(str(date), '%Y-%m-%d')

    if pd.isnull(published_at) or published_at.year < 2009:
        published_at = datetime.now().isoformat()
    else:
        published_at = published_at.isoformat()

    year = published_at[:4] # first 4 digits of iso is year
    # Need to retrieve blogs after each blog creation, for some reason?
    # Why don't we just keep a dictionary of the blogs we have created? 
    blogs = requests.get(BLOGS_URL, headers=headers).json() 
    sleep(0.5) # Don't get rate limited
    blog_id = None
    for blog in blogs['blogs']:
        if blog['title'] == year:
            blog_id = blog['id']
            break
        else:
            blog_id = None

    if blog_id is None: 
        blog_id = create_blog(year, published_at) 
        sleep(0.5)

    if blog_id is None:
        print("Failed to create blog. Skipping post.")
        continue

    tags = str(row['Tags'])
    if pd.isnull(tags) or pd.isna(tags) or tags.strip() == "nan":
        tags = ""

    tags = tags.replace("|", ",")

    image_url = row['Image Featured']
    if image_url is None or image_url != image_url:
        image_url = None
    if image_url is None or image_url == "nan":
        image_url = get_first_image(content)
    

    excerpt = row['Excerpt']
    if excerpt is None or excerpt != excerpt:
        excerpt = ""

    updated_at = row['Post Modified Date']
    if updated_at is None or updated_at != updated_at:
        updated_at = None
    else:
        updated_at = datetime.strptime(str(updated_at), '%Y-%m-%d')
        if updated_at.year < 2009:
            updated_at = datetime.now().isoformat()
        else:
            updated_at = updated_at.isoformat()

    # Create the article in Shopify
    result = create_article(blog_id, author, title, content, published_at,
                           updated_at, tags, excerpt, status, image_url)

    sleep(0.5) # Don't get rate limited

'''
TODO: Upload images to Shopify, then parse blog post contents and replace image URLs,
handle image captions and look for other inconsistencies to fix, then finally blogs are ready to be uploaded
'''

print("All posts have been uploaded.")
