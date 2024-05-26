"""
Module for infobeamer functionality.
"""

from communication import Nextride2PacketSender


def infobeamer_main(dest:str, seconds:int, uri:str):
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
    sender = Nextride2PacketSender()
    sender.send_packet(dest, seconds, uri)
