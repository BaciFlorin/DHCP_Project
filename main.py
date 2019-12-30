from tkinter import Tk
from gui import DHCP_gui

if __name__ == '__main__':
    root = Tk()
    root.geometry("1080x650")
    root.resizable(0, 0)
    server = DHCP_gui.DHCP_gui(root)
    root.mainloop()
