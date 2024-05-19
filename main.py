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
    import time
    image_urls = get_image_urls(os.environ.get('BASE_URL'))
    for image in image_urls:
        print(image)
        for i in range(3):
            infobeamer_main("255.255.255.255", 5, image)
        time.sleep(5)

if __name__ == '__main__':
    main()
