import tkinter as tk
from socket import *


from GUI.AttackPage import *


class AttackWindow(tk.Tk):
    def __init__(self, bus_list):
        tk.Tk.__init__(self)
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight()
        self.title("Attack Panel")
        self.geometry(f"+{int(ws/2)}+{int(hs/9)}")
        self.container = tk.Frame(self)
        self.container.pack()
        self.bus_list = bus_list
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.frames = {}
        frame = AttackPage(self.container, self)
        self.frames[AttackPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(AttackPage)
        

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


