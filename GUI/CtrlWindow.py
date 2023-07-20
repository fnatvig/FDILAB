import tkinter as tk
from socket import *
import sys
from threading import *


from constants import *
from GUI.CtrlPage1 import *
from GUI.CtrlPage2 import *
from GUI.CtrlPage3 import *
from GUI.AttackWindow import *
# from GUI.PlotServer import *

class CtrlWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.startup = True
        self.container = tk.Frame(self)
        self.title("Control Panel")
        self.width = 300 
        self.height = 100
        self.geometry(f"{self.width}x{self.height}")
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight()
        self.geometry(f"+{int(2*ws/5)}+{int(hs/9)}")
        self.container.pack()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", GUI_PORT))
        self.attack_win =None
        self.defense_win =None
        self.eval_win = None
        self.scenario = False

        self.running = True
        self.frames = {}
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.p, self.t = None, None
        self.sim_menu = tk.Menu(self.menubar, tearoff=False)
        self.scenario_menu = tk.Menu(self.sim_menu, tearoff=False)
        self.scenario_menu.add_command(
        label='Run Scenario 1 (unattacked)',
        state="disabled",
        command=lambda: self.load_scenario(SCENARIO1_UNATTACKED)
            )
        self.scenario_menu.add_command(
        label='Run Scenario 1 (attacked)',
        state="disabled",
        command=lambda: self.load_scenario(SCENARIO1_ATTACKED)
            )
        self.scenario_menu.add_command(
        label='Run Scenario 2 (unattacked)',
        state="disabled",
        command=lambda: self.load_scenario(SCENARIO2_UNATTACKED)
            )
        self.scenario_menu.add_command(
        label='Run Scenario 2 (attacked)',
        state="disabled",
        command=lambda: self.load_scenario(SCENARIO2_ATTACKED)
            )
        self.sim_menu.add_cascade(
        label='Run Scenario',
        state="disabled",
        menu = self.scenario_menu
            )
        self.export_menu = tk.Menu(self.sim_menu, tearoff=False)
        self.export_menu.add_command(
        label='as .xlsx',
        command=lambda: self.export_sim(EXPORT_EXCEL)
            )
        self.export_menu.add_command(
        label='as .csv',
        command=lambda: self.export_sim(EXPORT_CSV)
            )
        self.sim_menu.add_cascade(
        label='Export Simulation',
        state="disabled",
        menu = self.export_menu
            )
        self.sim_menu.add_separator()
        self.sim_menu.add_command(
        label='Stop Simulation',
        state="disabled",
        command=lambda: self.reset_sim()
            )
        self.sim_menu.add_command(
        label='Exit',
        command=lambda: self.on_closing()
            )
        self.menubar.add_cascade(
            label="Simulation",
            menu=self.sim_menu
        )
        self.action_menu = tk.Menu(self.menubar, tearoff=False)
        self.action_menu.add_command(
        label='Open Evaluation Window',
        command=lambda: self.open_evaluation_window())
        self.action_menu.add_command(
        label='Open Attack Window',
        command=lambda: self.open_attack_panel())
        self.action_menu.add_command(
        label='Open Defense Window',
        command=lambda: self.open_defense_panel())

        self.menubar.add_cascade(
            label="Window",
            state="disabled",
            menu=self.action_menu)
        
        for F in (CtrlPage1, CtrlPage2, CtrlPage3):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def load_scenario(self, msg):

        self.socket.sendto(LOAD_SCENARIO, (UDP_IP, POWER_PORT))
        self.socket.sendto(msg, (UDP_IP, POWER_PORT))
        self.sim_menu.entryconfig("Export Simulation", state="active")
        self.sim_menu.entryconfig("Run Scenario", state="disabled")
        self.show_page(CtrlPage3)


    def export_sim(self, msg):
        self.socket.sendto(SAVE_SIM, (UDP_IP, POWER_PORT))
        time.sleep(0.1)
        self.socket.sendto(msg, (UDP_IP, POWER_PORT))

    def eval_win_open(self):
        msg = self.socket.recv(1024)
        if msg == PLOT_CLOSED:
            self.action_menu.entryconfig("Open Evaluation Window", state="active")
        elif msg == KILL_PLOT:
            pass

    def open_evaluation_window(self):
        self.action_menu.entryconfig("Open Evaluation Window", state="disabled")
        self.socket.sendto(ACTIVATE_PLOT, (UDP_IP, PLOT_PORT))
        self.socket.sendto(ACTIVATE_PLOT, (UDP_IP, POWER_PORT))
        Thread(target=self.eval_win_open).start()
        

    def open_attack_panel(self):
        # self.action_menu.entryconfig("Open Attack Window", state="disabled")
        # if (self.attack_win == None) or (not self.attack_win.open): 
        bus_list = [str(list(range(int(self.number_of_buses)))[i]) for i in list(range(int(self.number_of_buses)))]
        self.attack_win = AttackWindow(bus_list)
        self.action_menu.entryconfig("Open Attack Window", state="disabled")
        self.attack_win.protocol("WM_DELETE_WINDOW", lambda: self.attack_win.on_closing(self.action_menu))            

    def open_defense_panel(self):
        # self.action_menu.entryconfig("Open Defense Window", state="disabled")
        self.defense_win = DefenseWindow()
        self.action_menu.entryconfig("Open Defense Window", state="disabled")
        self.defense_win.protocol("WM_DELETE_WINDOW", lambda: self.defense_win.on_closing(self.action_menu))            


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

    def on_closing(self):
        self.socket.sendto(KILL_SIM, (UDP_IP, POWER_PORT))
        self.socket.sendto(KILL_PLOT, (UDP_IP, PLOT_PORT))
        self.socket.sendto(KILL_PLOT, (UDP_IP, GUI_PORT))
        if not (self.p == None):
            for p in self.p:
                if p.is_alive():
                    p.kill()
        
        
        if not (self.attack_win ==None):
            try:
                self.attack_win.destroy()
            except tk.TclError:
                pass

        if not (self.defense_win ==None):
            try:
                self.defense_win.destroy()
            except tk.TclError:
                pass
        self.running = False
        self.destroy()

    def reset_sim(self):
        self.sim_menu.entryconfig("Run Scenario", state="disabled")
        self.sim_menu.entryconfig("Stop Simulation", state="disabled")
        self.sim_menu.entryconfig("Export Simulation", state="disabled")
        self.action_menu.entryconfig("Open Defense Window", state="active")
        self.action_menu.entryconfig("Open Attack Window", state="active")
        self.action_menu.entryconfig("Open Evaluation Window", state="active")
        self.menubar.entryconfig("Window", state="disabled")

        self.socket.sendto(RESET_SIM, (UDP_IP, POWER_PORT))
        self.socket.sendto(RESET_PLOT, (UDP_IP, PLOT_PORT))

        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}

        if (not (self.attack_win ==None)):
            try:
                self.attack_win.destroy()
            except tk.TclError:
                pass
        if not (self.defense_win ==None):
            try:
                self.defense_win.destroy()
            except tk.TclError:
                pass
        for F in (CtrlPage1, CtrlPage2, CtrlPage3):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(CtrlPage1)
