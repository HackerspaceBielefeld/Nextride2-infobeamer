"""
Module for infobeamer functionality.
"""

from communication import Nextride2PacketSender
from infobeamer_helper import get_urls


def infobeamer_main(dest:str, seconds:int, uri:str, schedule:list):
    """
    Sends content to infobeamer screens.

    If the schedule list, containing content urls is empty, the uri is displayed,
    otherwise the urls from the schedule are sent to the infobeamer screens. 

    Args:
        dest (str): The destination IP address.
        seconds (int): The time in seconds the content should be displayed.
        uri (str): The URI of the content to be displayed.
        schedule (list): List of scheduled content URIs.
    """
    if len(schedule) > 0:
        urls = get_urls(schedule)
    else:
        urls = []
    sender = Nextride2PacketSender()
    if uri and len(urls) == 0:
        sender.send_packet(dest, seconds, uri)
    for url in urls:
        sender.send_packet(dest, seconds, url)
