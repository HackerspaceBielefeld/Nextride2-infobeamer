import xml.etree.ElementTree as ET

import requests


def fetch_schedule(schedule_uri:str):
    try:
        response = requests.get(schedule_uri)
        if response.status_code == 200:
            return response.text
        print("Failed to fetch XML. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred while fetching XML:", str(e))
    return None

def get_local_schedule_content(schedule_uri):
    schedule = ""
    with open(schedule_uri, "r", encoding='UTF-8') as f:
        for line in f.readlines():
            schedule += line
    return schedule

def get_urls(schedule):
    root = ET.fromstring(schedule)

    urls = []
    url_elements = root.findall('.//url')

    # Extract the text content of each URL element
    for url_element in url_elements:
        url = url_element.text
        if url:
            print(url)
            urls.append(url)
    return urls
