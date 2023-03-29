import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Queue, Process
import numpy as np
import queue
import os
import struct


UDP_IP = "127.0.0.1"
UDP_PORT = 5006
condition = True 
x = [0]
y1 = [0]
y2 = [0]
flag = True

def animate(i, q):
    global x
    global y1
    global y2
    global flag
    try:
        data = q.get(False)
        y1_new, y2_new = struct.unpack('f f', data)
        y1.append(y1_new)
        y2.append(y2_new)
        x.append(i)
        if flag or (len(y1)>20):
            del y1[0]
            del y2[0]
            del x[0]
            flag = False

    except queue.Empty:
        pass
    plt.clf()
    plt.plot(x, y1, label='Voltage Magnitude, bus 0')
    plt.plot(x, y2, label='Estimated Voltage Magnitude, bus 0')
    plt.legend()
    plt.xlabel('Time', fontsize=10)
    plt.ylabel('Voltage [p.u]', fontsize=10)
    plt.tight_layout()

def child_process(q):
    ani = FuncAnimation(plt.gcf(), animate, fargs=(q,), interval=100)
    plt.tight_layout()
    plt.show()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    i = 0
    plot_queue = Queue()
    plt.style.use('fivethirtyeight')
    print("Plot Server is up and running!")
    data = sock.recv(1024)
    if data == b'1':
        sock.setblocking(0)
    
    p1 = Process(target=child_process, args=(plot_queue,))
    p1.start()

    while True:
        try:
            data = sock.recv(1024)
            plot_queue.put(data)
        except socket.error:
            pass

