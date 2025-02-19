from woocommerce import API
from dotenv import load_dotenv
from os import getenv
from time import sleep

load_dotenv()

WP_CONSUMER_KEY    = getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = getenv("WP_CONSUMER_SECRET")
WP_URL             = getenv("WP_URL")

assert WP_CONSUMER_KEY    != None, "\033[91mPlease set WP_CONSUMER_KEY environment variable\033[0m"
assert WP_CONSUMER_SECRET != None, "\033[91mPlease set WP_COMSUMER_SECRET environment variable\033[0m"
assert WP_URL             != None, "\033[91mPlease set WP_URL environment variable\033[0m"

print(WP_CONSUMER_KEY)
print(WP_CONSUMER_SECRET)

wcapi = API(
    url=WP_URL,
    consumer_key=WP_CONSUMER_KEY,
    consumer_secret=WP_CONSUMER_SECRET,
    version="wc/v3"
)

# orders = wcapi.get("orders", params={ "per_page": 1, "customer": 1181 }).json()
# customers = wcapi.get("customers/1181").json()

# print(orders)
# print(customers)

# product1 = wcapi.get("products/2221", params={ "per_page": 1 }).json()
# product2 = wcapi.get("products/2222", params={ "per_page": 1 }).json()
# product3 = wcapi.get("products/2223", params={ "per_page": 1 }).json()
# print("Product 1: ", product1)
# print("Product 2: ", product2)
# print("Product 3: ", product3)

wcapi.timeout = 20

products1 = wcapi.get("products", params={"per_page": 100, "page": 1})
products2 = wcapi.get("products", params={"per_page": 100, "page": 2})

if products1.status_code == 200 and products2.status_code == 200:
    print("Status 200")
    print(len(products1.json()) + len(products2.json()))
else:
    print(products1.status_code)
    print(products2.status_code)
