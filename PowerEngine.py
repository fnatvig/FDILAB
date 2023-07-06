import matplotlib.pyplot as plt
from socket import *
from multiprocessing import *
import pandapower as pp
import pandapower.networks as nw
import pandapower.estimation as est
import pandapower.plotting as plot
import numpy as np
import queue
import matplotlib.animation as animation
import struct
import os
from copy import copy

from constants import *
from FDIA import *
from Preprocessor import *
from scripts.test1 import *

class PowerEngine:
    def __init__(self):

        # Initializes socket 
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind((UDP_IP, POWER_PORT))

        set_start_method("spawn", force=True)
        self.time_iteration = 0
        self.df = None
        self.net = None
        self.toggle_plot = False
        self.toggle_defense = False
        self.update_animation  = True
        self.last_attack = FDIA(active=False)
        self.sim_queue, self.data_queue = Queue(), Queue()
        self.attack_queue, self.defense_queue = Queue(), Queue()

        # Confirms that the PowerEngine object is initialized
        self.socket.sendto(POWERENGINE_READY, (UDP_IP, GUI_PORT))
            
    def main(self):

        # Wait for user to choose a test case
        msg = self.socket.recv(1024)
        if msg == LOAD14:        
            self.net = nw.case14()
        elif msg == LOAD9:        
            self.net = nw.case9()        
        if not self.net == None:
            print("Test case loaded!")

        sim_process = Process(target=self.sim)
        sim_started = False
        buses, m_types, intensities = [], [], []
        while True:
            msg = self.socket.recv(1024)
            if msg == START_SIM:
                if not sim_started:
                    sim_process.start() 
                    sim_started = True
                self.sim_queue.put(True)   
            
            elif msg == PAUSE_SIM:
                self.sim_queue.put(False)    

            elif msg == KILL_SIM:
                sim_process.kill()
            
            elif msg == RESET_SIM:
                if sim_started:
                    sim_process.kill()
                self.reset()
                self.main()
            
            elif msg == ACTIVATE_DEFENSE:
                self.defense_queue.put(True)
            
            elif msg == DEACTIVATE_DEFENSE:
                self.defense_queue.put(False)

            elif msg == SAVE_SIM:
                self.sim_queue.put(False)    
                size = self.data_queue.qsize()
                self.df = pd.DataFrame(columns=["time", "bus", "V", "P", "Q", "label"])
                for i in range(size):
                    self.df.loc[len(self.df)] = self.data_queue.get()
                preprocessor = Preprocessor(self.df)
                preprocessor.sort()
                self.df = preprocessor.df
                sim_process.kill()

            elif msg == EXPORT_CSV:
                if not os.path.exists("data_exports"):
                    os.mkdir("data_exports")
                self.df.to_csv("data_exports/data_export.csv")

            elif msg == EXPORT_EXCEL:
                if not os.path.exists("data_exports"):
                    os.mkdir("data_exports")
                self.df.to_excel("data_exports/data_export.xlsx")
            
            unpacked = struct.unpack("i 12x", msg)
            if unpacked[0] == MULTI_BUS_ATTACK:
                bus, me_type, intensity = struct.unpack('i i s f', msg)[1:]
                m_type = None
                if me_type == b'v':
                    m_type = "vm_pu"
                elif me_type == b'p':
                    m_type = "p_mw"
                else:
                    m_type = "q_mvar"
                buses.append(bus)
                m_types.append(m_type)
                intensities.append(intensity)

            elif unpacked[0] == LAST_ATTACK_MSG:
                bus, me_type, intensity = struct.unpack('i i s f', msg)[1:]
                m_type = None
                if me_type == b'v':
                    m_type = "vm_pu"
                elif me_type == b'p':
                    m_type = "p_mw"
                else:
                    m_type = "q_mvar"
                buses.append(bus)
                m_types.append(m_type)
                intensities.append(intensity)
                if len(buses) == len(self.net.bus.index):
                    attack = FDIA(True, "bus", buses, m_types, 1, intensities)
                    buses, m_types, intensities = [], [], []
                    self.attack_queue.put(attack)
    def reset(self):
        self.time_iteration = 0
        self.df = None
        self.net = None
        self.toggle_plot = False
        self.update_animation  = True
        self.last_attack = FDIA(active=False)

        self.sim_queue, self.data_queue = Queue(), Queue()
        self.attack_queue, self.defense_queue = Queue(), Queue()
        
        # Confirms that the PowerEngine object is initialized
        self.socket.sendto(POWERENGINE_READY, (UDP_IP, GUI_PORT))
    def sim(self):
        i = 0
        is_running = True
        while True:
            try:
                is_running = self.sim_queue.get(False)
                self.sim_queue.put(is_running)
            except queue.Empty:
                pass

            if is_running:
                
                base_values = self.net.bus.iloc[:]['vn_kv'].tolist()

                pp.runpp(self.net, run_control=True, calculate_voltage_angles=True, init='dc')
                self.get_measurements()
                est.estimate(self.net, calculate_voltage_angles=True, init="flat")

                lc = pp.plotting.create_line_collection(self.net, color="black", zorder=1)
                bc = pp.plotting.create_bus_collection(self.net, self.net.bus.index, size=0.03, color="b", zorder=2)
                tc = pp.plotting.create_trafo_collection(self.net, color="black", size=0.05, zorder=1)
                eg = pp.plotting.create_ext_grid_collection(self.net, color="black", size=0.1, zorder=1, orientation=3.14159) 
                loadc = pp.plotting.create_load_collection(self.net, color="black", zorder=1, size=0.1) 
                genc = pp.plotting.create_gen_collection(self.net, size=0.1, color="black", zorder=1, orientation=3.14159*2) 

                n_ts =  100
                volatility=0.01
                lsfp = self.create_load_profile(n_ts, volatility)
                lsfq = self.create_load_profile(n_ts, volatility)
                self.update_animation = True
                fig, ax = plt.subplots(figsize=(6, 6))
                plt.subplots_adjust(left=0.0, bottom=0.0, top=1.0, right=1.0)
                pp.plotting.draw_collections([lc, bc, tc, eg], ax=ax)
                ani = animation.FuncAnimation(fig, self.animate, fargs=(ax, lc, bc, tc, eg, loadc, genc, lsfp, lsfq, base_values), frames =n_ts, interval=50, cache_frame_data=False) 
                plt.show()
    
    def get_measurements(self):
        bus_data, line_data, trafo_data = self.add_noise(SIGMA_BUS_V, SIGMA_BUS_PQ, SIGMA_LINE, SIGMA_TRAFO)
        
        # if an attack is initiated from the GUI, the attack vector is filled according to the 
        # data entered in he GUI
        try:
            attack=self.attack_queue.get(False)
            attack.fill_attack_vector(self.net)
            bus_data, line_data, trafo_data = attack.execute_attack(bus_data, line_data, trafo_data)
            # print(attack.get_attributes())
            atr1, atr2, atr3, atr4, atr5, atr6, atr7 = attack.get_attributes()
            self.last_attack = FDIA(atr1, atr2, atr3, atr4, atr5, atr6)
            self.last_attack.fill_attack_vector(self.net)



        # if an attack wasn't initiated
        except queue.Empty:
            pass

        # to keep the last attack vector
        if self.last_attack.active:
            self.last_attack.fill_attack_vector(self.net)
            bus_data, line_data, trafo_data = self.last_attack.execute_attack(bus_data, line_data, trafo_data)

        if not (self.last_attack.attack_vector == None):
            if (len(set(self.last_attack.attack_vector)) == 1) and (list(set(self.last_attack.attack_vector))[0] == 1.0):
                self.last_attack.active = False

        # Gathers the measurements (with added gaussian noise)
        for i in range(len(self.net.bus.index)):
            pp.create_measurement(self.net, "v", "bus", bus_data.loc["vm_pu"][i], SIGMA_BUS_V, element=i)
            pp.create_measurement(self.net, "p", "bus", bus_data.loc["p_mw"][i], SIGMA_BUS_PQ, element=i)
            pp.create_measurement(self.net, "q", "bus", bus_data.loc["q_mvar"][i], SIGMA_BUS_PQ, element=i)

        for i in range(len(self.net.trafo.index)):
            pp.create_measurement(self.net, "p", "trafo", trafo_data.loc["p_hv_mw"][i], SIGMA_TRAFO, element=i, side="hv")
            pp.create_measurement(self.net, "q", "trafo", trafo_data.loc["q_hv_mvar"][i], SIGMA_TRAFO, element=i, side="hv")
            pp.create_measurement(self.net, "p", "trafo", trafo_data.loc["p_lv_mw"][i], SIGMA_TRAFO, element=i, side="lv")
            pp.create_measurement(self.net, "q", "trafo", trafo_data.loc["q_lv_mvar"][i], SIGMA_TRAFO, element=i, side="lv")

        for i in range(len(self.net.line.index)):
            pp.create_measurement(self.net, "p", "line", line_data.loc["p_from_mw"][i], SIGMA_LINE, element=i, side="from")
            pp.create_measurement(self.net, "q", "line", line_data.loc["q_from_mvar"][i], SIGMA_LINE, element=i, side="from")
            pp.create_measurement(self.net, "p", "line", line_data.loc["p_to_mw"][i], SIGMA_LINE, element=i, side="to")
            pp.create_measurement(self.net, "q", "line", line_data.loc["p_to_mw"][i], SIGMA_LINE, element=i, side="to")

    # Adds fake measurement error to the power flow results (by multiplying with the different sigma:s)
    def add_noise(self, sigma_bus_v, sigma_bus_pq, sigma_line, sigma_trafo):

        bus_data = [np.array(self.net.res_bus.iloc[:]["vm_pu"]+np.random.normal(0,sigma_bus_v, len(self.net.res_bus.index))),
                    np.array(self.net.res_bus.iloc[:]["p_mw"]+np.random.normal(0,sigma_bus_pq, len(self.net.res_bus.index))),
                    np.array(self.net.res_bus.iloc[:]["q_mvar"]+np.random.normal(0,sigma_bus_pq, len(self.net.res_bus.index)))]

        line_data = [np.array(self.net.res_line.iloc[:]["p_from_mw"]+np.random.normal(0,sigma_line, len(self.net.res_line.index))),
                    np.array(self.net.res_line.iloc[:]["q_from_mvar"]+np.random.normal(0,sigma_line, len(self.net.res_line.index))),
                    np.array(self.net.res_line.iloc[:]["p_to_mw"]+np.random.normal(0,sigma_line, len(self.net.res_line.index))),
                    np.array(self.net.res_line.iloc[:]["q_to_mvar"]+np.random.normal(0,sigma_line, len(self.net.res_line.index)))
                    ]

        trafo_data = [np.array(self.net.res_trafo.iloc[:]["p_hv_mw"]+np.random.normal(0,sigma_trafo, len(self.net.res_trafo.index))),
                    np.array(self.net.res_trafo.iloc[:]["q_hv_mvar"]+np.random.normal(0,sigma_trafo, len(self.net.res_trafo.index))),
                    np.array(self.net.res_trafo.iloc[:]["p_lv_mw"]+np.random.normal(0,sigma_trafo, len(self.net.res_trafo.index))),
                    np.array(self.net.res_trafo.iloc[:]["q_lv_mvar"]+np.random.normal(0,sigma_trafo, len(self.net.res_trafo.index)))
                    ]
        busDF = pd.DataFrame(bus_data, index=["vm_pu", "p_mw", "q_mvar"])
        lineDF = pd.DataFrame(line_data, index=["p_from_mw", "q_from_mvar", "p_to_mw", "q_to_mvar"])
        trafoDF = pd.DataFrame(trafo_data, index=["p_hv_mw", "q_hv_mvar", "p_lv_mw", "q_lv_mvar"])

        return busDF, lineDF, trafoDF 
    
    # Used to create a random load profile (to make the simulation appear realistic over time)
    def create_load_profile(self, n_ts=24, volatility=0.05):
        n = len(self.net.load.index)
        lsf = np.zeros([n_ts,n])
        lsf_values = np.zeros(n_ts)
        for i in range(0,n_ts):
            new_value=volatility*np.random.rand()
            if np.random.rand() > 0.5:
                lsf_values[i] = new_value
            else:
                lsf_values[i] = -new_value

        for i in range(n_ts):
            lsf[i,:] = 1 + lsf_values[i]
        
        return lsf
    
    # The main animation loop (running the power flow, measurment gathering, state estimation etc...)
    def animate(self, i, ax, lc, bc, tc, eg, loadc, genc, load_list_p, load_list_q, bv):
        try:
            self.update_animation = self.sim_queue.get(False)
        except queue.Empty:
            pass
        if self.update_animation:
            draw_list = [lc, bc, tc, eg, loadc, genc]
            self.net.load.loc[:, "p_mw"] *= load_list_p[i][:] 
            self.net.load.loc[:, "q_mvar"] *= load_list_q[i][:] 
            if len(self.net.bus.index)<14:
                del draw_list[2]
            pp.plotting.draw_collections(draw_list, ax=ax)
            
            pp.runpp(self.net, run_control=True, max_iteration=50, calculate_voltage_angles=True, init="results")
            self.get_measurements()
            # print(self.net.measurement)
            try:
                self.toggle_defense = self.defense_queue.get(False)
            except queue.Empty:
                pass
            
            raw_measurements = []
            
            
            for j in range(len(self.net.measurement.index)):
                element_type = copy(self.net.measurement.iloc[j]["element_type"])
                measurement_type = copy(self.net.measurement.iloc[j]["measurement_type"])
                element = copy(self.net.measurement.iloc[j]["element"])
                value = copy(self.net.measurement.iloc[j]["value"])
                if element_type == "bus":
                    if measurement_type =="v":
                        if self.last_attack.active:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, value, None, None, "attack"]
                            self.data_queue.put(record)
                        else:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, value, None, None, "no_attack"]
                            self.data_queue.put(record)
                    if measurement_type =="p":
                        if self.last_attack.active:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, None, value, None, "attack"]
                            self.data_queue.put(record)
                        else:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, None, value, None, "no_attack"]
                            self.data_queue.put(record)
                    if measurement_type =="q":
                        if self.last_attack.active:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, None, None, value, "attack"]
                            self.data_queue.put(record)
                        else:
                            raw_measurements.append(value)
                            record = [self.time_iteration, element, None, None, value, "no_attack"]
                            self.data_queue.put(record)

            filter(self.toggle_defense, raw_measurements)

            est.estimate(self.net, calculate_voltage_angles=True, init="results")


            # list of all bus indices
            buses = self.net.bus.index.tolist() 
            vm_pu = np.array(self.net.res_bus.iloc[:]['vm_pu'])
            vm_pu_est = np.array(self.net.res_bus_est.iloc[:]['vm_pu'])
            vm_kv = np.array(self.net.res_bus.iloc[:]['vm_pu'])*np.array(bv[:])
            vm_kv_est = np.array(self.net.res_bus_est.iloc[:]['vm_pu'])*np.array(bv[:])
            min = np.array(self.net.bus.iloc[:]['min_vm_pu'])*vm_pu
            max = np.array(self.net.bus.iloc[:]['max_vm_pu'])*vm_pu

            

            # if self.toggle_plot:
            #     plot_data = struct.pack("f f", vm_pu[0], vm_pu_est[0])
            #     self.socket.sendto(plot_data, (UDP_IP, PLOT_PORT))

            # try:
            #     self.data_queue.get(False)
            #     plot_data = struct.pack("f f", vm_pu[0], vm_pu_est[0])
            #     self.socket.sendto(plot_data, (UDP_IP, PLOT_PORT))
            #     self.toggle_plot = True
            # except queue.Empty:
            #     pass
            

            vm_kvr, vm_kvb, busesr, busesb = self.alarm(buses, vm_pu, vm_kv, max, min)
            vm_kvr_est, vm_kvb_est, busesr_est, busesb_est = self.alarm(buses, vm_pu_est, vm_kv_est, max, min)

            #  tuples of coordinates for drawing the values on the map
            coordsi = zip(self.net.bus_geodata.x.loc[buses].values-0.15, self.net.bus_geodata.y.loc[buses].values-0.15) 
            coords_r = zip(self.net.bus_geodata.x.loc[busesr].values-0.3, self.net.bus_geodata.y.loc[busesr].values+0.05)
            coords_b = zip(self.net.bus_geodata.x.loc[busesb].values-0.3, self.net.bus_geodata.y.loc[busesb].values+0.05)
            coords_r_e = zip(self.net.bus_geodata.x.loc[busesr_est].values-0.3, self.net.bus_geodata.y.loc[busesr_est].values+0.18)
            coords_b_e = zip(self.net.bus_geodata.x.loc[busesb_est].values-0.3, self.net.bus_geodata.y.loc[busesb_est].values+0.18)
            bic_idx = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.mod('%d', buses), coords=coordsi, zorder=3, color="blue")
            draw_list.append(bic_idx)
            if not len(vm_kvr)==0:
                bic_r = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvr), ' kV'), coords=coords_r, zorder=3, color=(0, 0, 1, 0.5))
                draw_list.append(bic_r)
            if not len(vm_kvb)==0: 
                bic_b = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvb), ' kV'), coords=coords_b, zorder=3, color="blue")
                draw_list.append(bic_b)
            if not len(vm_kvr_est)==0: 
                bic_r_est = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvr_est), ' kV'), coords=coords_r_e, zorder=3, color=(1, 0, 0, 1))
                draw_list.append(bic_r_est)
            if not len(vm_kvb_est)==0: 
                bic_b_est = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.add(np.char.mod('%.4f', vm_kvb_est), ' kV'), coords=coords_b_e, zorder=3, color="limegreen")
                draw_list.append(bic_b_est)

            self.time_iteration +=1 
            plt.cla()
            pp.plotting.draw_collections(draw_list, ax=ax)


    # Used to highlight the estimates with a value outside of the acceptable limits 
    def alarm(self, buses, vm_pu, vm_kv, max_pu, min_pu):

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