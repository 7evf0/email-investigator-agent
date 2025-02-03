import requests
import random

from smolagents import tool

@tool
def fetch_random_product(item_id: int = 0) -> object:
    """
    Fetch a real random product from a public API to be used in the billing emails.

    Args:
        item_id: Index of which item will be fetched. This index will be helpful when fetching distinct items in each function call.
    """
    # Use Fakestore API to fetch products
    api_url = "https://fakestoreapi.com/products"
    response = requests.get(api_url)
    if response.status_code == 200:
        products = response.json()
        random_product = products[item_id]
        product_details = {
            "name": random_product["title"],
            "price": f"${random_product['price']:.2f}",
            "description": random_product["description"],
            "link": random_product["image"]
        }
        return product_details
    else:
        return "Failed to fetch product data"