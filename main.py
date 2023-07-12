from multiprocessing import Process

import plotServer
from PowerEngine import *
from GUI.CtrlPage1 import *
from GUI.CtrlPage2 import *
from GUI.CtrlWindow import *
from GUI.PlotServer import *

# This is the main function of the whole application
if __name__ == "__main__": 
     
     ctrl = CtrlWindow()
     powerengine = PowerEngine()     
     plotserver = PlotServer()
     while ctrl.running:
          try:
               p = [Process(target=powerengine.main), 
                    Process(target=plotserver.main)] 
               p[0].start(), p[1].start()
               ctrl.wait_for_confirmation()
               ctrl.p = p
               ctrl.protocol("WM_DELETE_WINDOW", lambda: ctrl.on_closing())
               ctrl.mainloop()
          except tk.TclError:
               pass


