import tkinter as tk

class AttackCtrl3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Page One")
        label.pack(pady=10, padx=10)


        button1 = tk.Button(self, text="btn3", command=lambda: self.send_msg("hej"))
        button1.pack()
        button2 = tk.Button(self, text="btn4", command=lambda: self.send_msg("då"))
        button2.pack()

    def send_msg(self, msg):
        print(msg)  