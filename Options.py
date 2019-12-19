import logging
logger = logging.getLogger("console_logger")

available_options = [1, 3, 6, 15, 28, 58, 53, 51, 54, 55, 50]

class Options:
    DHCPMessageType = {
        1: "DHCPDISCOVER",
        2: "DHCPOFFER",
        3: "DHCPREQUEST",
        4: "DHCPDECLINE",
        5: "DHCPACK",
        6: "DHCPNAK",
        7: "DHCPRELEASE",
        8: "DHCPINFORM"
    }
    def __init__(self, _options, _indicator):
        self.options = _options
        self.OptionsData = {}
        self.indicator = _indicator

    def optionSplit(self):
        Index = 2
        if self.options == "":
            logger.info(self.indicator + ":No options!")
        else:
            while Index < len(self.options):
                code = int(self.options[Index-2:Index], base=10)
                length = int(self.options[Index:Index+2], base=10) * 2
                if code in available_options:
                    self.OptionsData[code] = self.options[Index+2:Index+2+length]
                Index += length + 6
            self.optionDecode()

    def ipAddrFormat(self, address):
        if len(address) != 8:
            logger.error(self.indicator + ":" + address + " is not an ip address!")
            return "INVALID"
        else:
            newAddress = "%d.%d.%d.%d" % (int(address[0:2], base=16), int(address[2:4], base=16), int(address[4:6], base=16),int(address[6:8], base=16))
            return newAddress

    def nameFormat(self, name):
        if len(name) == 0:
            logger.error(self.indicator + ":No name in message!")
            return "INVALID"
        else:
            try:
                newName = ""
                start = 0
                end = 2
                while end <= len(name):
                    newName += chr(int(name[start:end], base=16))
                    start = end
                    end += 2
                return newName
            except:
                return "INVALID"

    def optionDecode(self):
        for i in self.OptionsData:
            # SUBNET MASK
            if i == 1:
                self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])

            # Router Option
            if i == 3:
                aux = ""
                startIndex = 0
                endIndex = 8
                optionLen = len(self.OptionsData[i])
                while endIndex <= optionLen:
                    aux += self.ipAddrFormat(self.OptionsData[i][startIndex:endIndex])
                    if endIndex != optionLen:
                        aux += ", "
                    startIndex = endIndex
                    endIndex += 8
                self.OptionsData[i] = aux

            # Domain Name Server Option
            if i == 6:
                aux = ""
                startIndex = 0
                endIndex = 8
                optionLen = len(self.OptionsData[i])
                while endIndex <= optionLen:
                    aux += self.ipAddrFormat(self.OptionsData[i][startIndex:endIndex])
                    if endIndex != optionLen:
                        aux += ", "
                    startIndex = endIndex
                    endIndex += 8
                self.OptionsData[i] = aux

            # Domain Name
            if i == 15:
                self.OptionsData[i] = self.nameFormat(self.OptionsData[i])

            # Broadcast Address Option
            if i == 28:
                self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])
            # Requested IP Address
            if i == 50:
                self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])
            # Lease Time
            if i == 51:
                try:
                    self.OptionsData[i] = int(self.OptionsData[i], base=10)
                except:
                    logger.error(self.indicator + ":Value at option 51 is not valid!")
                    self.OptionsData[i] = 'INVALID'

            # DHCP Message Type
            if i == 53:
                try:
                    self.OptionsData[i] = self.DHCPMessageType[int(self.OptionsData[i], base=10)]
                except:
                    logger.error(self.indicator + ":Value at oprion 53 is not valid!")
                    self.OptionsData[i] = 'INVALID'

            # Server Identifier
            if i == 54:
                self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])

            # Renewal (T1) Time Value
            if i == 58:
                try:
                    self.OptionsData[i] = int(self.OptionsData[i],base = 16)
                except:
                    logger.error(self.indicator + ":Value at oprion 58 is not valid!")
                    self.OptionsData[i] = 'INVALID'












