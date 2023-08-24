from socket import *
import numpy as np
from random import Random

from constants import *

class ModBot:
    def __init__(self, scenario=None, active=False):
        self.scenario = scenario
        self.last_mod = None
        self.i = 0

    def set_active(self):
        if self.scenario == SCENARIO1_MOD_ATTACKED:
            self.random = Random(1)
            self.active = True
        elif self.scenario == SCENARIO2_MOD_ATTACKED:
            self.random = Random(3)
            self.active = True
        else:
            self.active = False

    def main(self, line_list):
        if 0<self.i<10:
            self.i +=1
            print("last_mod ", self.last_mod)
            return self.last_mod
        elif self.i>10:
            self.i=0
            self.last_mod = None
            return self.resture_grid(line_list)
        elif self.random.choice(list(range(19)))==0:
            self.i+=1
            self.last_mod = self.modify(line_list)
            return self.last_mod
        else:
            return self.resture_grid(line_list)

    def modify(self, line_list):
        if (self.scenario == SCENARIO1_MOD_ATTACKED or
            self.scenario == SCENARIO2_MOD_ATTACKED):
            line_status = len(line_list)*[True]
            line_to_disable = self.random.choice(line_list)
            line_status[line_to_disable]  = False
            return line_status
                            
    def resture_grid(self, line_list):
        line_status = len(line_list)*[True]
        return line_status

                
