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
                variants(first: 1) {
                    nodes {
                        displayName 
                        price
                    }
                }
            }
        }
    }
    """

    response = requests.post(url, headers=headers, json={ 'query': query })
    result = response.json()
    if 'data' in result and 'products' in result['data'] and 'nodes' in result['data']['products']:
        return [{ 'id': product['id'], 'title': product['title'], 'price': product['variants']['nodes'][0]['price']} for product in result['data']['products']['nodes']]
    else:
        print(f"Error fetching products: {result}")
        exit(1)


def create_metafield_definition(key, name, ownerType, type, access, description = ""):
    """
    Create a metafield definition and return the ID
    """
    mutation_create_metafield = """
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          name
        }
        userErrors {
          field
          message
          code
        }
      }
    }
    """

    variables = {
        "definition": {
            "key": key,
            "name": name,
            "ownerType": ownerType,
            "type": type,
            "access": access,
            "description": description
        }
    }

    response = requests.post(url, headers=headers, json={'query': mutation_create_metafield, 'variables': variables})
    result = response.json()


def add_price_per_lb_metafield_to_products(products, blacklist_ids):
    for product in products:
        if product['id'] in blacklist_ids: continue
        add_price_per_lb_metafield_to_product(product['id'], product['price'])

def add_price_per_lb_metafield_to_product(id, price_per_lb):
    mutation_update_metafield = """
    mutation ProductUpdate($input: ProductInput!) {
      productUpdate(input: $input) {
        userErrors {
          field
          message
        }
      }
    }
    """


    variables = {
        "input": {
            "id": id,
            "metafields": {
                "namespace": "app--175464054785",
                "key": "price_per_lb",
                "value": json.dumps({
                    "amount": price_per_lb,
                    "currency_code": "USD"
                })
            }
        }
    }
    response = requests.post(url, headers=headers, json={ 'query': mutation_update_metafield, 'variables': variables })
    result = response.json()
    print(result)
    if 'errors' in result:
        print(result)
        exit(1)
    if len(result['data']['productUpdate']['userErrors']) > 0:
        print(result['data']['productUpdate']['userErrors'])
        exit(1)
    

def delete_metafield(id):
    mutation_delete_metafield = """
    mutation DeleteMetafieldDefinition($id: ID!, $deleteAllAssociatedMetafields: Boolean!) {
      metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: $deleteAllAssociatedMetafields) {
        deletedDefinitionId
        userErrors {
          field
          message
          code
        }
      }
    }
    """
    variables = {
        "id": id,
        "deleteAllAssociatedMetafields": True
    }
    response = requests.post(url, headers=headers, json={ 'query': mutation_delete_metafield, 'variables': variables })
    result = response.json()

def main():
    blacklisted_products = get_products_in_blacklisted_collections()
    # print(blacklisted_products)
    all_products = get_all_products() 
    # print(all_products)

    add_price_per_lb_metafield_to_products(all_products, blacklisted_products)

    # access = {
    #     "admin": "MERCHANT_READ_WRITE", 
    #     "customerAccount": "NONE", 
    #     "storefront": "PUBLIC_READ"
    # }
    # create_metafield_definition('price_per_lb', "Price Per Lb", "PRODUCT", "money", access, "The price per pound of the product.")


if __name__ == "__main__":
    main()

