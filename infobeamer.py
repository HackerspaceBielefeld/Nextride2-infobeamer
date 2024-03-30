from communication import Nextride2PacketSender
from helper import get_urls


def infobeamer_main(dest:str, seconds:int, uri:str, schedule:list):
    urls = get_urls(schedule)
    sender = Nextride2PacketSender()
    for url in urls:
        sender.send_packet(dest, seconds, url)


