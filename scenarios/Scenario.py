import numpy as np
import random

from constants import *

class Scenario:
    def __init__(self, nr):
        self.scenario_nr = nr
        if (self.scenario_nr == SCENARIO1_UNATTACKED or 
            self.scenario_nr == SCENARIO1_ATTACKED or
            self.scenario_nr == SCENARIO1_MOD_ATTACKED):
            np.random.seed(1)
        elif (self.scenario_nr == SCENARIO2_UNATTACKED or 
            self.scenario_nr == SCENARIO2_ATTACKED or
            self.scenario_nr == SCENARIO2_MOD):
            np.random.seed(2)
        elif (self.scenario_nr == SCENARIO3_MOD):
            np.random.seed(3)

        # np.random.RandomState(1)


    def create_load_profile(self, net):
        volatility=0.01
        n = len(net.load.index)
        if (self.scenario_nr == SCENARIO1_UNATTACKED or 
            self.scenario_nr == SCENARIO1_ATTACKED or 
            self.scenario_nr == SCENARIO1_MOD_ATTACKED):
            n_ts=100 
            load_profile = np.zeros([n_ts,n])
            load_values = np.zeros(n_ts)
            for i in range(n_ts):
                new_value=volatility*np.random.rand()
                if np.random.rand() > 0.5:
                    load_values[i] = new_value
                else:
                    load_values[i] = -new_value

            for i in range(n_ts):
                load_profile[i,:] = 1 + load_values[i]
            return load_profile
        
        elif (self.scenario_nr == SCENARIO2_UNATTACKED or 
            self.scenario_nr == SCENARIO2_ATTACKED or 
            self.scenario_nr == SCENARIO2_MOD):
            n_ts=500 
            load_profile = np.zeros([n_ts,n])
            load_values = np.zeros(n_ts)
            for i in range(n_ts):
                new_value=volatility*np.random.rand()
                if np.random.rand() > 0.5:
                    load_values[i] = new_value
                else:
                    load_values[i] = -new_value

            for i in range(n_ts):
                load_profile[i,:] = 1 + load_values[i]
            return load_profile
        
        elif (self.scenario_nr == SCENARIO3_MOD):
            n_ts=250
            load_profile = np.zeros([n_ts,n])
            load_values = np.zeros(n_ts)
            for i in range(n_ts):
                new_value=volatility*np.random.rand()
                if np.random.rand() > 0.5:
                    load_values[i] = new_value
                else:
                    load_values[i] = -new_value

            for i in range(n_ts):
                load_profile[i,:] = 1 + load_values[i]
            return load_profile