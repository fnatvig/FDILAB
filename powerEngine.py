import matplotlib.pyplot as plt
import pandapower as pp
import pandapower.plotting as plot
import pandapower.networks as nw
import pandapower.estimation as est
import multiprocessing
import socket
import numpy as np
import pandas as pd
from copy import copy
import queue
import struct
import os
from FDIA import *

import matplotlib.animation as animation


colors = ["b", "g", "r", "c", "y","b", "g", "r", "c", "y","b", "g", "r", "c"]

# The purpose of this array is to make sure that this process speaks the same 
# language as the gui
msg = [0, 14, 9, 2, 3, 4]

UDP_IP = "127.0.0.1"
# port for gui communication
UDP_PORT = 5005
# port for plotting
PLOT_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Measurement errors for the different measurement types
  
sigma_bus_v  = 0.0001
sigma_bus_pq  = 50*0.0001
sigma_line = 0.1
sigma_trafo = 0.1


toggle_attack = 0
toggle_plot = False
last_attack = FDIA(active=False)


def main():
    global toggle_plot 
    global msg
    multiprocessing.set_start_method("spawn", force=True)

    # Two "queues" that are used to share data inbetween processes 
    attackQueue = multiprocessing.Queue()
    plotQueue = multiprocessing.Queue()

    sock.bind((UDP_IP, UDP_PORT))
    print("Power Engine is up and running!")
    running = 1
    
    # we need to start a new process to be able to run the simulation while still 
    # being able to receive packets from the gui 
    p1 = multiprocessing.Process(target=load_case14, args=(attackQueue, plotQueue))
    p2 = multiprocessing.Process(target=load_case9, args=(attackQueue, plotQueue))
    while running == 1:

        # wait until a packet is received from the gui
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

        # to be able to determine the type of message, the first 4 bytes are interpreted 
        # as a integer and then decoded by comparing it to the previously mentioned msg array 
        unpacked = struct.unpack("i 12x", data)

        # load case 14 was pressed
        if unpacked[0] == msg[1]:
                p1.start()

        # load case 9 was pressed
        elif unpacked[0] == msg[2]:
            p2.start()
        
        # A "single bus attack" has been initiated
        elif unpacked[0] == msg[3]:
            temp, bus, me_type, intensity = struct.unpack('i i s f', data)
            m_type = None
            if me_type == b'v':
                m_type = "vm_pu"
            elif me_type == b'p':
                m_type = "p_mw"
            else:
                m_type = "q_mvar"
            
            attack = FDIA(True, "bus", bus, m_type, 0, intensity)

            # The FDIA instance is added to the queue attackQueue to be able to access it 
            # from all processes   
            attackQueue.put(attack)

        # The "show plot" button was pressed
        elif unpacked[0] == msg[4]:
            plotQueue.put(True)
        
        elif unpacked[0] == msg[0]:
            if p1.is_alive():
                p1.join()
            if p2.is_alive():
                p2.join()
            quit_struct = struct.pack("f f", 0.0, 0.0)
            sock.sendto(quit_struct, (UDP_IP, PLOT_PORT))
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            os._exit(0) 
            running = 0

# Used to create a random load profile (to make the simulation appear realistic over time)
def create_load_profile(net, n_ts=24, volatility=0.05):
    n = len(net.load.index)
    lsf = np.zeros([n_ts,n])
    # init_value = 1
    lsf_values = np.zeros(n_ts)
    # lsf_values[0] = init_value
    for i in range(0,n_ts):
        new_value=volatility*np.random.rand()
        if np.random.rand() > 0.5:
            lsf_values[i] = new_value
        else:
            lsf_values[i] = -new_value

    for i in range(n_ts):
        lsf[i,:] = 1 + lsf_values[i]
    
    return lsf_values, lsf

