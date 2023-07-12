from socket import *
from constants import *
from multiprocessing import Queue, Process
import matplotlib.pyplot as plt


class PlotServer:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", PLOT_PORT))
        self.plot_queue = Queue()
        self.socket.sendto(PLOTSERVER_READY, (UDP_IP, GUI_PORT))
        
    def animate(self):
        pass

    def wait_for_activation(self):
        while True:
            msg = self.socket.recv(1024)
            if msg == ACTIVATE_PLOT:
                break

    def main(self):
        self.wait_for_activation()
        print("Plot activated!")
        pass
        
    def child_process(self):
        pass
