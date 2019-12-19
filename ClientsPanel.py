import tkinter as tk

class ClientsPanel(tk.LabelFrame):
    clients_frame = {}
    free_rows = []

    def __init__(self, master, widh, heig, posx, posy, text):
        super(ClientsPanel, self).__init__()
        self.config(width=widh, height=heig, text=text)
        self.widgets = {}
        self.grid(row=posx, column=posy)
        self.initial_row = 0

    def add_client(self, xid, mac_address, ip_address):
        if len(self.free_rows) == 0:
            nr_row = self.initial_row
            self.initial_row += 1
        else:
            nr_row = self.free_rows[0]
            self.free_rows.remove(nr_row)

        cl_frame = tk.Frame(self, height=5)
        cl_frame.grid(row=nr_row, column=0, ipadx=5, ipady=5)
        self.clients_frame[xid] = [cl_frame, nr_row]

        tk.Label(cl_frame, text="-")
        txt = "Mac address:" + str(mac_address)
        mac_label = tk.Label(cl_frame, text=txt, width=30)
        mac_label.grid(row=0, column=1)

        txt = "IP address assigned: " + str(ip_address)
        ip_label = tk.Label(cl_frame, text=txt, width=30)
        ip_label.grid(row=0, column=2)


    def delete_client(self, xid):
        self.free_rows.append(self.clients_frame[xid][1])
        self.clients_frame[xid][0].grid_forget()

    def delete_all_clients(self):
        for xid in self.clients_frame.keys():
            self.clients_frame[xid][0].grid_forget()

    def exist_client(self, xid):
        if xid in self.clients_frame.keys():
            return True
        return False

