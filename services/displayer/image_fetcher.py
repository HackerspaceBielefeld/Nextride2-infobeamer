import requests
import pygame
from bs4 import BeautifulSoup
from io import BytesIO

# Function to fetch the image from a URL
def fetch_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Ensure no errors in response
        image_stream = BytesIO(response.content)
        image = pygame.image.load(image_stream)
        return image
    except requests.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None

# Function to get image URLs from a page
def get_image_urls(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for request errors
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')

    img_urls = []
    for img in images:
        img_url = img.get('src')
        if img_url:
            # Ensure the URL is absolute
            if not img_url.startswith(('http://', 'https://')):
                img_url = requests.compat.urljoin(url, img_url)
            img_urls.append(img_url)

    return img_urls