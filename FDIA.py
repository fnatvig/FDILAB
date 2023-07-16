import pandapower as pp
import numpy as np
import pandas as pd

from constants import *
# Class for False Data Injection Attacks
class FDIA:

    def __init__(self, active=None, element_type=None, element=None, measurement_type=None, attack_number=None, intensity=None):
        self.active = active
        self.e_type = element_type
        self.element = element
        self.m_type = measurement_type
        self.a_number = attack_number
        self.attack_vector = None
        self.intensity = intensity


    def fill_attack_vector(self, net):
        match self.e_type:
            case "bus":

                match self.a_number:
                    # # Single bus attack 
                    # case 0:
                    #     self.attack_vector = len(net.bus.index)*[1.0]
                    #     self.attack_vector[self.element] = self.intensity
                    # Attack on an all buses
                    case 1:
                        self.attack_vector = self.intensity

    def execute_attack(self, bus_data, line_data, trafo_data):
        match self.e_type:
            case "bus":
                for i in range(len(self.m_type)):
                    match self.m_type[i]:
                        case "vm_pu":
                            bus_data.loc["vm_pu"][i]*=self.attack_vector[i]
                        case "p_mw":
                            bus_data.loc["p_mw"][i]*=self.attack_vector[i]
                        case "q_mvar":
                            bus_data.loc["q_mvar"][i]*=self.attack_vector[i]
        return bus_data, line_data, trafo_data
    
    def get_attributes(self):
        return self.active, self.e_type, self.element, self.m_type, self.a_number, self.intensity, self.attack_vector