# Adds fake measurement error to the power flow results (by multiplying with the different sigma:s)
def add_noise(net, sigma_bus_v, sigma_bus_pq, sigma_line, sigma_trafo):



    bus_data = [np.array(net.res_bus.iloc[:]["vm_pu"]+np.random.normal(0,sigma_bus_v, len(net.res_bus.index))),
                np.array(net.res_bus.iloc[:]["p_mw"]+np.random.normal(0,sigma_bus_pq, len(net.res_bus.index))),
                np.array(net.res_bus.iloc[:]["q_mvar"]+np.random.normal(0,sigma_bus_pq, len(net.res_bus.index)))]

    line_data = [np.array(net.res_line.iloc[:]["p_from_mw"]+np.random.normal(0,sigma_line, len(net.res_line.index))),
                np.array(net.res_line.iloc[:]["q_from_mvar"]+np.random.normal(0,sigma_line, len(net.res_line.index))),
                np.array(net.res_line.iloc[:]["p_to_mw"]+np.random.normal(0,sigma_line, len(net.res_line.index))),
                np.array(net.res_line.iloc[:]["q_to_mvar"]+np.random.normal(0,sigma_line, len(net.res_line.index)))
                ]

    trafo_data = [np.array(net.res_trafo.iloc[:]["p_hv_mw"]+np.random.normal(0,sigma_trafo, len(net.res_trafo.index))),
                  np.array(net.res_trafo.iloc[:]["q_hv_mvar"]+np.random.normal(0,sigma_trafo, len(net.res_trafo.index))),
                  np.array(net.res_trafo.iloc[:]["p_lv_mw"]+np.random.normal(0,sigma_trafo, len(net.res_trafo.index))),
                  np.array(net.res_trafo.iloc[:]["q_lv_mvar"]+np.random.normal(0,sigma_trafo, len(net.res_trafo.index)))
                  ]
    busDF = pd.DataFrame(bus_data, index=["vm_pu", "p_mw", "q_mvar"])
    lineDF = pd.DataFrame(line_data, index=["p_from_mw", "q_from_mvar", "p_to_mw", "q_to_mvar"])
    trafoDF = pd.DataFrame(trafo_data, index=["p_hv_mw", "q_hv_mvar", "p_lv_mw", "q_lv_mvar"])

    return busDF, lineDF, trafoDF 

# Used to get the measurements that is used for the state estimator. 
def get_measurements(net, q):
    # global toggle_attack
    global last_attack
    bus_data, line_data, trafo_data = add_noise(net, sigma_bus_v, sigma_bus_pq, sigma_line, sigma_trafo)
    
    # if an attack is initiated from the GUI, the attack vector is filled according to the 
    # data entered in he GUI
    try:
        attack=q.get(False)
        attack.fill_attack_vector(net)
        bus_data, line_data, trafo_data = attack.execute_attack(bus_data, line_data, trafo_data)
        # print(attack.get_attributes())
        atr1, atr2, atr3, atr4, atr5, atr6, atr7 = attack.get_attributes()
        last_attack = FDIA(atr1, atr2, atr3, atr4, atr5, atr6)
        last_attack.fill_attack_vector(net)

    # if an attack wasn't initiated
    except queue.Empty:
        pass

    # to keep the last attack vector
    if last_attack.active:
        last_attack.fill_attack_vector(net)
        bus_data, line_data, trafo_data = last_attack.execute_attack(bus_data, line_data, trafo_data)

    # Gathers the measurements (with added gaussian noise)
    for i in range(len(net.bus.index)):
        pp.create_measurement(net, "v", "bus", bus_data.loc["vm_pu"][i], sigma_bus_v, element=i)
        pp.create_measurement(net, "p", "bus", bus_data.loc["p_mw"][i], sigma_bus_pq, element=i)
        pp.create_measurement(net, "q", "bus", bus_data.loc["q_mvar"][i], sigma_bus_pq, element=i)

    for i in range(len(net.trafo.index)):
        pp.create_measurement(net, "p", "trafo", trafo_data.loc["p_hv_mw"][i], sigma_trafo, element=i, side="hv")
        pp.create_measurement(net, "q", "trafo", trafo_data.loc["q_hv_mvar"][i], sigma_trafo, element=i, side="hv")
        pp.create_measurement(net, "p", "trafo", trafo_data.loc["p_lv_mw"][i], sigma_trafo, element=i, side="lv")
        pp.create_measurement(net, "q", "trafo", trafo_data.loc["q_lv_mvar"][i], sigma_trafo, element=i, side="lv")

    for i in range(len(net.line.index)):
        pp.create_measurement(net, "p", "line", line_data.loc["p_from_mw"][i], sigma_line, element=i, side="from")
        pp.create_measurement(net, "q", "line", line_data.loc["q_from_mvar"][i], sigma_line, element=i, side="from")
        pp.create_measurement(net, "p", "line", line_data.loc["p_to_mw"][i], sigma_line, element=i, side="to")
        pp.create_measurement(net, "q", "line", line_data.loc["p_to_mw"][i], sigma_line, element=i, side="to")

        
    

