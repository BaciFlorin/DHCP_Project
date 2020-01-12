import os
import socket
from Concat_dict import *
from Messages import *
from MessageType import *
import logging
logging.basicConfig(filename='app.log', filemode='w')



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
sock.connect(('127.0.0.1',5000))
#sock.connect_ex(('192.168.43.151',5000))

def main():
    com_level = Communication_Level(sock)
    com_level.decode_message(concat_dict(dhcp_discover))
    com_level.send('discover')
    
if __name__ == "__main__":
    main()