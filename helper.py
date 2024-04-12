"""
Helper module containing utility functions.
"""

import xml.etree.ElementTree as ET

import requests


def fetch_schedule(schedule_uri: str, timeout: int = 10) -> str:
    """
    Fetches schedule data from a given URI.

    Args:
        schedule_uri (str): The URI to fetch the schedule data from.
        timeout (int, optional): The timeout value for the HTTP request in seconds. Defaults to 10.

    Returns:
        str: The fetched schedule data if successful, None otherwise.
    """
    try:
        response = requests.get(schedule_uri, timeout=timeout)
        if response.status_code == 200:
            return response.text
        print("Failed to fetch XML. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred while fetching XML:", str(e))
    return None

def get_local_schedule_content(schedule_uri) -> str:
    """
    Reads and returns the content of a local schedule file.

    Args:
        schedule_uri (str): The URI of the local schedule file.

    Returns:
        str: The content of the local schedule file.
    """

    schedule_lines = []
    try:
        with open(schedule_uri, "r", encoding='UTF-8') as f:
            for line in f:
                schedule_lines.append(line.strip())  # Strip newline characters and add to the list
    except FileNotFoundError:
        print("Error: Schedule file not found.")
    except PermissionError:
        print("Error: Permission denied. You don't have access to the schedule file.")
    except IsADirectoryError:
        print("Error: The provided URI is a directory, not a file.")
    except UnicodeDecodeError:
        print("Error: Unable to decode schedule file. Ensure it is encoded in UTF-8.")
    except OSError as e:
        print(f"Error: OS error occurred: {e}")
    return schedule_lines

def get_urls(schedule:str) -> list:
    """
    Extracts URLs from XML schedule content.

    Args:
        schedule (str): The XML schedule content.

    Returns:
        list: A list containing URLs extracted from the XML schedule.
    """
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
