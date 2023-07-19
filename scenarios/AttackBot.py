from socket import *
import numpy as np
import random
import struct

from constants import *

class AttackBot:
    def __init__(self, scenario=None, active=False):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.scenario = scenario
        self.attack_ctr =0
        random.seed(1)

        # random.seed(1)
        # self.npseed = np.random.seed(1)

    def set_active(self):
        if self.scenario == STANDARDSCENARIO_ATTACKED:
            self.active = True
        else:
            self.active = False

    def main(self, bus_list):
        if random.choice(list(range(6)))==0:
            self.send_attack(bus_list)
        else:
            pass

    def send_attack(self, bus_list):
        if (self.scenario == STANDARDSCENARIO_ATTACKED):
            while self.attack_ctr < 3:
                for i in range(len(bus_list)):
                    self.intensity = random.choice([0.99, 1.0, 1.01])
                    self.m_type = random.choice([b'v',b'p',b'q']) 
                    if i < (len(bus_list)-1):
                        self.socket.sendto(
                            struct.pack('i i s f', MULTI_BUS_ATTACK, i, self.m_type, self.intensity),
                            (UDP_IP, POWER_PORT))
                    else:
                        self.socket.sendto(
                            struct.pack('i i s f', LAST_ATTACK_MSG, i, self.m_type, self.intensity),
                            (UDP_IP, POWER_PORT))
                self.attack_ctr +=1
            self.undo_attack(bus_list)
            self.attack_ctr = 0
                            
    def undo_attack(self, bus_list):
            for i in range(len(bus_list)):
                intensity = 1.0
                m_type = b'v' 
                if i < (len(bus_list)-1):
                    self.socket.sendto(
                        struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))
                else:
                    self.socket.sendto(
                        struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))
            for i in range(len(bus_list)):
                intensity = 1.0
                m_type = b'p' 
                if i < (len(bus_list)-1):
                    self.socket.sendto(
                        struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))
                else:
                    self.socket.sendto(
                        struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))
            for i in range(len(bus_list)):
                intensity = 1.0
                m_type = b'q' 
                if i < (len(bus_list)-1):
                    self.socket.sendto(
                        struct.pack('i i s f', MULTI_BUS_ATTACK, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))
                else:
                    self.socket.sendto(
                        struct.pack('i i s f', LAST_ATTACK_MSG, i, m_type, intensity),
                        (UDP_IP, POWER_PORT))


                
