from tkinter import *
from tkinter import scrolledtext
import socket
import threading
import SenderHandler
import AddressPool
import Message
import queue
from Logging import *

logger = logging.getLogger(__name__)

class DHCP_gui():
    def __init__(self, _master):
        self.frameWidth = 500
        self.frameHeight = 500
        self.master = _master
        self.initWindow()

    def initWindow(self):

        label2 = Label(self.master, text="Adresa retea:", font="Arial", width=10)
        label2.grid(row=0, column=0, pady=5)

        self.addr = Entry(self.master, width=25)
        self.addr.grid(row=0, column=1, padx=3, sticky=W)

        #entry for the mask
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
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
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
        exit()

    def com_thread(self,conn, addr, pool, lock):
        messageHandler = SenderHandler.SenderHandler(conn, addr, pool, lock)
        xid = 0
        while 1:
            data = conn.recv(4096)
            if data:
                data = data.decode("utf-8")
                message = Message.Message(data)
                message.messageSplit()
                if xid == 0:
                    xid = message.xid
                elif xid == message.xid:
                    messageHandler.handle(message)
                messageHandler.messageSend(message, conn)

    def start_server(self):
        if self.checkEntries():
            self.pool = AddressPool.AddressPool(self.addr.get(), self.mask.get())
            self.lock = threading.Lock()
            self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hostname = socket.gethostname()
            ipAddress = socket.gethostbyname(hostname)
            self.mainSocket.bind((ipAddress, 5000))
            try:
                threading.Thread(target=self.wait_connection).start()
            except:
                logger.log(logging.FATAL, "Thread for wainting a connection couldn\'t start!")


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
                logger.log(logging.FATAL, 'Thread it was not started!')

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.master.after(100, self.poll_log_queue)

    def checkEntries(self):
        ok = True
        ip = self.addr.get()
        mask = self.mask.get()
        leaseTime = self.leaseTime.get()
        ip = ip.split('.')
        if len(ip) != 4:
            logger.log(logging.CRITICAL, "Invalid network address!")
            ok = False
        else:
            for number in ip:
                try:
                    nr = int(number)
                    if nr > 255:
                        ok = False
                        logger.log(logging.CRITICAL, "Network address:" + str(number) + " out of range!")
                except:
                    ok = False
                    logger.log(logging.CRITICAL, "Network address:"+str(number)+" is not a number!")
        mask = mask.split('.')
        if len(mask) != 4:
            logger.log(logging.CRITICAL, "Invalid network mask!")
            ok = False
        else:
            suma = 0
            validNumber = []
            for x in range(7,0,-1):
                suma += pow(2,x)
                validNumber.append(suma)
            index = -1
            for ind in range(0, 3):
                try:
                    nr = int(mask[ind])
                    if nr != 255 and nr != 0:
                        if nr not in validNumber:
                            logger.log(logging.CRITICAL, "Network mask:" + mask[ind] + " is not a valid value for mask!")
                            ok = False
                        else:
                            if index == -1:
                                index = ind
                            elif nr != 0:
                                logger.log(logging.CRITICAL, "Network mask:" + mask[ind] + " at position "+str(ind)+" must be 0!")
                                ok = False
                except:
                    ok = False
                    logger.log(logging.CRITICAL, "Network mask:"+mask[ind]+" is not a number!")
        try:
            int(leaseTime)
        except:
            ok = False
            logger.log(logging.CRITICAL,"Lease time:" + str(leaseTime) + "is not a number!")
        return ok


if __name__ == '__main__':
    root = Tk()
    root.geometry("600x600")
    server = DHCP_gui(root)
    root.mainloop()