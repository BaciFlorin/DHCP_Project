import logging

logger = logging.getLogger("console_logger")

class SenderHandler():
    optionSendInDiscovery = {}
    leaseTime = {}
    configurations = {}
    
    
    def __init__(self, _conn,_addr, _pool, _lock, _configurations):
        self.conn = _conn
        self.addr = _addr
        self.pool = _pool
        self.lock = _lock
        self.indicator = ''
        self.configurations = _configurations


    def handle(self, message): # a fost start
        #functie de care imi identifica tipul de actiune pe care trebuie sa o iau
        #functie care sa imi returneze ce mesaj sa fie trimis
        type = self.identifieMessage(message.options)
        if type != '':
            self.indicator = str(message.xid)
            message = self.modifyMessage(type, message)
        else:
            logger.critical(self.indicator + ":Type option is not in message!")
            return 'INVALID'
        return message

    def identifieMessage(self,options):
        type = ''
        if 53 in options:
            type = options[53]
        return type

    def modifyMessage(self, typeOfMessage, message):
        self.lock.acquire()
        if typeOfMessage=='DHCPDISCOVER':
            #sa ai grija si la cazurile in care se retrimite un DHCPDISCOVERY
            message.op = '02'
            oldIp = self.pool.findOldAdress(message.chaddr)
            if oldIp != 0:
                if oldIp.free != 0 and oldIp.hold != 1:
                    #cazul in care se ia o adresa care a fost deja a clientului respectiv
                    message.yiaddr = oldIp.ip
                    oldIp.setMac(message.chaddr)
                    oldIp.holdAddress()
                    logger.info(self.indicator + ":DHCPDISCOVER:Client gets the old ip:" + oldIp.ip)
                else:
                    newIp = self.pool.getFreeAddress(message.chaddr)
                    message.yiaddr = newIp.ip
                    newIp.setMac(message.chaddr)
                    newIp.holdAddress()
                    logger.info(self.indicator + ":DHCPDISCOVER:Client's old ip is not free and it gets the new ip:"+newIp.ip)

            elif 50 in message.options:
                requestedIp = self.pool.findAddressIP(message.options[50])
                if requestedIp != 0:
                    if requestedIp.free == 1 and requestedIp.hold == 0:
                        message.yiaddr = requestedIp.ip
                        requestedIp.setMac(message.chaddr)
                        requestedIp.holdAddress()
                        logger.info(self.indicator + ":DHCPDISCOVER:Client gets the requested ip:" + requestedIp.ip)
                    else:
                        newIp = self.pool.getFreeAddress(message.chaddr)
                        message.yiaddr = newIp.ip
                        newIp.setMac(message.chaddr)
                        newIp.holdAddress()
                        logger.info(self.indicator + ":DHCPDISCOVER:Client's requested ip is not free and it gets the new ip:" + newIp.ip)
                else:
                    newIp = self.pool.getFreeAddress(message.chaddr)
                    message.yiaddr = newIp.ip
                    newIp.setMac(message.chaddr)
                    newIp.holdAddress()
                    logger.info(self.indicator + ":DHCPDISCOVER:Client's requested ip is from another address space and it gets the new ip:" + newIp.ip)
            else:
                newIp = self.pool.getFreeAddress(message.chaddr)
                message.yiaddr = newIp.ip
                newIp.setMac(message.chaddr)
                newIp.holdAddress()
                logger.info(self.indicator + ":DHCPDISCOVER:Client gets the new ip:" + newIp.ip)

            if 51 in message.options:
                requestedLeaseTime = int(message.options[51])
                if requestedLeaseTime >1000 and requestedLeaseTime<80000:
                    logger.info(self.indicator + ":DHCPDISCOVER:Client's requested lease time(" + str(requestedLeaseTime) + ") is a valid value!")
                else:
                    logger.info(self.indicator + ":DHCPDISCOVER:Client's requested lease time(" + str(requestedLeaseTime) + ") is not a valid value!")
                    requestedLeaseTime = self.configurations[51]
                message.options[51] = requestedLeaseTime
                self.leaseTime[message.chaddr] = requestedLeaseTime
            else:
                if message.chaddr in self.leaseTime:
                    logger.info(self.indicator + ":DHCPDISCOVER:Client gets a valid old lease time!")
                    message.options[51] = self.leaseTime[message.chaddr]
                else:
                    logger.info(self.indicator + ":DHCPDISCOVER:Client gets a default value!")
                    message.options[51] = self.configurations[51]

            message.options[53] = 'DHCPOFFER'

            remove_options = [50, 61, 55]
            for i in message.options.keys():
                if i != 50 and i != 53 and i != 51 and i in self.configurations:
                    message.options[i] = self.configurations[i]
                else:
                    if i != 50 and i != 53 and i != 51:
                        remove_options.append(i)

            for roption in remove_options:
                if roption in message.options.keys():
                    message.options.pop(roption)

            self.optionSendInDiscovery[message.chaddr] = message.options
            logger.info(self.indicator + ":DHCPDISCOVER:DHCPOFFER ready to transmit!")

        elif typeOfMessage == 'DHCPREQUEST':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            if ipAlocated != 0:
                if 54 in message.options:
                    #mesajul e un raspuns la DHCPOFFER
                    message.options[50] = ipAlocated.ip
                    if ipAlocated.ip == message.options[50] and message.ciaddr == '0.0.0.0':
                        #SELECTING STATE
                        #verificam daca cumva mesajul nu este al altui server
                        if self.configurations[54] != message.options[54]:
                            logger.info(self.indicator + ":DHCPREQUEST: Message for another server!")
                            ipAlocated.releaseAddress()
                            return 'INVALID'

                        message.op = '02'
                        message.yiaddr = ipAlocated.ip
                        message.options = self.optionSendInDiscovery[message.chaddr]
                        message.options[53] = 'DHCPACK'
                        ipAlocated.setAddress()
                        logger.info(self.indicator + ":DHCPREQUEST: DHCPACK ready to transmit!")
                else:
                    if message.ciaddr == '0.0.0.0':
                        # INIT REBOOT
                        error = "ok"
                        if message.options[50] != ipAlocated.ip:
                            logger.info(self.indicator
                                            + ":DHCPREQUEST: Init reboot, ip doesn't match!")
                            error = "Ip doesn't match"
                        tempip = message.options[50]
                        tempip = tempip.split('.')
                        for i in range(0, 3):
                            tempip[i] = int(tempip)
                            if self.pool.invertedMask[i] == 0:
                                if tempip[i] != self.pool.ip[i]:
                                    logger.info(self.indicator
                                                    + ":DHCPREQUEST: Init reboot, diferent networks!")
                                    error = "Not the same network"
                                    break
                            else:
                                if tempip[i] & (255 - self.pool.invertedMask[i]) != self.pool.ip[i]:
                                    error = "Not the same network"
                                    logger.info(self.indicator
                                                    + ":DHCPREQUEST: Init reboot, different networks!")
                                    break
                        if error == "Ip doesn't match" or error == "Not the same network":
                            message.op = '02'
                            message.yiaddr = '0.0.0.0'
                            message.options.clear()
                            message.options[53] = 'DHCPNACK'
                            message.sname = ''
                            message.siaddr = '0.0.0.0'
                            message.ciaddr = '0.0.0.0'
                            message.file = ''
                            ipAlocated.releaseAddress()
                            logger.info(self.indicator + ":DHCPREQUEST: DHCPNAK ready to transmit!")
                        else:
                            message = ''

                    elif 50 not in message.options:
                        logger.info(self.indicator + ":DHCPREQUEST: Renwing, lease time renew!")
                        self.leaseTime[message.chaddr] = self.configurations[51]
                        message = ''
            else:
                logger.info(self.indicator
                                + ":DHCPREQUEST:No ip found in address pool for this mac address!")
                return 'INVALID'

        elif typeOfMessage == 'DHCPDECLINE':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            ipAlocated.unsetAddress()
            message = 'INVALID'
            logger.info(self.indicator
                            + ":DHCPDECLINE: IP address was released and connection closed!")

        elif typeOfMessage == 'DHCPRELEASE':
            #se elibereaza adresa, parametrii de configurare deja sunt salvati in dictionarul de sus
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            ipAlocated.unsetAddress()
            message = 'INVALID'
            logger.info(self.indicator
                            + ":DHCPRELEASE: IP address was released and connection closed!")

        elif typeOfMessage == 'DHCPINFORM':
            ipAlocated = self.pool.findAddressMAC(message.chaddr)
            message.op = '02'
            message.yiaddr = ipAlocated.ip
            message.options = self.optionSendInDiscovery[message.chaddr]
            message.options.pop(51)
            message.options[53] = 'DHCPACK'
            logger.info(self.indicator + ":DHCPINFORM: Message ready to transmit!")
        else:
            logger.info(self.indicator + "No type known!")
            return 'INVALID'
        self.lock.release()
        return message


    def messageSend(self,message, conn):
        pass
        if message != '':
            pass
            # self.conn.sendall(message.code())

