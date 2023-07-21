import tkinter as tk
from socket import *

from GUI.ExportPage import *

class ExportWindow(tk.Tk):
    def __init__(self, file_format):
        tk.Tk.__init__(self)
        self.title("Export Window")
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight()
        self.geometry("250x50")
        self.container = tk.Frame(self)
        self.container.pack()
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.frames = {}
        self.file_format = file_format
        frame = ExportPage(self.container, self)
        self.frames[ExportPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_page(ExportPage)

    def show_page(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def on_closing(self, reset):
        if reset:

            self.socket.sendto(EXPORT_DONE, (UDP_IP, GUI_PORT2))
        else:    
            self.socket.sendto(EXPORT_CLOSED, (UDP_IP, GUI_PORT2))
        self.destroy()