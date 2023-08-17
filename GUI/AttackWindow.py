import tkinter as tk
from socket import *


from GUI.AttackPage import *


class AttackWindow(tk.Tk):
    def __init__(self, bus_list):
        tk.Tk.__init__(self)
        self.ws = self.winfo_screenwidth() # width of the screen
        self.hs = self.winfo_screenheight()
        self.title("Attack Window")
        # self.geometry(f"{int(self.ws*0.3)}x{int(self.hs*0.8)}+{int(self.ws/2)}+{int(self.hs/9)}")
        # self.geometry(f"{int(self.ws*0.2)}x{int(self.hs*0.8)}")
        self.container = tk.Frame(self)
        self.container.pack()
        self.bus_list = bus_list
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.frames = {}
        frame = AttackPage(self.container, self)
        self.frames[AttackPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(AttackPage)
        
    def on_closing(self, action_menu):
        action_menu.entryconfig("Open Defense Window", state="active")
        self.destroy()

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def reset_win(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}
        frame = AttackPage(self.container, self)
        self.frames[AttackPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(AttackPage)


