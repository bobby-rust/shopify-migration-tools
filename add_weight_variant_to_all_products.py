import requests
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()

SHOP_URL = getenv("SHOP_URL") 
ACCESS_TOKEN = getenv("API_ACCESS_TOKEN")
API_VERSION = "2024-04"

url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

def get_products_in_blacklisted_collections():
    """
    Get all blacklisted products and return their ids in a list of strings.

    Gets all products that are in the collections that we do NOT want to add 
    a price per lb metafield for. Gets all Snack Foods, Boxes, Bulk Meat
    Used to get a list of IDs for products that we do not want to add the metafield for
    so that when we get a list of all products, we have a blacklist
    """

    # snack foods      id: 282987495560
    # boxes            id: 275122159752
    # buy meat in bulk id: 275077136520 
    SNACK_FOODS = '282987495560'
    BOXES = '275122159752' 
    BUY_MEAT_IN_BULK = '275077136520'
    blacklisted_collections = [SNACK_FOODS, BOXES, BUY_MEAT_IN_BULK]

    query_get_product_ids_from_collection = """
        query getCollectionProducts($id: ID!) {
            collection(id: $id) {
                products(first: 250) {
                    nodes {
                        id
                    }
                }
            }
        }
    """

    blacklisted_products = set()
    for collection_id in blacklisted_collections:
        full_id = f"gid://shopify/Collection/{collection_id}"
        variables = {
            "id": full_id
        }
        response = requests.post(
            url, 
            headers=headers,
            json={
                'query': query_get_product_ids_from_collection,
                'variables': variables
            }
        )

        result = response.json()
        if 'data' in result and 'collection' in result['data']:
            products = result['data']['collection']['products']['nodes']
            collection_product_ids = {product['id'] for product in products}
            blacklisted_products.update(collection_product_ids)
            print(f"Found {len(collection_product_ids)} products in collection {collection_id}")
        else:
            print(f"Error fetching collection {collection_id}: {result}")

    return list(blacklisted_products)

def get_all_products():
    query = """
    query {
        products(first: 250) {
            nodes {
                id
                title
                variants(first: 10) {
                    nodes {
                        displayName 
                        price
                        selectedOptions {
                            name
                            value
                        }
                    }
                }
                options {
                    id
                    linkedMetafield {
                        key
                        namespace
                    }
                    name
                    optionValues {
                        id
                        linkedMetafieldValue
                        name
                    }
                    values
                }
            }
        }
    }
    """
    
    response = requests.post(url, headers=headers, json={ 'query': query })
    result = response.json()

    if 'data' in result and 'products' in result['data'] and 'nodes' in result['data']['products']:
        return [
            { 
                'id': product['id'], 
                'title': product['title'], 
                'price': product['variants']['nodes'][0]['price'],
                'variants': product['variants']['nodes'],
                'selected_options': [variant['selectedOptions'] for variant in product['variants']['nodes']],
                'options': product['options']
            } 
            for product in result['data']['products']['nodes']
        ]

    else:
        print(f"Error fetching products: {result}")
        exit(1)

def add_weight_variant_to_products(products):
    for product in products:
        add_weight_variant_to_product(product)

def add_weight_variant_to_product(product):
    print("Adding weight option to product: ", product['id'])
    mutation_update_option = """
    mutation updateOption(
       $productId: ID!, 
       $option: OptionUpdateInput!, 
       $optionValuesToAdd: [OptionValueCreateInput!], 
       $optionValuesToUpdate: [OptionValueUpdateInput!], 
       $optionValuesToDelete: [ID!], 
       $variantStrategy: ProductOptionUpdateVariantStrategy
    ) {
        productOptionUpdate(
            productId: $productId, 
            option: $option, 
            optionValuesToAdd: $optionValuesToAdd, 
            optionValuesToUpdate: $optionValuesToUpdate, 
            optionValuesToDelete: $optionValuesToDelete,
            variantStrategy: $variantStrategy
            ) {
            userErrors {
              field
              message
              code
            }
            product {
              id
              options {
                id
                name
                values
                position
                optionValues {
                  id
                  name
                  hasVariants
                }
              }
              variants(first: 5) {
                nodes {
                  id
                  title
                  selectedOptions {
                    name
                    value
                  }
                }
              }
            }
          }
        }
    """

    variables = {
        "productId": product['id'],
        "option": {
            "id": product['options'][0]['id'],
            "name": "Weight"
        },
        "optionValuesToUpdate": [
            {
              "id": product['options'][0]['optionValues'][0]['id'],
              "name": "1 LB"
            }
        ]
    }
     
    response = requests.post(url, headers=headers, json={ 'query': mutation_update_option, 'variables': variables })
    result = response.json()
    if 'errors' in result or ('userErrors' in result and len(result['userErrors']) > 0):
        print("Error adding variant to product: ", result)
    else:
        print("Successfully added variant to ", product['title'])

def main():
    products = get_all_products()
    blacklist = get_products_in_blacklisted_collections()
    products_whitelist = []
    for product in products:
        # Regarding the [0][0], I'm not sure if this needs to be a nested list. I may have just built the list wrong, but it works
        if product['id'] not in blacklist and product['selected_options'][0][0]['value'] == "Default Title":
            products_whitelist.append(product)
    
    # print({ 'data': products_whitelist })
    add_weight_variant_to_products(products_whitelist)

if __name__ == "__main__":
    main()

