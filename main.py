import os
from infobeamer import infobeamer_main

import requests
from bs4 import BeautifulSoup

def get_image_urls(url):
    try:
        response = requests.get(url)
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


def main():
    image_urls = get_image_urls("http://127.0.0.1:5000/")
    for image in image_urls:
        infobeamer_main("255.255.255.255", 10, image)

if __name__ == '__main__':
    main()
