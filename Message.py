import Options
import logging

logger = logging.getLogger("console_logger")

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
    }

    def __init__(self, _messageRecived):
        self.messageRecived = _messageRecived
        self.op = 0
        self.htype = 0
        self.hlen = 0
        self.hops = 0
        self.xid = 0
        self.secs = 0
        self.flags = 0
        self.ciaddr = 0
        self.yiaddr = 0
        self.siaddr = 0
        self.giaddr = 0
        self.chaddr = 0
        self.sname = 0
        self.file = 0
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
        self.flags =  self.messageRecived[startIndex:endIndex]
        #CIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["ciaddr"] * 2
        self.ciaddr = self.messageRecived[startIndex:endIndex]
        self.ciaddr = self.ipAddrFormat(self.ciaddr)
        #YIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["yiaddr"] * 2
        self.yiaddr = self.messageRecived[startIndex:endIndex]
        self.yiaddr = self.ipAddrFormat(self.yiaddr)
        #SIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["siaddr"] * 2
        self.siaddr = self.messageRecived[startIndex:endIndex]
        self.siaddr = self.ipAddrFormat(self.siaddr)
        #GIADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["giaddr"] * 2
        self.giaddr =  self.messageRecived[startIndex:endIndex]
        self.giaddr = self.ipAddrFormat(self.giaddr)
        #CHADDR
        startIndex = endIndex
        endIndex += self.fieldDimensions["chaddr"] * 2
        self.chaddr = self.messageRecived[startIndex:endIndex]
        self.chaddr = self.ipMacFormat(self.chaddr)
        #SNAME
        startIndex = endIndex
        endIndex += self.fieldDimensions["sname"] * 2
        self.sname = self.messageRecived[startIndex:endIndex]
        self.sname = self.nameFormat(self.sname)
        #FILE
        startIndex = endIndex
        endIndex += self.fieldDimensions["file"] * 2
        self.file =  self.messageRecived[startIndex:endIndex]
        self.file = self.nameFormat(self.file)
        #OPTIONS
        startIndex = endIndex
        endIndex += len(self.messageRecived) - 236
        options = Options.Options(self.messageRecived[startIndex:endIndex], self.xid)
        options.optionSplit()
        self.options = options.OptionsData

        err = self.verifyMessage()
        if err == -1:
            return -1
        else:
            return 0

    def ipAddrFormat(self, address):
        if len(address) != 8:
            logger.error(str(self.xid) + ":" + str(address) + "is not a valid ip address!")
            return "INVALID"
        else:
            try:
                newAddress = "%d.%d.%d.%d" % (int(address[0:2], base=16), int(address[2:4], base=16), int(address[4:6],
                                                base=16), int(address[6:8], base=16))
            except:
                logger.error(str(self.xid) + ":" + address + "could't be converted in 16 base numbers!")
                newAddress = 'INVALID'
            return newAddress

    def ipMacFormat(self,address):
        if len(address) != 32: #Adresa MAC are doar 6 octeti dar in mesaj are alocat 16 octeti
            logger.error(str(self.xid) + ":" + address + "is not a valid mac address!")
            return "INVALID"
        else:
            newAddress = "%s-%s-%s-%s-%s-%s" % (address[0:2], address[2:4], address[4:6], address[6:8], address[8:10], address[10:12])
            return newAddress

    def nameFormat(self, name):
        if len(name) == 0:
            logger.error(str(self.xid) + ":No name in message!")
            return "INVALID"
        else:
            newName = ""
            start = 0
            end = 2
            while name[start:end] != "20" and end<=len(name):
                newName += chr(int(name[start:end], base=16))
                start = end
                end += 2
            return newName

    def verifyMessage(self):
        if self.ciaddr == 'INVALID' or self.yiaddr == 'INVALID' or self.siaddr == 'INVALID' or self.giaddr == 'INVALID' or  self.chaddr == 'INVALID' or self.sname == 'INVALID' or self.file == 'INVALID':
            return -1
        for oprtion in self.options.keys():
            if self.options[oprtion] == 'INVALID':
                return -1

