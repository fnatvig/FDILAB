import tkinter as tk
from socket import *

from constants import *
from GUI.PageOne import *
from GUI.PageTwo import *
from GUI.PageThree import *

class GuiApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(self)
        container.pack()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", GUI_PORT))
        self.frames = {}
        for F in (PageOne, PageTwo, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def wait_for_confirmation(self):
        counter = 0
        print("Intializing modules...")
        while counter<2:
            msg = self.socket.recv(1024) 
            if (msg == POWERENGINE_READY):
                print("Power Engine ready!")
                counter += 1
            elif (msg == PLOTSERVER_READY):
                print("Plot Server ready!")
                counter += 1
        self.show_page(PageOne)

    def on_closing(self, procs):


        for p in procs:
            if p.is_alive():
                self.socket.sendto(KILL_SIM, (UDP_IP, POWER_PORT))
                p.kill()
        self.destroy()
