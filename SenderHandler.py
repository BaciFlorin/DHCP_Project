import threading
from coada import *
from AddressPool import *
from IPAddress import *
typesOfMessage={
    1:"DISCOVERY",
    2:"DHCPOFFER",
    3:"DHCPREQUEST",
    4:"DHCPDECLINE",
    5:"DHCPACK",
    6:"DHCPNAK",
    7:"DHCPRELEASE",
    8:"DHCPINFORM"
}

options={

}

class SenderHandler(threading.Thread):
    def __init__(self,_messageQueue):
        threading.Thread.__init__(self)
        self.messageQueue=_messageQueue
        self.unfinisedClients = []
        self.pool=AddressPool("192.168.128.0","255.255.128.0")

    def start(self):
        while True:
            if not self.messageQueue.isEmpty():
                #functie de care imi identifica tipul de actiune pe care trebuie sa o iau
                #functie care sa imi returneze ce mesaj sa fie trimis
                message = self.messageQueue.get()
                type=typesOfMessage[self.identifieMessage(message)]
                self.modifieMessage(type,message)

    def identifieMessage(self,message):
        type=0
        for i in range(0,len(message.options)):
            if int(message.options[i])==53:
                type=int(message.options[i+2])
                break
        return type

    def modifieMessage(self,typeOfMessage,message):
        if typeOfMessage=="DISCOVERY":
            message.op=0x02
            address=self.pool.getFreeAddress(message.chaddr).split('.')
            message.yiaddr=0
            for i in range (0,4):
                message.yiaddr+=int(address[i])*pow(2,(3-i))
            message.yiaddr=hex(message.yiaddr)

    def messageSend(self):
        pass
