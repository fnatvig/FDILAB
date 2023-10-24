from socket import *
import numpy as np
from random import Random

from constants import *

class AttackBot:
    def __init__(self, scenario=None):
        self.scenario = scenario
        self.attack_ctr =0


    def set_active(self):
        if (self.scenario == SCENARIO1_ATTACKED or 
            self.scenario == SCENARIO1_MOD_ATTACKED):
            self.random = Random(1)
            self.active = True
        elif (self.scenario == SCENARIO2_ATTACKED):
        #  or 
            # self.scenario == SCENARIO2_MOD_ATTACKED):
            self.random = Random(3)
            self.active = True
        else:
            self.active = False

    def main(self, bus_list):
        if self.random.choice(list(range(9)))==0:
            return self.send_attack(bus_list)
        else:
            return self.undo_attack(bus_list)

    def send_attack(self, bus_list):
        if (self.scenario == SCENARIO1_ATTACKED or
            self.scenario == SCENARIO1_MOD_ATTACKED):
            intensity = []
            m_type = []
            for i in range(len(bus_list)):
                intensity.append(self.random.choice([0.99, 1.0, 1.01]))
                m_type.append(self.random.choice(['vm_pu','p_mw','q_mvar'])) 

            return intensity, m_type
        
        if (self.scenario == SCENARIO2_ATTACKED):
            # self.scenario == SCENARIO2_MOD_ATTACKED):
            intensity = []
            m_type = []
            for i in range(len(bus_list)):
                intensity.append(self.random.choice([0.99, 1.0, 1.01]))
                m_type.append(self.random.choice(['vm_pu','p_mw','q_mvar'])) 

            return intensity, m_type
                            
    def undo_attack(self, bus_list):
        intensity = []
        m_type = []
        for i in range(len(bus_list)):
            intensity.append(1.0)
            m_type.append('vm_pu') 
        return intensity, m_type

                
