import time
import logging

message_type = {
    'DHCP_Discover' : '01',
    'DHCP_Offer' : '02',
    'DHCP_Request' : '03',
    'DHCP_Ack' : '04',
    'Indices' : [562,563]
}

class Communication_Level():
    def __init__(self,socket):
        self.socket = socket
        self.level = [False for i in range(0,4)]
        self.data_on_each_level = {
            'discover' : [],
            'offer' : None,
            'request' : None,
            'ack' : None
        }
        self.offer_exists = False
        self.offers = 0

    def decode_message(self,message):
        message_tp = message[message_type['Indices'][0]:message_type['Indices'][1]+1].decode("utf-8")

        def write(self,message,type):
            if type == '01':
                self.data_on_each_level['discover'].append(message)
                self.level[0] = True
                self.offer_exists = True
                self.offers += 1
            elif type == '02':
                self.data_on_each_level['offer'] = message
                self.level[1] = True
            elif type == '03':
                self.data_on_each_level['request'] = message
                self.level[2] = True
            elif type == '04':
                self.data_on_each_level['ack'] = message
                self.level[3] = True

        if message_tp == '01':
            write(self,message,'01')
        elif message_tp == '02':
            write(self,message,'02')
        elif message_tp == '03':
            write(self,message,'03')
        elif message_tp == '04':
            write(self,message,'04')

    def send(self,type):
        if type == 'discover':
            message = self.data_on_each_level['discover'][0]
            sender = SendMessage(message,self.socket)
            sender.sendTo()
        elif type == 'request':
            message = self.data_on_each_level['request']
            sender = SendMessage(message,self.socket)
            sender.sendTo()

    def receive(self,type):
        if type == 'offer':
            message = RecvMessage(self.socket)
            message.get_data()
            self.data_on_each_level['offer'] = message.data
        elif type == 'ack':
            message = RecvMessage(self.socket)
            message.get_data()
            self.data_on_each_level['ack'] = message.data

class SendMessage():
    def __init__(self,message,my_socket):
        self.message = message
        self.mysocket = my_socket
        self.nr_bytes = len(self.message)

    def sendTo(self):
          if self.nr_bytes is not 0:
                try:
                    self.mysocket.send(self.message)
                    print('Trying to send data')
                    time.sleep(0.001)
                except Exception as e:
                    logging.warning(e)
          else:
              print('Message has length 0')

class RecvMessage():
    def __init__(self,my_socket):
        self.socket = my_socket
        self.data = None

    def get_data(self):
        while True:
            self.data = self.socket.recv(1024)
            if len(self.data) is not 0:
                break
        print(self.data)
