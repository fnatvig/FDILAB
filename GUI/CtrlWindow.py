import tkinter as tk
from socket import *

from constants import *
from GUI.CtrlPage1 import *
from GUI.CtrlPage2 import *
from GUI.AttackWindow import *

class CtrlWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.startup = True
        self.container = tk.Frame(self)
        self.title("Control Panel")
        self.geometry("300x100")
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight()
        self.geometry(f"+{int(2*ws/5)}+{int(hs/9)}")
        self.container.pack()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", GUI_PORT))
        self.attack_win =None
        self.export_win =None
        self.running = True
        self.frames = {}
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.sim_menu = tk.Menu(self.menubar, tearoff=False)
        self.sim_menu.add_command(
        label='Stop Simulation',
        command=lambda: self.reset_sim()
            )
        self.sim_menu.add_command(
        label='Exit',
        command=lambda: self.on_closing(procs=None, )
        )
        self.menubar.add_cascade(
            label="Simulation",
            state="disabled",
            menu=self.sim_menu
        )
        self.action_menu = tk.Menu(self.menubar, tearoff=False)
        self.action_menu.add_command(
        label='Open Attack Panel',
        command=lambda: self.open_attack_panel())
        self.action_menu.add_command(
        label='Open Defense Panel',
        command=self.destroy)

        self.menubar.add_cascade(
            label="Action",
            state="disabled",
            menu=self.action_menu)
        
        for F in (CtrlPage1, CtrlPage2):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def open_attack_panel(self):
        bus_list = [str(list(range(int(self.number_of_buses)))[i]) for i in list(range(int(self.number_of_buses)))]
        self.attack_win = AttackWindow(bus_list)

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
        self.show_page(CtrlPage1)

    def on_closing(self, procs):
        if not (procs == None):
            for p in procs:
                if p.is_alive():
                    self.socket.sendto(KILL_SIM, (UDP_IP, POWER_PORT))
                    p.kill()
        
        if not (self.attack_win ==None):
            try:
                self.attack_win.destroy()
            except tk.TclError:
                pass

        if not (self.export_win ==None):
            try:
                self.export_win.destroy()
            except tk.TclError:
                pass
        self.running = False
        self.destroy()

    def reset_sim(self):
        self.socket.sendto(RESET_SIM, (UDP_IP, POWER_PORT))
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}

        if (not (self.attack_win ==None)):
            try:
                self.attack_win.destroy()
            except tk.TclError:
                pass
        if not (self.export_win ==None):
            try:
                self.export_win.destroy()
            except tk.TclError:
                pass
        for F in (CtrlPage1, CtrlPage2):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(CtrlPage1)
