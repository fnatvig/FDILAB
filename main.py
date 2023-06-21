from multiprocessing import Process

import plotServer
import powerEngine_old
from PowerEngine import *
from GUI.CtrlPage1 import *
from GUI.CtrlPage2 import *
from GUI.CtrlPage3 import *
from GUI.CtrlWindow import *


# This is the main function of the whole application
if __name__ == "__main__": 
     
#     p = [Process(target=powerEngine_old.main), 
     #      Process(target=plotServer.main)] 
     # p[0].start(), p[1].start()
     
     ctrl = CtrlWindow()
     powerengine = PowerEngine()
     p = [Process(target=powerengine.main), 
          Process(target=plotServer.main)] 
     p[0].start(), p[1].start()
     ctrl.wait_for_confirmation()
     ctrl.protocol("WM_DELETE_WINDOW", lambda: ctrl.on_closing(p))
     ctrl.mainloop()


