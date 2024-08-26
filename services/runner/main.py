import argparse
import requests
import time

from bs4 import BeautifulSoup

from infobeamer import infobeamer_main

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

def display_image(image:str, duration:int):
    print(image)
    for _ in range(3):
        infobeamer_main("255.255.255.255", duration, image)
    time.sleep(duration)

def main(cms_url:str):
    duration = 5
    while(1):
        image_urls = get_image_urls(cms_url)
        system_image_urls = get_image_urls(cms_url + "/system")

        for system_image in system_image_urls:
            display_image(system_image, duration)

        for i, image in enumerate(image_urls):
            if i % 6 == 5:
                for system_image in system_image_urls:
                    display_image(system_image, duration)
            display_image(image, duration)
            time.sleep(duration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='N2i runner')
    parser.add_argument('-c', '--cms', required=True, \
                        help='URL of the CMS whichs content to display')
    args = parser.parse_args()
    main(args.cms)
