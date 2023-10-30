from socket import *
from constants import *
from multiprocessing import Queue, Process
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import struct
import queue
import os


class PlotServer:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((UDP_IP, PLOT_PORT))
        self.plot_queue = Queue()
        self.mse, self.mae, self.x = [], [], []
        self.flag = True
        self.time = 0
        self.socket.sendto(PLOTSERVER_READY, (UDP_IP, GUI_PORT1))
        
    def animate(self, i):
        try:
            y_new = self.plot_queue.get(False)
            if (y_new==0.0):
                    plt.close()
            self.mse.append(y_new[0])
            # self.mae.append(y_new[1])
            self.x.append(self.time)
            self.time +=1
            if (len(self.mse)>500):
                del self.mse[0]
                # del self.mae[0]
                del self.x[0]

        except queue.Empty:
            pass

        plt.clf()
        plt.plot(self.x, self.mse, label = "Mean Squared Error")
        if (len(self.mse) == 100) and (self.flag):
            self.flag = False
            print(self.mse)
        # plt.plot(self.x, self.mae, label = "Mean Absolute Error")
        # plt.legend()
        plt.xlabel('Time', fontsize=10)
        plt.ylabel("Mean Squared Error", fontsize=10)
        # plt.ylabel("Error", fontsize=10)
        # plt.ylabel('Mean Squared Error', fontsize=10)
        plt.tight_layout()

    def wait_for_activation(self):
        while True:
            msg = self.socket.recv(1024)
            if msg == ACTIVATE_PLOT:
                break

    def on_close(self, event):
        self.socket.sendto(PLOT_CLOSED, (UDP_IP, GUI_PORT1))
        self.socket.sendto(RESET_PLOT, (UDP_IP, PLOT_PORT))

    def child_process(self):
        fig = plt.figure()
        fig.canvas.manager.set_window_title('Evaluation Window')
        fig.canvas.mpl_connect('close_event', self.on_close)
        ani = FuncAnimation(plt.gcf(), func=self.animate, interval=50, cache_frame_data=False)
        plt.tight_layout()
        plt.show()

    def main(self):
        is_running = True
        while is_running:
            self.wait_for_activation()
            p = Process(target=self.child_process)
            p.start()
            while True:
                try:
                    data = self.socket.recv(1024)
                    if data == RESET_PLOT:
                        p.kill()
                        break
                    elif data == ACTIVATE_PLOT:
                        pass
                    elif data == KILL_PLOT:
                        p.kill()
                        is_running = False
                        break
                    else:
                        unpack = struct.unpack("f f", data)
                        self.plot_queue.put(unpack)
                except socket.error:
                    pass
        
