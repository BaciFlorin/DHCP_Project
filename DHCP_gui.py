from tkinter import *
from tkinter import scrolledtext
import socket
import threading
import SenderHandler
import AddressPool
import Message
import queue
from Logging import *

class DHCP_gui():
    def __init__(self, _master):
        self.frameWidth = 500
        self.frameHeight = 500
        self.master = _master
        self.initWindow()
        self.stop_threads = False

    def initWindow(self):

        label2 = Label(self.master, text="Adresa retea:", font="Arial", width=10)
        label2.grid(row=0, column=0, pady=5)

        self.addr = Entry(self.master, width=25)
        self.addr.grid(row=0, column=1, padx=3, sticky=W)

        label3 = Label(self.master, text="Masca:", font="Arial", width=10)
        label3.grid(row=0, column=2, pady=5, sticky=W, padx=2)

        self.mask = Entry(self.master, width=25)
        self.mask.grid(row=0, column=3, sticky=W, padx=2)

        label4 = Label(self.master, text="Lease Time:", font="Arial", width=14)
        label4.grid(row=1, column=0, pady=10)

        self.leaseTime = Entry(self.master, width=25)
        self.leaseTime.grid(row=1, column=1, padx=2, sticky=W)

        self.scrolled_text = scrolledtext.ScrolledText(self.master, state='disabled', height=12, width=50)
        self.scrolled_text.grid(row=4, column=0, sticky=(N, S, W, E), columnspan=30, padx=20, pady=20)
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='black')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.master.after(100, self.poll_log_queue)

        self.master.title("DHCP server")
        self.quitButton = Button(self.master, text="Quit", command=self.exitServer)
        self.quitButton.grid(column=0, row=6)
        self.startButton = Button(self.master, text="Start", command=self.start_server)
        self.startButton.grid(column=20, row=6)

    def exitServer(self):
        if self.startButton["text"] == "Stop":
            self.stop_server()
        for handler in file_logger.handlers:
            if handler is logging.FileHandler:
                handler.close()
        exit()

    def start_server(self):
        if self.checkEntries():
            self.stop_threads = False
            self.startButton["text"] = "Stop"
            self.startButton["command"] = self.stop_server

            self.pool = AddressPool.AddressPool(self.addr.get(), self.mask.get())
            self.lock = threading.Lock()
            self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hostname = socket.gethostname()
            ipAddress = socket.gethostbyname(hostname)
            self.mainSocket.bind(('127.0.0.1', 5000))
            logger.info("Wait for connection....")
            try:
                threading.Thread(target=self.wait_connection).start()
            except:
                logger.fatal("Thread for wainting a connection couldn't start!")
                self.pool = 0
                self.mainSocket.close()

    def stop_server(self):
        self.stop_threads = True
        self.mainSocket.close()
        self.pool = 0
        self.lock = 0
        self.startButton["text"] = "Start"
        self.startButton["command"] = self.start_server
        logger.info("Server stopped!")

    def wait_connection(self):
        self.mainSocket.listen(1)
        while 1:
            try:
                conn, addr = self.mainSocket.accept()
            except KeyboardInterrupt:
                break
            logger.log(logging.INFO, 'S-a conectat:' + str(addr) + "!")
            try:
                threading.Thread(target=self.com_thread, args=(conn, addr, self.pool, self.lock)).start()
            except:
                logger.log(logging.FATAL, "Thread for the client" + str(addr) + " couldn't start!")

    def com_thread(self,conn, addr, pool, lock):
        messageHandler = SenderHandler.SenderHandler(conn, addr, pool, lock)
        while 1:
            data = conn.recv(4096)
            if data:
                data = data.decode("utf-8")
                message = Message.Message(data)
                err = message.messageSplit()
                if err == -1:
                    conn.close()
                    break
                file_logger.info("RECEIVE:\n" + messageToString(message))
                message = messageHandler.handle(message)
                if message == 'INVALID':
                    logger.info(str(message.xid)+": Connection closed!")
                    conn.close()
                    break
                file_logger.info("SEND:\n" + messageToString(message))
                messageHandler.messageSend(message, conn)
                if self.stop_threads:
                    logger.info(str(message.xid) + ": Thread terminated and connection closed!")
                    conn.close()
                    break

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                msg = self.queue_handler.format(record)
                self.scrolled_text.configure(state='normal')
                self.scrolled_text.insert(END, msg + '\n', record.levelname)
                self.scrolled_text.configure(state='disabled')
                # Autoscroll to the bottom
                self.scrolled_text.yview(END)
        self.master.after(100, self.poll_log_queue)


    def checkEntries(self):
        ok = True
        ip = self.addr.get()
        mask = self.mask.get()
        leaseTime = self.leaseTime.get()
        ip = ip.split('.')
        if len(ip) != 4:
            logger.error("Invalid length of network address!")
            ok = False
        else:
            for number in ip:
                try:
                    nr = int(number)
                    if nr > 255:
                        ok = False
                        logger.error("Network address:" + str(number) + " out of range!")
                except:
                    ok = False
                    logger.error("Network address:"+str(number)+" is not a number!")
        mask = mask.split('.')
        if len(mask) != 4:
            logger.error("Invalid length of network mask!")
            ok = False
        else:
            suma = 0
            validNumber = []
            for x in range(7, 0, -1):
                suma += pow(2, x)
                validNumber.append(suma)
            index = -1
            for ind in range(0, 3):
                try:
                    nr = int(mask[ind])
                    if nr != 255 and nr != 0:
                        if nr not in validNumber:
                            logger.error("Network mask:" + mask[ind]
                                       + " is not a valid value for mask!")
                            ok = False
                        else:
                            if index == -1:
                                index = ind
                            elif nr != 0:
                                logger.error("Network mask:" + mask[ind] + " at position "+str(ind)
                                           + "must be 0!")
                                ok = False
                except:
                    ok = False
                    logger.error("Network mask:"+mask[ind]+" is not a number!")
        try:
            int(leaseTime)
        except:
            ok = False
            logger.error("Lease time:" + str(leaseTime) + "is not a number!")
        return ok

def messageToString(message):
    string_message = ""
    string_message += "Message type:" + str(message.op) + "\n"
    string_message += "Hardware type:" + str(message.hlen) + "\n"
    string_message += "Hops:" + str(message.hops) + "\n"
    string_message += "Transaction ID:" + str(message.xid) + "\n"
    string_message += "Second elapsed:" + str(message.secs) + "\n"
    string_message += "Bootp flags:" + str(message.flags) + "\n"
    string_message += "Client IP address:" + message.ciaddr + "\n"
    string_message += "Your (client) IP address:" + message.yiaddr + "\n"
    string_message += "Next server IP address:" + message.siaddr + "\n"
    string_message += "Relasy agent IP address:" + message.giaddr + "\n"
    string_message += "Client MAC address:" + message.chaddr + "\n"
    string_message += "Server host name:" + message.sname + "\n"
    string_message += "Boot file name:" + message.file + "\n"
    string_message += "Options:" + "\n"
    for option in message.options.keys():
        string_message += "\t" + str(option) + ":" + str(message.options[option]) + "\n"
    return string_message

if __name__ == '__main__':
    root = Tk()
    root.geometry("600x600")
    server = DHCP_gui(root)
    root.mainloop()