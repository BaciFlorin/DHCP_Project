from tkinter import *
from tkinter import scrolledtext
import socket
import threading
import SenderHandler
import AddressPool
import Message
import queue
from ClientsPanel import *
from Logging import *

name_of_options = {
    1: "Subnet Mask:",
    3: "Router option",
    6: "Domain Name Server Option:",
    15: "Domain Name",
    58: "Renewal Time Value:"
}


class DHCP_gui():
    available_options = [1, 3, 6, 15, 28, 58]
    configurations = {}

    def __init__(self, _master):
        self.master = _master
        self.initWindow()
        self.stop_threads = False
        self.clients_sockets = []

        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)

        # Start polling messages from the queue
        self.master.after(100, self.poll_log_queue)

    def initWindow(self):
        self.master.title("DHCP server")

        pool_config_label_frame = LabelFrame(self.master, text="Pool and lease time config:", width=50, height=50)
        pool_config_label_frame.grid(row=0, column=1, sticky=(N, E, W, S), ipadx=10, ipady=10, padx=5, pady=5)

        # Input network address
        label2 = Label(pool_config_label_frame, text="Adresa retea:", font="Arial")
        label2.grid(row=0, column=0, padx=3, pady=10)
        self.addr = Entry(pool_config_label_frame, width=25)
        self.addr.grid(row=0, column=1)
        self.addr.insert(0, "192.168.0.0")

        # Input mask address
        label3 = Label(pool_config_label_frame, text="Mask:", font="Arial")
        label3.grid(row=1, column=0, padx=3, pady=10)
        self.mask = Entry(pool_config_label_frame, width=25)
        self.mask.grid(row=1, column=1)
        self.mask.insert(0, "255.255.255.0")

        # Lease time input
        label4 = Label(pool_config_label_frame, text="Lease Time:", font="Arial")
        label4.grid(row=2, column=0, padx=3, pady=10)
        self.leaseTime = Entry(pool_config_label_frame, width=25)
        self.leaseTime.grid(row=2, column=1)
        self.leaseTime.insert(0, "1000")

        # frame-ul unde se afla logul
        log_frame = LabelFrame(self.master, text="Activity log")
        log_frame.grid(row=1, column=2, sticky=(N, E, W, S), ipadx=10, ipady=10, padx=5, pady=5)

        # Console for the log
        self.scrolled_text = scrolledtext.ScrolledText(log_frame, state='disabled', width=80, height=22)
        self.scrolled_text.grid(row=0, column=0, padx=10, pady=10)
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='black')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)

        # frame-ul unde se afla optiunile
        option_frame = LabelFrame(self.master, width=50, height=50, text="Select options:")
        option_frame.grid(row=1, column=1, sticky=(N, E, W, S), ipadx=10, ipady=10, padx=5, pady=5)

        # check buttons
        self.values_for_options = {}
        self.checkbuttons = []
        i = 0
        for option in self.available_options:
            val = IntVar()
            chk = Checkbutton(option_frame, text="Option " + str(option), variable=val)
            chk.grid(row=i, column=0, pady=5)
            self.checkbuttons.append(chk)
            self.values_for_options[option] = val
            i += 1

        # entry for Options
        self.entryOfOptions = {}
        for option in self.available_options:
            if option != 28:
                Label(option_frame, text="(" + str(option) + ")" + name_of_options[option]).grid(row=i, column=0, sticky=W, pady=5)
                ent = Entry(option_frame, width=25)
                ent.grid(row=i, column=1, pady=5)
                self.entryOfOptions[option] = ent
                i += 1

        # space for show clients

        self.clients_frame = ClientsPanel(self.master, 50, 50, 0, 2, "Clients")
        self.clients_frame.grid(sticky=(N, E, W, S), ipadx=10, ipady=10, padx=5, pady=5)

        comand_buttons = Frame(self.master)
        comand_buttons.grid(row=3, column=1, columnspan=2, ipadx=10, ipady=10, padx=5, pady=5)

        # Quit Button Config
        self.quitButton = Button(comand_buttons, text="Quit", command=self.exitServer, width=30)
        self.quitButton.grid(column=1, row=0, padx=30)

        # Start button Config
        self.startButton = Button(comand_buttons, text="Start", command=self.start_server, width=30)
        self.startButton.grid(column=0, row=0, padx=30)

    def exitServer(self):
        if self.startButton["text"] == "Stop":
            self.stop_server()
        exit()

    def start_server(self):
        if self.checkEntries() and self.checkOptionsEntries():
            self.updateInterfaceforStart()

            networkAddress = self.addr.get()
            networkMask = self.mask.get()
            self.pool = AddressPool.AddressPool(networkAddress, networkMask)
            if self.values_for_options[28].get() == 1:
                self.configurations[28] = self.pool.broadcastAddress
            self.configurations[54] = self.pool.server_identifier
            self.configurations[51] = int(self.leaseTime.get())
            print(self.configurations)

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
        self.updateInterfaceforStop()
        self.stop_threads = True
        self.mainSocket.close()
        self.pool = 0
        self.lock = 0
        for sock in self.clients_sockets:
            sock.close()
        self.clients_frame.delete_all_clients()
        logger.info("Server stopped!")

    def wait_connection(self):
        self.mainSocket.listen(1)
        while 1:
            try:
                conn, addr = self.mainSocket.accept()
                self.clients_sockets.append(conn)
            except:
                break
            logger.log(logging.INFO, 'S-a conectat:' + str(addr) + "!")
            try:
                threading.Thread(target=self.com_thread, args=(conn, addr, self.pool, self.lock)).start()
            except:
                logger.log(logging.FATAL, "Thread for the client" + str(addr) + " couldn't start!")

    def com_thread(self, conn, addr, pool, lock):
        messageHandler = SenderHandler.SenderHandler(conn, addr, pool, lock, self.configurations)
        while 1:
            try:
                data = conn.recv(4096)
            except:
                break
            if data:
                data = data.decode("utf-8")
                message = Message.Message(data)
                err = message.messageSplit()
                if err == -1:
                    logger.info("Message incorrect!")
                    conn.close()
                    break
                file_logger.info("RECEIVE:\n" + message.message_to_string())
                if message.options[53] == 'DHCPRELEASE':
                    lock.acquire()
                    self.clients_frame.delete_client(message.xid)
                    lock.release()
                message = messageHandler.handle(message)
                if message == 'INVALID':
                    logger.info("Connection closed!")
                    conn.close()
                    break
                if message.options[53] == 'DHCPACK':
                    lock.acquire()
                    self.clients_frame.add_client(message.xid, message.chaddr, message.yiaddr)
                    lock.release()

                file_logger.info("SEND:\n" + message.message_to_string())
                messageHandler.messageSend(message, conn)

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
        ip = self.addr.get()
        mask = self.mask.get()
        leaseTime = self.leaseTime.get()
        ip = ip.split('.')
        if not self.check_ip_address(ip, ""):
            return False
        mask = mask.split('.')
        if not self.check_mask_address(mask,"", "Network"):
            return False
        try:
            int(leaseTime)
        except:
            logger.error("Lease time:" + str(leaseTime) + "is not a number!")
            return False
        return True


    def checkOptionsEntries(self):
        self.configurations.clear()
        print([x for x in self.available_options if self.values_for_options[x].get() == 1])
        for option in [x for x in self.available_options if self.values_for_options[x].get() == 1]:
            data = ""
            if option != 28:
                data = self.entryOfOptions[option].get()
            if option == 1:
                temp_mask = data.split('.')
                if not self.check_mask_address(temp_mask, "Option 1:", "Subnet"):
                    return False
                self.configurations[option] = data
            if option == 3:
                ips = data.split(',')
                if not self.check_ip_address(ips, "Option 3:"):
                    return False
                self.configurations = data
            if option == 6:
                self.configurations[option] = data
            if option == 15:
                self.configurations[option] = data
            if option == 58:
                try:
                    self.configurations[option] = int(data)
                except:
                    logger.error("Option 58: Value in entry is not a number!")
                    self.configurations.clear()
                    return False
        return True

    def updateInterfaceforStart(self):
        self.startButton["text"] = "Stop"
        self.startButton["command"] = self.stop_server
        self.pool = AddressPool.AddressPool(self.addr.get(), self.mask.get())

        # disable checkbutons
        for chk in self.checkbuttons:
            chk["state"] = "disabled"

        #disable entries for options
        for ent in self.entryOfOptions.values():
            ent["state"] = "disabled"

    def updateInterfaceforStop(self):
        # channge start button
        self.startButton["text"] = "Start"
        self.startButton["command"] = self.start_server

        # enable check buttons
        for chk in self.checkbuttons:
            chk["state"] = "active"

        # enable option entries
        for ent in self.entryOfOptions.values():
            ent["state"] = "normal"

    def check_ip_address(self, ip, option):
        if len(ip) != 4:
            logger.error("Invalid length of network address!")
            return False
        else:
            for number in ip:
                try:
                    nr = int(number)
                    if nr > 255:
                        logger.error(option + "Network address:" + str(number) + " out of range!")
                        return False
                except:
                    logger.error(option + "Network address:"+str(number)+" is not a number!")
                    return False
        return True


    def check_mask_address(self, data, option, mask_type):
        if len(data) != 4:
            logger.error("Invalid length of subnet mask!")
            self.configurations.clear()
            return False
        else:
            suma = 0
            validNumber = []
            for x in range(7, 0, -1):
                suma += pow(2, x)
                validNumber.append(suma)
            index = -1
            for ind in range(0, 3):
                try:
                    nr = int(data[ind])
                    if nr != 255 and nr != 0:
                        if nr not in validNumber:
                            logger.error(option + " " + mask_type + " mask:" + data[ind]
                                         + " is not a valid value for mask!")
                            self.configurations.clear()
                            return False
                        else:
                            if index == -1:
                                index = ind
                            elif nr != 0:
                                logger.error(
                                    option + " " + mask_type + " mask:" + data[ind] + " at position " + str(ind)
                                    + "must be 0!")
                                self.configurations.clear()
                                return False
                except:
                    logger.error(option + " " + mask_type + " mask:" + data[ind] + " is not a number!")
                    self.configurations.clear()
                    return False
        return True


if __name__ == '__main__':
    root = Tk()
    root.geometry("1080x650")
    root.resizable(0, 0)
    server = DHCP_gui(root)
    root.mainloop()
