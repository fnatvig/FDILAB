from socket import *
import numpy as np
from random import Random

from constants import *

class ModBot:
    def __init__(self, scenario=None, t_end=100, number_of_buses=None):
        self.scenario = scenario
        self.last_mod = None
        self.t_end = t_end
        self.number_of_buses = number_of_buses


    def set_active(self):
        if self.scenario == SCENARIO1_MOD_ATTACKED:
            self.random = Random(1)
            self.active = True
        elif self.scenario == SCENARIO2_MOD:
            self.random = Random(3)
            self.active = True
        elif self.scenario == SCENARIO3_MOD:
            self.random = Random(4)
            self.active = True
        else:
            self.active = False

    def main(self, line_list, t):
        if self.number_of_buses == 9:
            if self.scenario == SCENARIO1_MOD_ATTACKED:
                if t<int(0.5*self.t_end):
                    return self.restore_grid(line_list)
                else:
                    return self.modify(line_list, 5)
            elif self.scenario == SCENARIO2_MOD:
                if int(0.2*self.t_end)<t<int(0.3*self.t_end):
                    return self.modify(line_list, 7)
                elif int(0.5*self.t_end)<t<int(0.6*self.t_end):
                    return self.modify(line_list, 4)              
                else:
                    return self.restore_grid(line_list)
            elif self.scenario == SCENARIO3_MOD:
                if int(0.2*self.t_end)<t<int(0.4*self.t_end):
                    return self.modify(line_list, 1)                 
                else:
                    return self.restore_grid(line_list)
        elif self.number_of_buses == 30:
            if self.scenario == SCENARIO1_MOD_ATTACKED:
                if t<int(0.5*self.t_end):
                    return self.restore_grid(line_list)
                else:
                    return self.modify(line_list, 26)
            elif self.scenario == SCENARIO2_MOD:
                if int(0.1*self.t_end)<t<int(0.2*self.t_end):
                    return self.modify(line_list, 28)
                elif int(0.25*self.t_end)<t<int(0.3*self.t_end):
                    return self.modify(line_list, 25)
                elif int(0.35*self.t_end)<t<int(0.4*self.t_end):
                    return self.modify(line_list, 19)            
                elif int(0.45*self.t_end)<t<int(0.5*self.t_end):
                    return self.modify(line_list, 10)
                elif int(0.55*self.t_end)<t<int(0.6*self.t_end):
                    return self.modify(line_list, 31)
                elif int(0.75*self.t_end)<t<int(0.8*self.t_end):
                    return self.modify(line_list, 8)
                else:
                    return self.restore_grid(line_list)

            elif self.scenario == SCENARIO3_MOD:
                if int(0.2*self.t_end)<t<int(0.3*self.t_end):
                    return self.modify(line_list, 20)
                elif int(0.5*self.t_end)<t<int(0.6*self.t_end):
                    return self.modify(line_list, 9)
                elif int(0.7*self.t_end)<t<int(0.8*self.t_end):
                    return self.modify(line_list, 23)                
                else:
                    return self.restore_grid(line_list)
                

    def modify(self, line_list, line_to_disable):
        line_status = len(line_list)*[True]
        if type(line_to_disable) == list:
            for i in line_to_disable:
                line_status[i] = False
        else:    
            line_status[line_to_disable]  = False
        return line_status
        
    def modify_rand(self, line_list):
        if (self.scenario == SCENARIO1_MOD_ATTACKED or
            self.scenario == SCENARIO2_MOD):
            line_status = len(line_list)*[True]
            line_to_disable = self.random.choice(line_list)
            line_status[line_to_disable]  = False
            return line_status
                            
    def restore_grid(self, line_list):
        line_status = len(line_list)*[True]
        return line_status

                
