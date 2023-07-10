from socket import *
from constants import *

class EvaluationWindow:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(("127.0.0.1", PLOT_PORT))