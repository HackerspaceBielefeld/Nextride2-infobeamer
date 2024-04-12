import socket

class Nextride2PacketSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send_packet(self, dest:str, sec:int, uri:str):
        urilen = len(uri)
        r = bytearray([sec, urilen]) + uri.encode('ascii')
        r += bytearray(257 - len(r))
        for _ in range(3):
            self.sock.sendto(r, (dest, 31337))
