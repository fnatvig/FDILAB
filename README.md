# FDIASIM
A False Data Injection Attack (FDIA) Simulator

# Prerequisites
The application is only tested with python version Python 3.10.10, although I believe one should be able to run the application with older versions of python as well. Other than that, there are a couple of python libraries that need to be installed beforehand: 
1. Pandapower https://pandapower.readthedocs.io/en/v2.10.1/about.html
3. pygame https://www.pygame.org/news
5. pygame_gui https://pygame-gui.readthedocs.io/en/v_067/
6. matplotlib https://matplotlib.org/

# Instructions
1. Clone the repo and cd into it with a terminal/cmd
2. Run the command: python main.py
3. Wait until the control panel window pops up
4. Click on one of the buttons and wait until a second window pops up. 
5. Now you can see the values of the actual voltage magnitudes (shown in blue) and estimated values (shown in black/red). The values are shifting because the network's loads are varied with time. 
6. Here you have the ability to see a plot over the voltage at bus 0, by clicking "Show Plot (bus 0)". 
7. You also have the possibility to send single bus attacks into the network and observe how the network reacts. This is done by clicking the "single bus attack" button.

# How to interpret the results
As for now, the map only shows how the actual and estimated voltage magnitudes vary with time. As written in the previous section, the values shown in blue (acquired with the pandapower powerflow calculator) should be interpreted as the ground truth. The black values are the resulting values of the state estimation. The black values turn red if the estimates fall outside of their specified ranges which are given in the test cases. 
