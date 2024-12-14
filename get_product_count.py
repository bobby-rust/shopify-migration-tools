import requests
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Replace with your shop's details
SHOP_NAME = "8-oclock-ranch-ny"  # e.g., "myshop" for myshop.myshopify.com
ACCESS_TOKEN = getenv("API_ACCESS_TOKEN")
API_VERSION = "2023-10"  # Latest API version or the version of your choice

url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products/count.json?status=active"
headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an error for 4XX/5XX responses
    data = response.json()
    # product_count = data["count"]
    # print(f"Total products in store: {product_count}")
    print(data)
except requests.exceptions.RequestException as e:
    print("Error fetching product count:", e)
