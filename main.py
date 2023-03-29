import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from multiprocessing import Process
import controlPanel
import powerEngine
import plotServer
import time

# This is the main function of the whole application
if __name__ == "__main__": 
    # Like the name suggests, this process is responsible for the actual 
    # power grid simulation. This is where most things happen
    p1 = Process(target=powerEngine.main)
    p1.start()
    # This process is responsible for the gui (mostlly based on a module named "pygame")
    p2 = Process(target=controlPanel.main)
    p2.start()
    # This process is responsible for single bus plotting
    p3 = Process(target=plotServer.main)
    p3.start()


