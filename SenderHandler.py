import logging

leaseTime = {}

optionSendInDiscovery = {}

configurations = {
        51: 5000,
        54: '192.168.100.182',
        1: '255.255.255.0',
        3: '192.0.0.0, 192.1.1.1',
        6: '192.168.100.69',
        15: 'TataBaci',
        28: '192.168.128.255',
        58: 7220
    }

class SenderHandler():
    def __init__(self, _conn,_addr, _pool, _lock):
        self.conn = _conn
        self.addr = _addr
        self.pool = _pool
        self.lock = _lock


    def handle(self, message): # a fost start
        #functie de care imi identifica tipul de actiune pe care trebuie sa o iau
        #functie care sa imi returneze ce mesaj sa fie trimis
        type = self.identifieMessage(message.options)

        if type != 0:
            message = self.modifyMessage(type, message)
            self.messageSend(message)

    def identifieMessage(self,options):
        type = 0
        if 53 in options:
            type = options[53]
        else:
            pass
        return type

    def modifyMessage(self, typeOfMessage, message):
        self.lock.acquire()
        if typeOfMessage=='DHCPDISCOVER':
            #sa ai grija si la cazurile in care se retrimite un DHCPDISCOVERY
            message.op = '02'
            oldIp = self.pool.findOldAdress(message.chaddr)
            alocatedAddress = 0
            if oldIp != 0:
                if oldIp.free != 0 and oldIp.hold != 1:
                    #cazul in care se ia o adresa care a fost deja a clientului respectiv
                    message.yiaddr = oldIp.ip
                    oldIp.setMac(message.chaddr)
                    oldIp.holdAddress()
                    alocatedAddress = oldIp
                else:

                    newIp = self.pool.getFreeAddress(message.chaddr)
                    message.yiaddr = newIp.ip
                    alocatedAddress = newIp

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
                    # cazul in care trebuie sa alocam o noua adresa
                    newIp = self.pool.getFreeAddress(message.chaddr)
                    message.yiaddr = newIp.ip
                    alocatedAddress = newIp
            else:
                #cazul in care trebuie sa alocam o noua adresa
                newIp = self.pool.getFreeAddress(message.chaddr)
                message.yiaddr = newIp.ip
                alocatedAddress = newIp

            if 51 in message.options:
                requestedLeaseTime = message.options[51]
                clientIp=self.pool.findAddressMAC(message.chaddr)
                if clientIp !=0 and clientIp.free == 0:
                    requestedLeaseTime = clientIp.leaseTime
                elif True:
                    requestedLeaseTime = configurations[51]
                message.options[51] = requestedLeaseTime
                leaseTime[message.chaddr] = requestedLeaseTime
            else:
                message.options[51] = configurations[51]
                leaseTime[message.chaddr] = configurations[51]

            message.options[53] = 'DHCPOFFER'

            for i in message.options.keys():
                if i != 50 and i != 53 and i != 51:
                    message.options[i] = configurations[i]
                if i == 50 or i == 61 or i == 55:
                    message.pop(i)

            optionSendInDiscovery[message.chaddr] = message.options

        elif typeOfMessage == 'DHCPREQUEST':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            if ipAlocated != 0:
                if 54 in message.options:
                    #mesajul e un raspuns la DHCPOFFER
                    error = "ok"
                    message.options[50] = ipAlocated.ip
                    if ipAlocated.ip == message.options[50] and message.ciaddr == '':
                        #SELECTING STATE
                        #verificam daca cumva mesajul nu este al altui server
                        if configurations[54] != message.options[54]:
                            ipAlocated.releaseAddress()
                            error = "Another server"

                        #daca totul e corect se va construi un mesaj de tip DHCPACK
                        if error == "ok":
                            message.op = '02'
                            message.yiaddr = ipAlocated.ip
                            message.options = optionSendInDiscovery[message.chaddr]
                            message.options[53] = 'DHCPACK'
                            ipAlocated.setAddress()
                else:
                    error = "ok"
                    if message.ciaddr == '': #0.0.0.0 ??
                        # INIT REBOOT
                        if message.options[50] != ipAlocated.ip:
                            error = "Ip doesn't match"
                        tempip = message.options[50]
                        tempip = tempip.split('.')
                        for i in range(0, 3):
                            tempip[i] = int(tempip)
                            if self.pool.invertedMask[i] == 0:
                                if tempip[i] != self.pool.ip[i]:
                                    error = "Not the same network"
                            else:
                                if tempip[i] & (255 - self.pool.invertedMask[i]) != self.pool.ip[i]:
                                    error = "Not the same network"
                        if error == "Ip doesn't match" or error == "Not the same network":
                            message.op = '02'
                            message.yiaddr = ''
                            message.options.clear()
                            message.options[53] = 'DHCPNACK'
                            message.sname = ''
                            message.siaddr = ''
                            message.ciaddr = ''
                            message.file = ''
                            ipAlocated.releaseAddress()
                        else:
                            message = 0

                    elif 50 not in message.options:
                        #extend lease time
                        leaseTime[message.chaddr] = configurations[51]
                        #renewing
            else:
                message = 0

        elif typeOfMessage == 'DHCPDECLINE':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            ipAlocated.unsetAddress()
            message = 0

        elif typeOfMessage == 'DHCPRELEASE':
            #se elibereaza adresa, parametrii de configurare deja sunt salvati in dictionarul de sus
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            ipAlocated.unsetAddress()
            message = 0

        elif typeOfMessage == 'DHCPINFORM':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            message.op = '02'
            message.yiaddr = ''
            message.options = optionSendInDiscovery[message.chaddr]
            message.options.pop(51)
            message.options[53] = 'DHCPACK'
        else:
            pass
            #log error
        self.lock.release()
        return message

    def messageSend(self,message, conn):
        pass
        if message != 0:
            self.conn.sendall(message.code())