# Used to highlight the estimates with a value outside of the acceptable limits 
def alarm(buses, vm_pu, vm_kv, max_pu, min_pu):

    kr = 0
    kb = 0
    vm_kvr = np.array(len(buses)*[np.nan])
    vm_kvb = np.array(len(buses)*[np.nan])
    busesr= copy(buses)
    busesb= copy(buses)
    for j in range(len(vm_pu)):
        if (vm_pu[j]>max_pu[j]) | (vm_pu[j]<min_pu[j]):
            vm_kvr[kr] = vm_kv[j]
            busesr[kr] = buses[j]
            kr +=1
        else:
            vm_kvb[kb] = vm_kv[j]
            busesb[kb] = buses[j]
            kb +=1 

    del busesr[kr:]
    del busesb[kb:]

    vm_kvr = vm_kvr[~np.isnan(vm_kvr)]
    vm_kvb = vm_kvb[~np.isnan(vm_kvb)]

    return vm_kvr, vm_kvb, busesr, busesb

# The main animation loop (running the power flow, measurment gathering, state estimation etc...)
def animate(i, net, ax, lc, bc, tc, eg, load_list_p, load_list_q, bv, q, q1):
    global sock
    global toggle_plot
    draw_list = [lc, bc, tc, eg]
    net.load.loc[:, "p_mw"] *= load_list_p[i][:] 
    net.load.loc[:, "q_mvar"] *= load_list_q[i][:] 
    if len(net.bus.index)<14:
        del draw_list[2]
    plot.draw_collections(draw_list, ax=ax)
    
    pp.runpp(net, run_control=True, max_iteration=50, calculate_voltage_angles=True, init="results")
    get_measurements(net, q)
    est.estimate(net, calculate_voltage_angles=True, init="results")


    buses = net.bus.index.tolist() # list of all bus indices
    vm_pu = np.array(net.res_bus.iloc[:]['vm_pu'])
    vm_pu_est = np.array(net.res_bus_est.iloc[:]['vm_pu'])
    vm_kv = np.array(net.res_bus.iloc[:]['vm_pu'])*np.array(bv[:])
    vm_kv_est = np.array(net.res_bus_est.iloc[:]['vm_pu'])*np.array(bv[:])
    min = np.array(net.bus.iloc[:]['min_vm_pu'])*vm_pu
    max = np.array(net.bus.iloc[:]['max_vm_pu'])*vm_pu

    if toggle_plot:
        plot_data = struct.pack("f f", vm_pu[0], vm_pu_est[0])
        sock.sendto(plot_data, (UDP_IP, PLOT_PORT))

    try:
        q1.get(False)
        plot_data = struct.pack("f f", vm_pu[0], vm_pu_est[0])
        sock.sendto(plot_data, (UDP_IP, PLOT_PORT))
        toggle_plot = True
    except queue.Empty:
        pass
    

    vm_kvr, vm_kvb, busesr, busesb = alarm(buses, vm_pu, vm_kv, max, min)
    vm_kvr_est, vm_kvb_est, busesr_est, busesb_est = alarm(buses, vm_pu_est, vm_kv_est, max, min)

    #  tuples of coordinates for drawing the values on the map
    coordsi = zip(net.bus_geodata.x.loc[buses].values-0.15, net.bus_geodata.y.loc[buses].values-0.15) 
    coords_r = zip(net.bus_geodata.x.loc[busesr].values-0.3, net.bus_geodata.y.loc[busesr].values+0.18)
    coords_b = zip(net.bus_geodata.x.loc[busesb].values-0.3, net.bus_geodata.y.loc[busesb].values+0.18)
    coords_r_e = zip(net.bus_geodata.x.loc[busesr_est].values-0.3, net.bus_geodata.y.loc[busesr_est].values+0.05)
    coords_b_e = zip(net.bus_geodata.x.loc[busesb_est].values-0.3, net.bus_geodata.y.loc[busesb_est].values+0.05)
    bic_idx = plot.create_annotation_collection(size=0.13, texts=np.char.mod('%d', buses), coords=coordsi, zorder=3, color="blue")
    draw_list.append(bic_idx)
    if not len(vm_kvr)==0:
        bic_r = plot.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvr), ' kV'), coords=coords_r, zorder=3, color=(0, 0, 1, 0.5))
        draw_list.append(bic_r)
    if not len(vm_kvb)==0: 
        bic_b = plot.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvb), ' kV'), coords=coords_b, zorder=3, color=(0, 0, 1, 0.5))
        draw_list.append(bic_b)
    if not len(vm_kvr_est)==0: 
        bic_r_est = plot.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvr_est), ' kV'), coords=coords_r_e, zorder=3, color=(1, 0, 0, 1))
        draw_list.append(bic_r_est)
    if not len(vm_kvb_est)==0: 
        bic_b_est = plot.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvb_est), ' kV'), coords=coords_b_e, zorder=3, color=(0, 0, 0, 0.5))
        draw_list.append(bic_b_est)

    plt.cla()
    plot.draw_collections(draw_list, ax=ax)



