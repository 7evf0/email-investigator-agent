import requests
from bs4 import BeautifulSoup
import random
import json

from smolagents import tool, CodeAgent, OpenAIServerModel, ManagedAgent

@tool
def fetch_security_cases(website: str) -> list:
    """
    Fetches the top security vulnerabilities from the given Microsoft 365 security blog.

    Args:
        website: The URL of the blog post listing security vulnerabilities.
    """
    try:
        # Fetch the webpage
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website, headers=headers)
        response.raise_for_status()  # Raise an error if the request fails
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract vulnerabilities from the ordered list
        vulnerabilities = []
        ol = soup.find("ol", class_="wp-block-list")  # Locate the <ol> tag with the specific class
        if ol:
            for li in ol.find_all("li"):  # Find all <li> items within the <ol>
                vulnerabilities.append(li.get_text(strip=True))
        
        return vulnerabilities
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []