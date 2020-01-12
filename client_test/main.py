import socket, time
from Messages import *
from Concat_dict import *

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('0.0.0.0', 68))
s.sendto(concat_dict(dhcp_discover), ('255.255.255.255', 67))
data = s.recvfrom(4096)
data = data[0].decode("utf-8")
print(data)
s.close()
