import socket

class Nextride2PacketSender:
    """
    A class for sending packets to a destination using the Nextride2 interface.
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send_packet(self, dest:str, sec:int, uri:str):
        """
        Sends a packet to the specified destination.

        Args:
            dest (str): The destination ip-address to send the packet to.
            sec (int): The time in seconds the file should be displayed on the nextride screens.
            uri (str): The URI of the media to display.
        """
        urilen = len(uri)
        r = bytearray([sec, urilen]) + uri.encode('ascii')
        r += bytearray(257 - len(r))
        for _ in range(3):
            self.sock.sendto(r, (dest, 31337))
