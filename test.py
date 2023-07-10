import pandapower as pp
import pandapower.networks as nw
import pandas as pd
from copy import copy

net = nw.case14()
pp.create_measurement(net, "v", "bus", 5.4, 0.1, net.bus.index[0], side = None)
pp.create_measurement(net, "p", "bus", 3.2, 0.2, net.bus.index[0], side = None)
df = copy(net.measurement)




print(net.measurement)
net.measurement.drop([0], inplace=True)
net.measurement.reset_index(inplace=True, drop=True)
print(net.measurement)
net.measurement = df
print(net.measurement)

