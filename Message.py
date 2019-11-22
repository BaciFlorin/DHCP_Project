
class Message:
    def __init__(self,_op,_htype,_len,_hops,_xid,_secs,_flags,_ciaddr,_yiaddr,_siaddr,_giaddr,_chaddr,_sname,_file,_options):
        self.op=_op
        self.len=_len
        self.hops=_hops
        self.xid=_xid
        self.secs=_secs
        self.flags=_flags
        self.ciaddr=_ciaddr
        self.yiaddr=_yiaddr
        self.siaddr=_siaddr
        self.giaddr=_giaddr
        self.chaddr=_chaddr
        self.sname=_sname
        self.file=_file
        self.options=_options

    def convertToBytes(self):
        result=[]
        #unde ai mai multi bytes ar trebui sa ii iei pe fiecare si sa ii imparti
        result.append(self.op)
        result.append(self.len)
        result.append(self.hops)
        result.append(self.xid)
        result.append(self.secs)
        result.append(self.flags)
        result.append(self.ciaddr)
        result.append(self.yiaddr)
        result.append(self.siaddr)
        result.append(self.giaddr)
        result.append(self.chaddr)
        result.append(bytes(self.sname,"utf-8"))
        result.append(bytes(self.file,"utf-8"))
        #for x in self.options:
            #result.append(x)
        return result
