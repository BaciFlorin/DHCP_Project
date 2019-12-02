import threading
from AddressPool import *
from IPAddress import *

configurations={
        51: 5000,
        54: '192.168.100.182',
        1: '255.255.255.0',
        3: '192.0.0.0, 192.1.1.1',
        6: '192.168.100.69',
        15: 'TataBaci',
        28: '192.168.128.255',
        58: 7220
    }

class SenderHandler(threading.Thread):
    def __init__(self, _queueOfMessages, _ip, _mask):
        threading.Thread.__init__(self)
        self.queueOfMessages = _queueOfMessages
        self.clients = []
        self.pool = AddressPool("192.168.128.0","255.255.128.0")

    def test(self, message): # a fost start
        #while True:
        #citim doar daca exista ceva in coada
        #if not self.queueOfMessages.empty():
        #functie de care imi identifica tipul de actiune pe care trebuie sa o iau
        #functie care sa imi returneze ce mesaj sa fie trimis
        #message = self.queueOfMessages.get()
        type = self.identifieMessage(message.options)
        message=self.modifyMessage(type,message)
        print(message.options)
        self.messageSend(message)

    def identifieMessage(self,options):
        type = 0
        if 53 in options:
            type = options[53]
        else:
            #TO DO: secventa de if-uri care sa isi dea seama ce fel de mesaj avem
            pass
        return type

    def modifyMessage(self, typeOfMessage, message):
        if typeOfMessage=='DHCPDISCOVER':
            #sa ai grija si la cazurile in care se retrimite un DHCPDISCOVERY
            self.clients.append(message.xid)
            message.op = '02'
            oldIp = self.pool.findOldAdress(message.chaddr)
            alocatedAddress=0
            if oldIp != 0:
                if oldIp.free != 0 and oldIp.hold != 1:
                    #cazul in care se ia o adresa care a fost deja a clientului respectiv
                    message.yiaddr = oldIp.ip
                    oldIp.setMac(message.chaddr)
                    oldIp.holdAddress()
                    alocatedAddress=oldIp
                else:
                    #log in care precizezi ca adresa veche nu este libere
                    pass

            elif 50 in message.options:
                requestedIp = self.pool.findAddressIP(message.options[50])
                if requestedIp != 0:
                    if requestedIp.free == 1 and requestedIp.hold == 0:
                        #cazul in care se accepta o adresa data de client
                        message.yiaddr = requestedIp.ip
                        requestedIp.setMac(message.chaddr)
                        requestedIp.holdAddress()
                        alocatedAddress=requestedIp
                    else:
                        #log in care precizezi ca nu este libera adresa ceruta
                        pass
                else:
                    pass
                    #log in care precizezi ca nu este adresa aia in spatiul nostru

            else:
                #cazul in care trebuie sa alocam o noua adresa
                newIp = self.pool.getFreeAddress(message.chaddr)
                message.yiaddr = newIp.ip
                alocatedAddress=newIp

            alocatedAddress.optionsDiscovery = message.options.values()
            alocatedAddress.xid=message.xid

            if 51 in message.options:
                requestedLeaseTime = message.options[51]
                clientIp=self.pool.findAddressMAC(message.chaddr)
                if clientIp !=0 and clientIp.free == 0:
                    requestedLeaseTime = clientIp.leaseTime
                elif requestedLeaseTime < 1000:
                    requestedLeaseTime = configurations[51]
                message.options[51] = requestedLeaseTime
            else:
                message.options[51] = configurations[51]

            message.options[53] = 'DHCPOFFER'

            for i in message.options.keys():
                if i != 50 and i != 53 and i != 51:
                    message.options[i] = configurations[i]
                if i == 50 or i == 61 or i == 55:
                    message.pop(i)
            alocatedAddress.optionsSend=message.options

        elif typeOfMessage == 'DHCPREQUEST':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            ok = True
            # nu mai verifici xid deoarece clientul este obligat sa puna acelasi
            for option in ipAlocated.optionsDiscovery:
                if option not in message.options:
                    ok = False
                    break
            if ok == True:
                if 54 in message.options:
                    #mesajul e un raspuns la DHCPOFFER
                    error = "ok"
                    if ipAlocated.ip == message.options[50] and message.ciaddr == 0:
                        #SELECTING STATE
                        if configurations[54] != message.options[54]:
                            ipAlocated.releaseAddress()
                            error = "Another server"

                    if error == "ok":
                        message.op = '02'
                        message.yiaddr = ipAlocated.ip
                        message.options = ipAlocated.optionsSend
                        message.options[53] = 'DHCPACK'
                else:
                    error= "ok"
                    if message.ciaddr == '':
                        # INIT REBOOT
                        if message.options[50] != ipAlocated.ip:
                            error = "Ip doesn't match"
                        tempip = message.options[50]
                        tempip = tempip.split('.')
                        for i in range(0, 3):
                            tempip[i] = int(tempip)
                            if 255 - self.pool.invertedMask[i] == 255:
                                if tempip[i] != self.pool.ip[i]:
                                    error = "Not the same network"
                            else:
                                if tempip[i] & (255 - self.pool.invertedMask[i]) != self.pool.ip[i]:
                                    error = "Not the same network"
                    elif 50 not in message.options:
                        pass
                    #renewing


        elif typeOfMessage == 'DHCPDECLINE':
            pass
        elif typeOfMessage == 'DHCPRELEASE':
            pass
        elif typeOfMessage == 'DHCPINFORM':
            pass
        else:
            pass
            #log error
        return message




    def messageSend(self,message):
        #broadcast la dhcpnak
        #ciaddr la renewing
        if message != 0:
            pass
