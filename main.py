from bs4 import BeautifulSoup
import requests
import time
import os

from infobeamer import infobeamer_main

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
    while(1):
        image_urls = get_image_urls("")
        for image in image_urls:
            print(image)
            for i in range(3):
                duration = 5
                infobeamer_main("255.255.255.255", duration, image)
            time.sleep(duration)

if __name__ == '__main__':
    main()

