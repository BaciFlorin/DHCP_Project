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
    def __init__(self, _options):
        self.options = _options
        self.OptionsData = {
        1: "Empty",
        3: "Empty",
        6: "Empty",
        15: "Empty",
        28: "Empty",
        53: "Empty",
        54: "Empty",
        58: "Empty"
    }

    def optionSplit(self):
        Index = 2
        if self.options == "":
            print("No options!")
        else:
            while Index < len(self.options):
                code = int(self.options[Index-2:Index], base=10)
                length = int(self.options[Index:Index+2], base=10) * 2
                if code != 1 and code != 3 and code != 6 and code != 15 and code != 28 and code != 53 and code != 54 and code != 58:
                    print("Optiune invalida!")
                self.OptionsData[code] = self.options[Index+2:Index+2+length]
                Index += length + 6

    def ipAddrFormat(self, address):
        if len(address) != 8:
            print("Parametrul primit nu e adresa!")
            return "INVALID"
        else:
            newAddress = "%d.%d.%d.%d" % (int(address[0:2], base=16), int(address[2:4], base=16), int(address[4:6], base=16),int(address[6:8], base=16))
            return newAddress

    def nameFormat(self, name):
        if len(name) == 0:
            return "INVALID"
        else:
            newName = ""
            start = 0
            end = 2
            while end <= len(name):
                newName += chr(int(name[start:end], base=16))
                start = end
                end += 2
            return newName

    def optionDecode(self):
        for i in self.OptionsData:
            if self.OptionsData[i] != "Empty":
                # SUBNET MASK
                if i==1:
                    self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])

                # Router Option
                if i==3:
                    aux = ""
                    startIndex = 0
                    endIndex = 8
                    optionLen = len(self.OptionsData[i])
                    while endIndex <= optionLen:
                        aux += self.ipAddrFormat(self.OptionsData[i][startIndex:endIndex])
                        if endIndex != optionLen:
                            aux += ", "
                        startIndex = endIndex
                        endIndex +=8
                    self.OptionsData[i] = aux

                #Domain Name Server Option
                if i==6:
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

                #Domain Name
                if i==15:
                    self.OptionsData[i] = self.nameFormat(self.OptionsData[i])

                #Broadcast Address Option
                if i==28:
                    self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])

                #DHCP Message Type
                if i==53:
                    self.OptionsData[i] = self.DHCPMessageType[int(self.OptionsData[i],base = 10)]

                #Server Identifier
                if i==54:
                    self.OptionsData[i] = self.ipAddrFormat(self.OptionsData[i])

                #Renewal (T1) Time Value
                if i==58:
                    self.OptionsData[i] = int(self.OptionsData[i],base = 16)












