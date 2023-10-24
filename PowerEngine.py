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
import time
import sys

from constants import *
from FDIA import *
from Preprocessor import *
from Defense import *
# from scripts.autoencoder_9bus import *
# from scripts.perfect_classifier import *
from scenarios.Scenario import *
from scenarios.AttackBot import *
from scenarios.ModBot import *


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
        self.last_measurement = None
        self.scenario_toggle = False
        self.line_status = []
        self.scenario = None
        self.speed = 50
        self.attackbot = AttackBot()
        self.modbot = ModBot()
        self.defense = Defense()
        self.last_attack = FDIA(active=False)
        self.sim_queue, self.data_queue = Queue(), Queue()
        self.attack_queue, self.defense_queue = Queue(), Queue()
        self.plot_queue = Queue()
        self.grid_queue = Queue()
        self.memory = pd.DataFrame()
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0
        self.mse = []

        # Confirms that the PowerEngine object is initialized
        self.socket.sendto(POWERENGINE_READY, (UDP_IP, GUI_PORT1))
            
    def main(self):

        # Wait for user to choose a test case
        msg = self.socket.recv(128)
        if msg == LOAD30:        
            self.net = nw.case_ieee30()
        elif msg == LOAD9:        
            self.net = nw.case9()        
        if not self.net == None:
            print("Test case loaded!")
        sim_process = Process(target=self.sim)
        sim_started = False
        buses, m_types, intensities = [], [], []
        lines, active = [], []
        while True:

            msg = self.socket.recv(128)

            if msg == START_SIM:
                if not sim_started:
                    sim_process.start() 
                    sim_started = True
                self.sim_queue.put(True)   
            
            elif (msg == LOAD_SCENARIO) and (not sim_started):
                self.scenario_toggle = True
                nr = self.socket.recv(128)
                self.scenario = Scenario(nr)
                self.attackbot.scenario = nr
                self.attackbot.set_active()
                self.modbot.scenario = nr
                self.modbot.number_of_buses = len(self.net.bus.index)
                self.modbot.set_active()
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

            elif msg == ACTIVATE_PLOT:
                self.plot_queue.put(True)
            
            elif msg == ACTIVATE_DEFENSE:
                print("Defense activated!")
                self.defense_queue.put(True)
                script = bytes.decode(self.socket.recv(128), "utf-8")
                self.defense_queue.put(script) 
            
            elif msg == DEACTIVATE_DEFENSE:
                print("Defense deactivated!")
                self.defense_queue.put(False)

            elif msg == SAVE_SIM:
                self.sim_queue.put(False)    
                size = self.data_queue.qsize()
                self.df = pd.DataFrame(columns=["time", "bus", "V", "P", "Q", "grid_modified", "label"])
                for i in range(size):

                    print(f"Exporting simulation... {i}/{size}", end="\r")
                    self.df.loc[len(self.df)] = self.data_queue.get()
                preprocessor = Preprocessor(self.df)
                preprocessor.sort()
                self.df = preprocessor.df
                sim_process.kill()
                self.filename = bytes.decode(self.socket.recv(1024),"utf-8")

            elif msg == EXPORT_CSV:
                if not os.path.exists("data_exports"):
                    os.mkdir("data_exports")
                self.df.to_csv("data_exports/"+self.filename+".csv")
                print("The simulation has been successfully exported!")


            elif msg == EXPORT_EXCEL:
                if not os.path.exists("data_exports"):
                    os.mkdir("data_exports")
                self.df.to_excel("data_exports/"+self.filename+".xlsx")
                print("The simulation has been successfully exported!")
            
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
                    # print(attack)
                    self.attack_queue.put(attack)

            elif unpacked[0] == MOD_GRID:
                line, status = struct.unpack('i i ? 7x', msg)[1:]
                lines.append(line)
                active.append(status)

            elif unpacked[0] == LAST_MOD_GRID:
                line, status = struct.unpack('i i ? 7x', msg)[1:]
                lines.append(line)
                active.append(status)
                if len(lines) == len(self.net.line.index):
                    self.grid_queue.put(active)
                    lines, active = [], []

    def reset(self):
        self.time_iteration = 0
        self.df = None
        self.net = None
        self.toggle_plot = False
        self.toggle_defense = False
        self.update_animation  = True
        self.last_measurement = None
        self.line_status = []
        self.scenario_toggle = False
        self.scenario = None
        self.speed = 50
        self.attackbot = AttackBot()
        self.modbot = ModBot()
        self.defense = Defense()
        self.last_attack = FDIA(active=False)
        self.sim_queue, self.data_queue = Queue(), Queue()
        self.attack_queue, self.defense_queue = Queue(), Queue()
        self.plot_queue = Queue()
        self.grid_queue = Queue()
        self.memory = pd.DataFrame()
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0
        self.mse = []
        # Confirms that the PowerEngine object is initialized
        self.socket.sendto(POWERENGINE_READY, (UDP_IP, GUI_PORT1))

    def gen(self):
        i = 0
        while (self.time_iteration < self.n_iterations):
            i += 1
            yield i
        print("Simulation finished.")

    def sim(self):
        is_running = True
        while True:

            if is_running:
                
                base_values = self.net.bus.iloc[:]['vn_kv'].tolist()

                pp.runpp(self.net, run_control=True, calculate_voltage_angles=True, init='dc')
                self.get_measurements()
                est.estimate(self.net, calculate_voltage_angles=True, init="flat")

                sys.stdout = open(os.devnull, 'w')
                lines_in_service = []
                for i in range(len(self.net.line.index)):
                    if self.net.line.iloc[i]["in_service"] == True:
                        lines_in_service.append(self.net.line.index[i])
                lc = pp.plotting.create_line_collection(self.net, lines=lines_in_service, color="black", zorder=1, use_bus_geodata=True)
                bc = pp.plotting.create_bus_collection(self.net, self.net.bus.index, size=0.03, color="b", zorder=2)
                eg = pp.plotting.create_ext_grid_collection(self.net, color="black", size=0.1, zorder=1, orientation=3.14159) 
                loadc = pp.plotting.create_load_collection(self.net, color="black", zorder=1, size=0.1) 
                tc = pp.plotting.create_trafo_collection(self.net, color="black", size=0.05, zorder=1)
                genc = pp.plotting.create_gen_collection(self.net, size=0.1, color="black", zorder=1, orientation=3.14159*2) 
                brc = pp.plotting.create_bus_bus_switch_collection(self.net, size=0.05)
                self.line_status = len(self.net.line.index)*[True]
                sys.stdout = sys.__stdout__
                n_ts =  500
                volatility=0.02
                load_prof_p, load_prof_q = None, None
                repeat = True
                if self.scenario_toggle:
                    load_prof_p = self.scenario.create_load_profile(net=self.net)
                    load_prof_q = self.scenario.create_load_profile(net=self.net)
                else:
                    load_prof_p = self.create_load_profile(n_ts, volatility)
                    load_prof_q = self.create_load_profile(n_ts, volatility)
                    self.n_iterations = n_ts
                self.update_animation = True

                fig, ax = plt.subplots(figsize=(6, 6))
                fig.canvas.manager.set_window_title('Network Window')
                plt.subplots_adjust(left=0.0, bottom=0.0, top=1.0, right=1.0)
                drawlist = [lc, bc, eg]
                if len(self.net.bus.index) > 9:
                    drawlist.append(tc)
                
                pp.plotting.draw_collections([lc, bc, eg], ax=ax)
                self.n_iterations = len(load_prof_p)
                self.modbot.t_end = self.n_iterations
                ani = animation.FuncAnimation(fig, self.animate, fargs=(ax, bc, lc, tc, eg, loadc, genc, brc, load_prof_p, load_prof_q, base_values), frames =self.gen, interval=self.speed, save_count=500, cache_frame_data=True, repeat=False) 
                plt.show()

                
    
    def get_measurements(self):
        seed = False 
        if self.scenario_toggle:
            seed = True

        bus_data, line_data, trafo_data = self.add_noise(SIGMA_BUS_V, SIGMA_BUS_PQ, SIGMA_LINE, SIGMA_TRAFO, seed=self.scenario_toggle)
        
        if self.scenario_toggle:
            if self.time_iteration > 0:
                if self.attackbot.active:
                    intensities, m_types = self.attackbot.main(self.net.bus.index)
                    attack = FDIA(True, "bus", list(range(len(self.net.bus))), m_types, 1, intensities)
                    attack.fill_attack_vector(self.net)
                    bus_data, line_data, trafo_data = attack.execute_attack(bus_data, line_data, trafo_data)
                    # print(attack.get_attributes())
                    atr1, atr2, atr3, atr4, atr5, atr6, atr7 = attack.get_attributes()
                    self.last_attack = FDIA(atr1, atr2, atr3, atr4, atr5, atr6)
                    self.last_attack.fill_attack_vector(self.net)
        else:
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
    def add_noise(self, sigma_bus_v, sigma_bus_pq, sigma_line, sigma_trafo, seed=False):
        # if seed:
        #     np.random.seed(1)
        # else:
        #     np.random.seed(1)
        np.random.seed(1)

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
    

    def moving_window(self, current_state, memory_length=100):
        if len(self.memory) == 0:
            self.memory = pd.DataFrame([current_state])
        else:
            self.memory.loc[len(self.memory)] = current_state

        if len(self.memory)>memory_length:
            self.memory.drop(0)


        
    # Used to create a random load profile (to make the simulation appear realistic over time)
    def create_load_profile(self, n_ts, volatility):
        n = len(self.net.load.index)
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
    
    # The main animation loop (running the power flow, measurement gathering, state estimation etc...)
    def animate(self, i, ax, bc, lc, tc, eg, loadc, genc, brc, load_list_p, load_list_q, bv):
        try:
            # self.update_animation = self.anim_queue.get(False)
            self.update_animation = self.sim_queue.get(False)
        except queue.Empty:
            pass

        if self.update_animation:

            if self.scenario_toggle:
                if self.time_iteration > 0:
                    if self.modbot.active:
                        self.line_status = self.modbot.main(self.net.line.index, self.time_iteration)
            try:
                self.line_status = self.grid_queue.get(False)
            except queue.Empty:
                pass

            for i in range(len(self.line_status)):
                self.net.line.in_service.at[i] = self.line_status[i]
            
            lines_in_service = []
            for i in range(len(self.net.line.index)):
                if self.net.line.iloc[i]["in_service"] == True:
                    lines_in_service.append(self.net.line.index[i])
                        
            lc = pp.plotting.create_line_collection(self.net, lines=lines_in_service, color="black", zorder=1, use_bus_geodata=True)

            draw_list = [lc, bc, eg, loadc, genc, brc]
            if len(self.net.bus.index) == 30:
                draw_list.append(tc)
            self.net.load.loc[:, "p_mw"] *= load_list_p[self.time_iteration][:] 
            self.net.load.loc[:, "q_mvar"] *= load_list_q[self.time_iteration][:] 
            
            # if len(self.net.trafo) != 0:
            #     print("hej")
            # del draw_list[2]

            pp.plotting.draw_collections(draw_list, ax=ax)
            
            try:
                pp.runpp(self.net, run_control=True, max_iteration=400, calculate_voltage_angles=True, tolerance_mva=1e-7, init="results", numba=True)
            except pp.powerflow.LoadflowNotConverged:
                pp.runpp(self.net, run_control=True, max_iteration=400, calculate_voltage_angles=True, tolerance_mva=1e-6, numba=True)
            self.get_measurements()
            # print(self.net.measurement)

            grid_modified = "False"
            if self.line_status != len(self.net.line.index)*[True]:
                grid_modified = "True"
            
            raw_measurements = []
            
            for j in range(len(self.net.measurement.index)):
                element_type = copy(self.net.measurement.iloc[j]["element_type"])
                measurement_type = copy(self.net.measurement.iloc[j]["measurement_type"])
                element = copy(self.net.measurement.iloc[j]["element"])
                value = copy(self.net.measurement.iloc[j]["value"])
                
                if element_type == "bus":
                    if measurement_type =="v":
                        if self.last_attack.active:
                            record = [self.time_iteration, element, value, None, None, grid_modified, "attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)
                        else:
                            record = [self.time_iteration, element, value, None, None, grid_modified, "no_attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)
                    if measurement_type =="p":
                        if self.last_attack.active:
                            record = [self.time_iteration, element, None, value, None, grid_modified, "attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)
                        else:
                            record = [self.time_iteration, element, None, value, None, grid_modified, "no_attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)
                    if measurement_type =="q":
                        if self.last_attack.active:
                            record = [self.time_iteration, element, None, None, value, grid_modified, "attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)
                        else:
                            record = [self.time_iteration, element, None, None, value, grid_modified, "no_attack"]
                            raw_measurements.append(record)
                            self.data_queue.put(record)

            df = pd.DataFrame(raw_measurements, columns=["time", "bus", "V", "P", "Q", "grid_modified", "label"])
            pre = Preprocessor(df)
            pre.sort_instant()
            try:
                toggle = self.defense_queue.get(False)
                self.defense.set_active(toggle)
                try:
                    script = self.defense_queue.get(False)
                    self.defense.set_script(script)
                except queue.Empty:
                    pass
            except queue.Empty:
                pass
            
            verdict = self.defense.filter(pre.df, self.memory)

            if verdict == "attack":
                
                if (self.time_iteration == 0) and (self.defense.active == True):                    
                    self.last_measurement = copy(self.net.measurement)
                else:
                    self.net.measurement = copy(self.last_measurement)

                if verdict == pre.df.iloc[0]["label"]:
                    print("Attack detected (True Positive)")
                    self.tp +=1
                else:
                    print("Normal observation misclassified as attacked (False Positive)")
                    self.fp +=1
            else:
                self.last_measurement = copy(self.net.measurement)
                
                if verdict == pre.df.iloc[0]["label"]:
                    self.tn +=1
                else:
                    print("An attack occured without being detected (False Negative)")
                    self.fn +=1
            try:
                est.estimate(self.net, calculate_voltage_angles=True, tolerance=1e-5, init="results")
            except ValueError:
                est.estimate(self.net, calculate_voltage_angles=True, tolerance=1e-5)
            # print(self.evaluate())

            # list of all bus indices
            buses = self.net.bus.index.tolist() 
            vm_pu = np.array(self.net.res_bus.iloc[:]['vm_pu'])
            vm_pu_est = np.array(self.net.res_bus_est.iloc[:]['vm_pu'])
            vm_kv = np.array(self.net.res_bus.iloc[:]['vm_pu'])*np.array(bv[:])
            # vm_kv = np.array(self.net.res_bus.iloc[:]['vm_pu'])*np.array(bv[:])
            vm_kv_est = np.array(self.net.res_bus_est.iloc[:]['vm_pu'])*np.array(bv[:])
            minimum = np.array(self.net.bus.iloc[:]['min_vm_pu'])*vm_pu
            maximum = np.array(self.net.bus.iloc[:]['max_vm_pu'])*vm_pu



            
            try:
                self.toggle_plot = self.plot_queue.get(False)
            except queue.Empty:
                pass

            mse, mae = self.evaluate()
            self.mse.append(float(mse))

            if self.toggle_plot:
                plot_data = struct.pack("f f", mse, mae)
                self.socket.sendto(plot_data, (UDP_IP, PLOT_PORT))

            vm_kvr, vm_kvb, busesr, busesb = self.alarm(buses, vm_pu, vm_kv, maximum, minimum)
            vm_kvr_est, vm_kvb_est, busesr_est, busesb_est = self.alarm(buses, vm_pu_est, vm_kv_est, maximum, minimum)

            #  tuples of coordinates for drawing the values on the map
            coordsi = zip(self.net.bus_geodata.x.loc[buses].values-0.15, self.net.bus_geodata.y.loc[buses].values-0.15) 
            coords_r = zip(self.net.bus_geodata.x.loc[busesr].values-0.3, self.net.bus_geodata.y.loc[busesr].values+0.05)
            coords_b = zip(self.net.bus_geodata.x.loc[busesb].values-0.3, self.net.bus_geodata.y.loc[busesb].values+0.05)
            coords_r_e = zip(self.net.bus_geodata.x.loc[busesr_est].values-0.3, self.net.bus_geodata.y.loc[busesr_est].values+0.18)
            coords_b_e = zip(self.net.bus_geodata.x.loc[busesb_est].values-0.3, self.net.bus_geodata.y.loc[busesb_est].values+0.18)
            
            lines_geodata_x = []
            lines_geodata_y = []
            for line in self.net.line.index.tolist():
                from_bus = self.net.line.iloc[line]["from_bus"]
                from_bus_x = self.net.bus_geodata.x.loc[from_bus]
                from_bus_y = self.net.bus_geodata.y.loc[from_bus]
                to_bus = self.net.line.iloc[line]["to_bus"]
                to_bus_x = self.net.bus_geodata.x.loc[to_bus]
                to_bus_y = self.net.bus_geodata.y.loc[to_bus]

                lines_geodata_x.append(from_bus_x+(to_bus_x-from_bus_x)/2)
                lines_geodata_y.append(from_bus_y+(to_bus_y-from_bus_y)/2)

            coords_lines = zip(lines_geodata_x, lines_geodata_y)
            t_x = math.floor(min(self.net.bus_geodata.iloc[:]['x']))
            t_y = math.ceil(max(self.net.bus_geodata.iloc[:]['y']))
            t_col = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.add('t = ', np.char.mod('%d', [self.time_iteration])), coords=zip([t_x],[t_y]), zorder=3, color="black")
            draw_list.append(t_col)
            lines_idx = pp.plotting.create_annotation_collection(size=0.13, texts=np.char.mod('%d', self.net.line.index.tolist()), coords=coords_lines, zorder=3, color="black")
            # print(self.net.line)
            # print(len(self.net.line.index))
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

            draw_list.append(lines_idx)

            self.time_iteration +=1 

            plt.cla()

            pp.plotting.draw_collections(draw_list, ax=ax)

            if self.time_iteration == self.n_iterations:
                print("\n________SIMULATION_RESULTS________")
                print("total MSE = ", sum(self.mse))
                print("max MSE = ", max(self.mse))
                if (self.tp+self.fp) != 0:
                    print("Precision = ", self.tp/(self.tp+self.fp))
                if (self.tp+self.fn) != 0:
                    print("Recall = ", self.tp/(self.tp+self.fn))
                print("\n")
                if self.scenario_toggle:

                    return -1

        

    def evaluate(self):
        sum_mse = 0
        sum_mae = 0
        for i in range(len(self.net.bus.index)):
            sum_mse += (self.net.res_bus.iloc[i]['vm_pu']-self.net.res_bus_est.iloc[i]['vm_pu'])*(self.net.res_bus.iloc[i]['vm_pu']-self.net.res_bus_est.iloc[i]['vm_pu'])
            sum_mae += abs(self.net.res_bus.iloc[i]['vm_pu']-self.net.res_bus_est.iloc[i]['vm_pu'])

        
        return sum_mse/len(self.net.bus.index), sum_mae/len(self.net.bus.index)
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