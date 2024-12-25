from woocommerce import API
from dotenv import load_dotenv
from os import getenv

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
customers = wcapi.get("customers/1181").json()

# print(orders)
print(customers)





