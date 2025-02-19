"""
Products on WooCommerce do not have inventory/quantity..
Still, I must make sure that all of the products from WooCommerce exist on Shopify,
and that their prices are correct.
"""

import json

sp = None
wp = None
with open("shopify_products.json", "r") as f:
    sp = json.load(f)
with open("wc_products.json", "r") as f:
    wp = json.load(f)



def levenshteinFullMatrix(str1, str2):
    m = len(str1)
    n = len(str2)

    # Initialize a matrix to store the edit distances
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

    # Initialize the first row and column with values from 0 to m and 0 to n respectively
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill the matrix using dynamic programming to compute edit distances
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                # Characters match, no operation needed
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # Characters don't match, choose minimum cost among insertion, deletion, or substitution
                dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j], dp[i - 1][j - 1])

    # Return the edit distance between the strings
    return dp[m][n]

num_matches = 0
matches = []
# TODO: Compare shopify variants 
# try "slug" compared with "handle" ?
for sproduct in sp:
    for wproduct in wp:
        # print(sproduct["title"])
        # print(wproduct["name"])
        if sproduct["title"].lower() == wproduct["name"].lower():
            num_matches+=1
            title = sproduct["title"]
            matches.append(title)
            # print(f"Match: {title}")

non_matches = []
for sproduct in sp:
    title = sproduct["title"]
    if title not in matches:
        non_matches.append(title)
for wproduct in wp:
    title = wproduct["name"]
    if title not in matches:
        non_matches.append(title)

print("Need to compare: ", len(non_matches)**2)
comparisons = []
for nm in non_matches:
    for nm2 in non_matches:
        current_comparison = [nm, nm2]
        skip = False
        for comparison in comparisons:
            if nm in comparison and nm2 in comparison:
                skip = True

        if not skip:
            comparisons.append(current_comparison)
            if nm != nm2:
                dist = levenshteinFullMatrix(nm, nm2)
                if dist < 3:
                    print("Close match detected: ", nm, ", ", nm2, " - dist: ", dist)

print(num_matches)

# print(non_matches)

# from os import getenv
# from dotenv import load_dotenv
# import requests
# from woocommerce import API
# from json import dump
#
# load_dotenv()
#
# SHOP_URL = getenv("SHOP_URL") 
# ACCESS_TOKEN = getenv("API_ACCESS_TOKEN") 
#
# assert SHOP_URL is not None, "\033[91mPlease set SHOP_URL environment variable\033[0m"
# assert ACCESS_TOKEN is not None, "\033[91mPlease set API_ACCESS_TOKEN environment variable\033[0m"
#
# api_version ="2024-10"
# url = f"https://{SHOP_URL}/admin/api/{api_version}/products.json?limit=250"
# headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}
#
# shopify_products_count = 0
# shopify_products =[] 
# try:
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()  # Raises an error for 4XX/5XX responses
#     data = response.json()
#     shopify_products = data["products"]
#     for product in shopify_products:
#         shopify_products_count += len(product["variants"])
#         if len(product["variants"]) == 0:
#             shopify_products_count += 1
# except requests.exceptions.RequestException as e:
#     print("Error fetching product count:", e)

# Shopify API endpoint
# api_url = f"https://{SHOP_URL}/admin/api/2024-10"
# headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}
#
# r = requests.get(api_url + "/products/7112883011720.json", headers=headers).json()
#
# print(r)

# WP_CONSUMER_KEY    = getenv("WP_CONSUMER_KEY")
# WP_CONSUMER_SECRET = getenv("WP_CONSUMER_SECRET")
# WP_URL             = getenv("WP_URL")
#
# assert WP_CONSUMER_KEY    != None, "\033[91mPlease set WP_CONSUMER_KEY environment variable\033[0m"
# assert WP_CONSUMER_SECRET != None, "\033[91mPlease set WP_COMSUMER_SECRET environment variable\033[0m"
# assert WP_URL             != None, "\033[91mPlease set WP_URL environment variable\033[0m"
#
# print(WP_CONSUMER_KEY)
# print(WP_CONSUMER_SECRET)
#
# wcapi = API(
#     url=WP_URL,
#     consumer_key=WP_CONSUMER_KEY,
#     consumer_secret=WP_CONSUMER_SECRET,
#     version="wc/v3"
# )
#
# wcapi.timeout = 20
#
# wc_products = wcapi.get("products", params={"per_page": 100, "page": 1}).json()
# products2 = wcapi.get("products", params={"per_page": 100, "page": 2})
#
# wc_products_count = None
# if products2.status_code == 200:
#     print("Status 200")
#     wc_products_count = len(wc_products) + len(products2.json())
#     wc_products.extend(products2.json())
# else:
#     print(products2.status_code)
#
# print("length of shopify_products array: ", len(shopify_products))
# print("length of wc_products array: ", len(wc_products))

# with open("shopify_products.json", "x") as sf:
#     dump(shopify_products, sf)
#
# with open("wc_products.json", "x") as wf:
#     dump(wc_products, wf)
#
# for sp in shopify_products:
#     for wp in wc_products:
#         if sp["title"] == wp["title"]:
#             print(f"Match: {sp["title"]}")
#
# print(f"shopify product count: {shopify_products_count}")
# print(f"wc product count: {wc_products_count}")
