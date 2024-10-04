import os
import argparse
import pygame


from display import display_image
from image_fetcher import fetch_image_from_url
from image_fetcher import get_image_urls

# Initialize pygame
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen, pygame.time.Clock()

# Cache image surfaces to avoid redundant downloads
image_cache = {}


# Main loop to fetch and display images
def main(cms_url):
    os.environ['DISPLAY'] = ':0'

    duration = 5  # Image display duration
    screen, clock = init_pygame()  # Initialize pygame once

    while True:
        # Get image URLs from CMS
        image_urls = get_image_urls(cms_url)
        system_image_urls = get_image_urls(cms_url + "/system")

        # Display system images first
        for system_image_url in system_image_urls:
            if system_image_url not in image_cache:
                image = fetch_image_from_url(system_image_url)
                if image:
                    image_cache[system_image_url] = image
            display_image(screen, clock, image_cache[system_image_url], duration)

        # Display CMS images and intersperse with system images
        for i, image_url in enumerate(image_urls):
            if i % 6 == 5:
                for system_image_url in system_image_urls:
                    if system_image_url not in image_cache:
                        image = fetch_image_from_url(system_image_url)
                        if image:
                            image_cache[system_image_url] = image
                    display_image(screen, clock, image_cache[system_image_url], duration)
            if image_url not in image_cache:
                image = fetch_image_from_url(image_url)
                if image:
                    image_cache[image_url] = image
            display_image(screen, clock, image_cache[image_url], duration)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='N2i runner')
    parser.add_argument('-c', '--cms', required=True, \
                        help='URL of the CMS whose content to display')
    args = parser.parse_args()
    main(args.cms)
