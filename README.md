# FDIASIM
A False Data Injection Attack (FDIA) Simulator

# Prerequisites
The application is only tested with python version Python 3.10.10, although I believe one should be able to run the application with slightly older python versions as well. However, older versions than 3.10 won't work (as the code contains "match case" statements). Other than that, there are a couple of python libraries that need to be installed beforehand:

1. Pandapower https://pandapower.readthedocs.io/en/v2.10.1/about.html
3. pygame https://www.pygame.org/news
5. pygame_gui https://pygame-gui.readthedocs.io/en/v_067/

# Instructions
1. Clone the repo, cd into it with git bash, run the command ``` git checkout stable ``` (to change to the stable branch). 
2. Run the command: python main.py
3. Wait until the control panel window pops up
4. Click on one of the buttons and wait until a second window pops up. 
5. Now you can see the values of the actual voltage magnitudes (shown in blue) and estimated values (shown in black/red). The values are shifting because the network's loads are varied with time. 
6. Here you have the ability to see a plot over the voltage at bus 0, by clicking "Show Plot (bus 0)". 
7. You also have the possibility to send single bus attacks into the network and observe how the network reacts. This is done by clicking the "single bus attack" button.

# How to interpret the results
As for now, the map only shows how the actual and estimated voltage magnitudes vary with time. As written in the previous section, the values shown in blue (acquired with the pandapower powerflow calculator) should be interpreted as the ground truth. The black values are the resulting values of the state estimation. The black values turn red if the estimates fall outside of their specified ranges which are given in the test cases (referred to as "optimal power flow parameters" in the pandapower documantation). 

# System Architecture
This section aims to describe the application's overall architecture. After reading this section, you will get a general sense of the most relevant components of the application. However, to understand the application more in-depth, please turn to the comments in the code. 

The figure below may clarify how the different modules are connected. The blue boxes represent the involved python modules, while the black arrows show how the modules depend on each other. For instance, powerEngine.py depends on FDIA.py, which explains why the arrow points from powerEngine.py to FDIA.py. Furthermore, the white boxes with curved black arrows show the most important processes defined in each module.

![architecture](https://user-images.githubusercontent.com/103872952/229731005-504d11e1-bfb9-4ce2-a358-cf32d610a2c6.png)

---TBD--- 
