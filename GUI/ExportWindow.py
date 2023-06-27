import tkinter as tk
from socket import *


from GUI.ExportPage1 import *



class ExportWindow(tk.Tk):
    def __init__(self, bus_list):
        tk.Tk.__init__(self)
        self.title("Export Panel")
        self.geometry("300x50")
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight()
        self.geometry(f"+{int(3*ws/4)}+{int(hs/9)}")
        self.container = tk.Frame(self)
        self.container.pack()
        self.bus_list = bus_list
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.frames = {}

        frame = ExportPage1(self.container, self)
        self.frames[ExportPage1] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(ExportPage1)
        

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def reset_win(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}
        frame = ExportPage1(self.container, self)
        self.frames[ExportPage1] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(ExportPage1)
