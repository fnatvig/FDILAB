import numpy as np
import random

from constants import *

class Scenario:
    def __init__(self, nr):
        self.scenario_nr = nr
        np.random.seed(1)
            # np.random.seed(1)


    def create_load_profile(self, net):
        n = len(net.load.index)
        if (self.scenario_nr == STANDARDSCENARIO_UNATTACKED) or (self.scenario_nr == STANDARDSCENARIO_ATTACKED):

            n_ts=100 
            volatility=0.02
            load_profile = np.zeros([n_ts,n])
            load_values = np.zeros(n_ts)
            for i in range(0,n_ts):
                new_value=volatility*np.random.rand()
                if np.random.rand() > 0.5:
                    load_values[i] = new_value
                else:
                    load_values[i] = -new_value

            for i in range(n_ts):
                load_profile[i,:] = 1 + load_values[i]
            return load_profile