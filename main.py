from multiprocessing import Process

import plotServer
import powerEngine_old
from PowerEngine import *
from GUI.PageOne import *
from GUI.PageTwo import *
from GUI.PageThree import *
from GUI.GuiApp import *


# This is the main function of the whole application
if __name__ == "__main__": 
     
#     p = [Process(target=powerEngine_old.main), 
     #      Process(target=plotServer.main)] 
     # p[0].start(), p[1].start()
     
     app = GuiApp()
     powerengine = PowerEngine()
     p = [Process(target=powerengine.main), 
          Process(target=plotServer.main)] 
     p[0].start(), p[1].start()
     app.wait_for_confirmation()
     app.protocol("WM_DELETE_WINDOW", lambda: app.on_closing(p))
     app.mainloop()


