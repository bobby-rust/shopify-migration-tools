import requests
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SHOP_URL = getenv("SHOP_URL") 
ACCESS_TOKEN = getenv("API_ACCESS_TOKEN")
API_VERSION = "2023-10"

url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/products.json?limit=250"
headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an error for 4XX/5XX responses
    data = response.json()
    product_count = 0
    for product in data["products"]:
        product_count += len(product["variants"])
        if len(product["variants"]) == 0:
            product_count += 1

    print(f"Total products in store: {product_count}")
except requests.exceptions.RequestException as e:
    print("Error fetching product count:", e)