def load_case14(q, q1):
    # loads the IEEE 14-bus test case
    net = nw.case14()

    base_values = net.bus.iloc[:]['vn_kv'].tolist()
    fig, ax = plt.subplots(figsize=(7, 7))

    pp.runpp(net, run_control=True, calculate_voltage_angles=True, init='dc')
    get_measurements(net, q)
    est.estimate(net, calculate_voltage_angles=True, init="flat")

    #create lines (for plotting)
    lc = plot.create_line_collection(net, color="silver", zorder=1)
    #create buses (for plotting)
    bc = plot.create_bus_collection(net, net.bus.index, size=0.03, color="b", zorder=2)
    #create transformers (for plotting)
    tc = plot.create_trafo_collection(net, color="silver",size=0.05, zorder=1)
    #Create external grid connection (for plotting)
    eg = plot.create_ext_grid_collection(net, color="black", size=0.1, zorder=3, orientation=3.14159) 
    
    n_ts =  500
    volatility=0.01
    lsf_values, lsfp = create_load_profile(net, n_ts, volatility)
    lsf_values, lsfq = create_load_profile(net, n_ts, volatility)
    ani = animation.FuncAnimation(fig, animate, fargs=(net, ax, lc, bc, tc, eg, lsfp, lsfq, base_values, q, q1), interval=500, frames=100, cache_frame_data=False) 


    plt.show()



def load_case9(q, q1):  
    # loads the IEEE 9-bus test case
    net = nw.case9()
    base_values = net.bus.iloc[:]['vn_kv'].tolist()
    fig, ax = plt.subplots(figsize=(7, 7))
    pp.runpp(net, run_control=True, calculate_voltage_angles=True, init='dc')
    print(net.bus)
    get_measurements(net, q)
    est.estimate(net, calculate_voltage_angles=True, init="flat")
    
    #create lines (for plotting)
    lc = plot.create_line_collection(net, color="silver", zorder=1)
    #create buses (for plotting)
    bc = plot.create_bus_collection(net, net.bus.index, size=0.03, color="b", zorder=2)
    #create transformers (for plotting)
    tc = plot.create_trafo_collection(net, color="silver",size=0.05, zorder=1)
    #Create external grid connection (for plotting)
    eg = plot.create_ext_grid_collection(net, color="black", size=0.1, zorder=3, orientation=3.14159) 
    
    n_ts =  500
    volatility=0.01
    lsf_values, lsfp = create_load_profile(net, n_ts, volatility)
    lsf_values, lsfq = create_load_profile(net, n_ts, volatility)
    plt.plot(lsfp)
    plt.plot(lsfq)
    ani = animation.FuncAnimation(fig, animate, fargs=(net, ax, lc, bc, tc, eg, lsfp, lsfq, base_values, q, q1), interval=500, frames=100, cache_frame_data=False) 


    plt.show()
