import Options
import binascii

class Message:
    fieldDimensions = {
        "op": 1,
        "htype": 1,
        "hlen": 1,
        "hops": 1,
        "xid": 4,
        "secs": 2,
        "flags": 2,
        "ciaddr": 4,
        "yiaddr": 4,
        "siaddr": 4,
        "giaddr": 4,
        "chaddr": 16,
        "sname": 64,
        "file": 128,
        "magic": 4
    }

    def __init__(self, _messageRecived):
        self.messageRecived = _messageRecived
        self.op = ''
        self.htype = ''
        self.hlen = ''
        self.hops = ''
        self.xid = ''
        self.secs = ''
        self.flags = ''
        self.ciaddr = ''
        self.yiaddr = ''
        self.siaddr = ''
        self.giaddr = ''
        self.chaddr = ''
        self.sname = ''
        self.file = ''
        self.magic_cookie = ''
        self.options = {}

    def messageSplit(self):
        startIndex = 0
        endIndex = 0
        #OP
        endIndex += self.fieldDimensions["op"]*2
        self.op = self.messageRecived[startIndex:endIndex]

        #HTYPE
        startIndex = endIndex
        endIndex += self.fieldDimensions["htype"]*2
        self.htype = self.messageRecived[startIndex:endIndex]

        #HLEN
        startIndex = endIndex
        endIndex += self.fieldDimensions["hlen"] * 2
        self.hlen = self.messageRecived[startIndex:endIndex]

        #HOPS
        startIndex = endIndex
        endIndex += self.fieldDimensions["hops"] * 2
        self.hops = self.messageRecived[startIndex:endIndex]

        #XID
        startIndex = endIndex
        endIndex += self.fieldDimensions["xid"] * 2
        self.xid = self.messageRecived[startIndex:endIndex]

        #SECS
        startIndex = endIndex
        endIndex += self.fieldDimensions["secs"] * 2
        self.secs = self.messageRecived[startIndex:endIndex]

        #FLAGS
        startIndex = endIndex
        endIndex += self.fieldDimensions["flags"] * 2
        self.flags = self.messageRecived[startIndex:endIndex]

        #CIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["ciaddr"] * 2
        self.ciaddr = self.messageRecived[startIndex:endIndex]
        self.ciaddr = self.ipAddrFormat(self.ciaddr)
        if self.ciaddr == "INVALID":
            return -1

        #YIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["yiaddr"] * 2
        self.yiaddr = self.messageRecived[startIndex:endIndex]
        self.yiaddr = self.ipAddrFormat(self.yiaddr)
        if self.yiaddr == "INVALID":
            return -1

        #SIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["siaddr"] * 2
        self.siaddr = self.messageRecived[startIndex:endIndex]
        self.siaddr = self.ipAddrFormat(self.siaddr)
        if self.siaddr == "INVALID":
            return -1

        #GIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["giaddr"] * 2
        self.giaddr = self.messageRecived[startIndex:endIndex]
        self.giaddr = self.ipAddrFormat(self.giaddr)
        if self.giaddr == "INVALID":
            return -1

        #CHADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["chaddr"] * 2
        self.chaddr = self.messageRecived[startIndex:endIndex]
        self.chaddr = self.ipMacFormat(self.chaddr)
        if self.chaddr == "INVALID":
            return -1

        #SNAME
        startIndex = endIndex
        endIndex += self.fieldDimensions["sname"] * 2
        self.sname = self.messageRecived[startIndex:endIndex]
        self.sname = self.nameFormat(self.sname)
        if self.sname == "INVALID":
            return -1

        #FILE
        startIndex = endIndex
        endIndex += self.fieldDimensions["file"] * 2
        self.file = self.messageRecived[startIndex:endIndex]
        self.file = self.nameFormat(self.file)
        if self.file == "INVALID":
            return -1

        # MAGIC COOKIE
        startIndex = endIndex
        endIndex += self.fieldDimensions["magic"] * 2
        self.magic_cookie = self.messageRecived[startIndex:endIndex]

        #OPTIONS
        startIndex = endIndex
        endIndex += len(self.messageRecived) - 236
        Opt = Options.Options(self.messageRecived[startIndex:endIndex])
        Opt.optionSplit()
        Opt.optionDecode()
        self.options = Opt.OptionsData

        for option in self.options:
            if self.options[option] == "INVALID":
                return -1
        return 0

    def ipAddrFormat(self, address):
        if len(address) != 8:
            return "INVALID"
        else:
            newAddress = "%d.%d.%d.%d" % (int(address[0:2], base=16), int(address[2:4], base=16), int(address[4:6], base=16), int(address[6:8], base=16))
            return newAddress

    def ipAddrFormatToHex(self, address):
        aux = address.split(".")
        if len(aux) == 4:
            newAddress = ""
            for i in range(4):
                # Ne folosim de int(aux[n], base = 10) unde n = 0,3 pentu a transfomra fiecare octet al adresei pe care l-am separat cu split(".") din string in numar intreg
                # Transformam din numar intreg in numar hexazecimal folosind hex(n) apoi taiem primele 2 caractere pentu ca functia hex returneaza un numar de forma 0xAA si noi avem nevoie doar de AA.
                data = hex(int(aux[i], base=10))[2:]
                if int(data, base=16) < 0x10:
                    data = "0" + data
                newAddress += data
            return newAddress
        else:
            return ''

    def ipMacFormatToHex(self, address):
        aux = address.split(":")
        if len(aux) == 6:
            newAddress = ""
            for i in range(6):
                newAddress += aux[i]
            # Adaugam zerouri pentru a pastra lungimea data de documentatie
            while len(newAddress) != 32:
                newAddress += "0"
            return newAddress
        else:
            return ''

    def ipMacFormat(self, address):
        # Adresa MAC are doar 6 octeti dar in mesaj are alocat 16 octeti
        if len(address) != 32:
            return "INVALID"
        else:
            # newAddress = "%s:%s:%s:%s:%:%s" %
            # (address[0:2], address[2:4], address[4:6],address[6:8],address[8:10],address[10:12])
            newAddress = address[0:2] + ":" + address[2:4] + ":" + address[4:6] + ":" + address[6:8] + ":" + address[8:10] + ":" + address[10:12]
            return newAddress

    def nameFormat(self,name):
        if len(name) == 0:
            return "INVALID"
        else:
            newName = ""
            start = 0
            end = 2
            while name[start:end] != "00" and end <= len(name):
                newName += chr(int(name[start:end], base=16))
                start = end
                end += 2
            return newName

    def nameFormatToASCIIHex(self, name):
        if name and len(name) < 128:
            name = bytearray(name, encoding="utf-8")
            name = binascii.hexlify(name)
            name = name.decode("utf-8")
            return name
        else:
            return ''

    def encode(self):
        # aceste parti din mesaj nu au fost decodificate asa ca le putem concatena fara alte modificari
        encoded = self.op + self.htype + self.hlen + self.hops + self.xid + self.secs + self.flags

        # Convertim adresele IP folosind functia ipAddrFormatToHex si concatenam la sir
        encoded += self.ipAddrFormatToHex(self.ciaddr) + self.ipAddrFormatToHex(self.yiaddr) + self.ipAddrFormatToHex(self.siaddr) + self.ipAddrFormatToHex(self.giaddr)

        # Convertim adresa MAC folosind functia ipMacFormatToHex si concatenam la sir
        encoded += self.ipMacFormatToHex(self.chaddr)

        # Adaugam un numar de caractere "goale" adica 0 pentru a pastra dimensiunea data de standard
        encoded += self.nameFormatToASCIIHex(self.sname) + '00' * (64 - len(self.sname))
        encoded += self.nameFormatToASCIIHex(self.file) + (128 - len(self.file)) * '00'

        # Adaugam magic cookie
        encoded += self.magic_cookie

        for option in self.options:
            if option == 1:
                length = len(self.ipAddrFormatToHex(self.options[option])) / 2
                encoded += "0" + str(option) + "0" + str(int(length)) + self.ipAddrFormatToHex(
                    self.options[option])

            # Router Option
            if option == 3:
                aux = self.options[option].split(" ")
                length = 0
                buff = ""
                for i in range(0, len(aux)):
                    buff += self.ipAddrFormatToHex(aux[i])
                    length += len(self.ipAddrFormatToHex(aux[i]))
                encoded += "0" + str(option) + "0" + str(int(length / 2)) + buff

            # Domain Name Server Option
            if option == 6:
                aux = self.options[option].split(" ")
                length = 0
                buff = ""
                for i in range(0, len(aux)):
                    buff += self.ipAddrFormatToHex(aux[i])
                    length += len(self.ipAddrFormatToHex(aux[i]))
                encoded += "0" + str(option) + "0" + str(int(length / 2)) + buff

            # Domain Name
            if option == 15:
                length = len(self.options[option])
                code = "0" + str(hex(option))[2:]
                if length < 10:
                    encoded += code + "0" + str(length) + self.nameFormatToASCIIHex(self.options[option])
                else:
                    encoded += code + str(length) + self.nameFormatToASCIIHex(self.options[option])

            # Broadcast Address Option
            if option == 28:
                length = len(self.ipAddrFormatToHex(self.options[option])) / 2
                encoded += str(hex(option))[2:] + "0" + str(int(length)) + self.ipAddrFormatToHex(
                    self.options[option])

            # IP Address Lease Time
            if option == 51:
                time = str(hex(self.options[option]))[2:]
                dim = len(time)
                while dim < 8:
                    time = "0" + time
                    dim += 1
                encoded += str(hex(option))[2:] + "04" + time

            # DHCP Message Type
            if option == 53:
                DHCPMessageTypeEncode = {
                    "DHCPDISCOVER": 1,
                    "DHCPOFFER": 2,
                    "DHCPREQUEST": 3,
                    "DHCPDECLINE": 4,
                    "DHCPACK": 5,
                    "DHCPNAK": 6,
                    "DHCPRELEASE": 7,
                    "DHCPINFORM": 8
                }
                encoded += str(hex(option))[2:] + "01" + "0" + str(DHCPMessageTypeEncode[self.options[option]])

            # Server Identifier
            if option == 54:
                length = len(self.ipAddrFormatToHex(self.options[option])) / 2
                encoded += str(hex(option))[2:] + "0" + str(int(length)) + self.ipAddrFormatToHex(
                    self.options[option])

            # Renewal (T1) Time Value
            if option == 58:
                time = str(hex(self.options[option]))[2:]
                dim = len(time)
                while dim < 8:
                    time = "0" + time
                    dim += 1
                encoded += hex(option)[2:] + "04" + time

        encoded += "ff"
        # Transformam din string in Bytes
        encoded = bytearray(encoded.upper(), encoding="utf-8")
        return encoded

    def message_to_string(self):
        string_message = ""
        string_message += "Message type:" + self.op + "\n"
        string_message += "Hardware type:" + self.hlen + "\n"
        string_message += "Hops:" + self.hops + "\n"
        string_message += "Transaction ID:" + self.xid + "\n"
        string_message += "Second elapsed:" + str(self.secs) + "\n"
        string_message += "Bootp flags:" + self.flags + "\n"
        string_message += "Client IP address:" + self.ciaddr + "\n"
        string_message += "Your (client) IP address:" + self.yiaddr + "\n"
        string_message += "Next server IP address:" + self.siaddr + "\n"
        string_message += "Relasy agent IP address:" + self.giaddr + "\n"
        string_message += "Client MAC address:" + self.chaddr + "\n"
        string_message += "Server host name:" + self.sname + "\n"
        string_message += "Boot file name:" + self.file + "\n"
        string_message += "Options:" + "\n"
        for option in self.options.keys():
            string_message += "\t" + str(option) + ":" + str(self.options[option]) + "\n"
        return string_message









