import tkinter as tk
from socket import *


from GUI.AttackPage1 import *
from GUI.AttackPage2 import *
from GUI.AttackPage3 import *


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
        # for F in (AttackPage3):
        #     frame = F(self.container, self)
        #     self.frames[F] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")

        frame = AttackPage3(self.container, self)
        self.frames[AttackPage3] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(AttackPage3)
        

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def reset_win(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}
        # for F in (AttackPage1, AttackPage2, AttackPage3):
            # frame = F(self.container, self)
            # self.frames[F] = frame
            # frame.grid(row=0, column=0, sticky="nsew")
        frame = AttackPage3(self.container, self)
        self.frames[AttackPage3] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(AttackPage3)


