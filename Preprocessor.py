import pandas as pd
import math
from copy import copy

class Preprocessor:
    def __init__(self, df):
        if len(df) > 0:
            self.raw_df = df
            self.bus_cardinality = len(set(df.iloc[:]["bus"]))
            bus_list = [f"bus_{i}" for i in range(self.bus_cardinality)]
            columns = ["time"]
            for bus in bus_list:
                columns.append("V_" + bus)
                columns.append("P_" + bus)
                columns.append("Q_" + bus)
            columns.append("label")

            self.df = pd.DataFrame(columns=columns)
        else:
            pass
    
    def sort_instant(self):
        m = 0
        net_data = []
        for i in range(self.bus_cardinality):
            bus_data = []
            for j in range(3):
                measurement = list(copy(self.raw_df.iloc[m]["V":"Q"]))
                if len(bus_data) == 0:
                    bus_data = measurement
                else:
                    bus_data = [bus_data[j] if not 
                                ((bus_data[j] == None) or 
                                 (math.isnan(bus_data[j]))) 
                                 else measurement[j] for j in range(3)]
                m+=1
            for j in range(3):
                net_data.append(bus_data[j])
        row = [self.raw_df.iloc[0]["time"]]
        for k in range(len(net_data)):
            row.append(net_data[k])
        row.append(self.raw_df.iloc[m-1]["label"])
        self.df.loc[len(self.df)] = row

    def sort(self):
        t, m = 0, 0
        t_end = self.raw_df.iloc[-1]["time"]
        print("t_end = ", t_end)
        while t < t_end:
            net_data=[]
            for i in range(self.bus_cardinality):
                bus_data = []
                for j in range(3):
                    print(m)
                    measurement = list(copy(self.raw_df.iloc[m]["V":"Q"]))
                    if len(bus_data) == 0:
                        bus_data = measurement
                    else:
                        bus_data = [bus_data[j] if not 
                                ((bus_data[j] == None) or 
                                 (math.isnan(bus_data[j]))) 
                                 else measurement[j] for j in range(3)] 
                    m+=1
                for j in range(3):
                    net_data.append(bus_data[j])
                
            row = [t]
            for k in range(len(net_data)):
                row.append(net_data[k])
            row.append(self.raw_df.iloc[m-1]["label"])
            self.df.loc[len(self.df)] = row
            t+=1

    def disassemble(self, data):
        arr = []
        for i in range(len(data)):
            subarr = []
            for j in range(1, len(data.columns)-1):
                subarr.append(data.iloc[i][data.columns[j]])
            arr.append(subarr)

        return arr




            # if self.raw_df.iloc[i]["bus"] == bus and (t < (t_end-1)):
            #     measurement = list(copy(self.raw_df.iloc[i]["V":"Q"]))
            #     print(measurement)
            #     if len(bus_data) == 0:
            #         bus_data = measurement
            #     else:
            #         bus_data = [bus_data[j] if not ((bus_data[j] == None) or (mif len(bus_data) == 0:
            #         bus_data = measurement
            #     else:
                
            #     m = i
            # else:
            #     for k in range(len(bus_data)):
            #         net_data.append(bus_data[k])
            #     print(bus_data)
            #     bus_data = []
            #     i-=1
            #     bus +=1 

            # if not (self.raw_df.iloc[m]["time"] == t):
            #     row = [t]
            #     for k in range(len(net_data)):
            #         row.append(net_data[k])
            #     row.append(self.raw_df.iloc[m-1]["label"])
            #     self.df.loc[len(self.df)] = row
            #     net_data = []
            #     bus=0
            #     t +=1

            # i +=1


            #     new_row = copy(self.raw_df.iloc[c][:])
            #     if len(row) == 0:
            #         row = new_row
            #     else:
            #         row = [row[j] if not (row[j] == None) else new_row[j] for j in range(len(row))]
                
            #     c+=1
            # else:
            #     self.df.loc[len(self.df)] = row
            #     t +=1
            #     row = []