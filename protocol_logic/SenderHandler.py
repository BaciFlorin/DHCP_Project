import logging

logger = logging.getLogger("console_logger")


class SenderHandler:
    optionSendInDiscovery = {}
    leaseTime = {}
    configurations = {}
        
    def __init__(self, _conn, _addr, _pool, _lock, _configurations):
        self.conn = _conn
        self.addr = _addr
        self.pool = _pool
        self.lock = _lock
        self.configurations = _configurations

    def handle(self, message, clients_display):
        if self.get_type_of_message(message.options) != '':
            message = self.change_message_for_send(self.get_type_of_message(message.options), message, clients_display)
        else:
            logger.critical("Type option is not in message!")
            return 'INVALID'
        return message

    def get_type_of_message(self, options):
        return options[53]

    def change_message_for_send(self, type_of_message, message, clients_display):
        self.lock.acquire()

        if type_of_message == 'DHCPDISCOVER':
            message.op = '02'
            message.yiaddr = self.pool.get_a_new_ip_for_client(message.chaddr, message.options)
            logger.info("Client gets the this ip:" + message.yiaddr + "!")

            if 51 in message.options:
                requested_lease_time = int(message.options[51])
                if 1000 > requested_lease_time > 8000:
                    requested_lease_time = self.configurations[51]
                message.options[51] = requested_lease_time
                self.leaseTime[message.chaddr] = requested_lease_time
            else:
                if message.chaddr in self.leaseTime:
                    message.options[51] = self.leaseTime[message.chaddr]
                else:
                    message.options[51] = self.configurations[51]
            logger.info("Client got this lease time:" + str(message.options[51]) + "!")

            # change type of message
            message.options[53] = 'DHCPOFFER'

            # server identifier
            message.options[54] = self.configurations[54]

            # configure the other options
            if 55 in message.options:
                for option in message.options[55]:
                    if option in self.configurations:
                        message.options[option] = self.configurations[option]
            else:
                for i in message.options.keys():
                    if i in self.configurations:
                        message.options[i] = self.configurations[i]

            # remove useless option
            for roption in [option for option in message.options if option not in self.configurations and option != 53 and option != 51 and option != 54]:
                    message.options.pop(roption)

            # save options send for the future use
            self.optionSendInDiscovery[message.chaddr] = message.options
            logger.info(" DHCPOFFER ready to transmit!")

        elif type_of_message == 'DHCPREQUEST':
            ip_allocated = self.pool.find_ip_after_mac(message.chaddr)
            if ip_allocated != "":
                if 54 in message.options:
                    if ip_allocated.ip == message.options[50] and message.ciaddr == '0.0.0.0':
                        # SELECTING STATE
                        if self.configurations[54] != message.options[54]:
                            logger.info("Message received is for another server!")
                            ip_allocated.releaseAddress()
                            return 'INVALID'

                        message.op = '02'
                        message.yiaddr = ip_allocated.ip
                        message.options = self.optionSendInDiscovery[message.chaddr]
                        message.options[53] = 'DHCPACK'
                        ip_allocated.make_ip_unavailable()
                        logger.info("DHCPACK ready to transmit!")
                        clients_display.add_client(message.xid, message.chaddr, message.yiaddr)
                    else:
                        logger.error("Selecting state:Requested ip from options is not the same with the one assigned!")
                        return 'INVALID'
                else:
                    if message.ciaddr == '0.0.0.0':
                        # INIT REBOOT
                        error = "ok"
                        if message.options[50] != ip_allocated.ip:
                            error = "Ip doesn't match"
                            logger.info("Init reboot state: Requested ip doesn't match!")

                        if error == "Ip doesn't match":
                            message.op = '02'
                            message.yiaddr = '0.0.0.0'
                            message.options.clear()
                            message.options[53] = 'DHCPNAK'
                            message.options[54] = self.configurations[54]
                            message.sname = ''
                            message.siaddr = '0.0.0.0'
                            message.ciaddr = '0.0.0.0'
                            message.file = ''
                            ip_allocated.release_address()
                            logger.info("DHCPNAK ready to transmit!")
                        else:
                            logger.info("Init Reboot: Everything is fine!")
                            message = ''

                    elif 50 not in message.options:
                        logger.info("Renwing state: Lease time updated!")
                        self.leaseTime[message.chaddr] = self.configurations[51]
                        message = ''
            else:
                logger.info("No ip found in address pool for this mac address!")
                return 'INVALID'

        elif type_of_message == 'DHCPDECLINE':
            if message.options[54] == self.configurations[54]:
                ip_allocated = self.pool.find_ip_after_mac(message.chaddr)
                ip_allocated.make_ip_available()
                message = 'INVALID'
                logger.info("IP address was released and connection closed!")

        elif type_of_message == 'DHCPRELEASE':
            ip_allocated = self.pool.find_ip_after_mac(message.chaddr)
            ip_allocated.make_ip_available()
            message = 'INVALID'
            logger.info("IP address was released and connection closed!")

        elif type_of_message == 'DHCPINFORM':
            ip_allocated = self.pool.find_ip_after_mac(message.chaddr)
            message.op = '02'
            message.yiaddr = ip_allocated.ip
            message.options = self.optionSendInDiscovery[message.chaddr]
            message.options.pop(51)
            message.options[53] = 'DHCPACK'
            logger.info("Message ready to transmit, client will be inform about his configurations!")
        self.lock.release()
        return message

    def messageSend(self, message, conn):
        if message != '':
            conn.sendall(message.encode())
