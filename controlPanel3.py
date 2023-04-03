import os
import pygame
import pygame_gui
import socket
import controlPanel2
import struct

#Control panel size
width=600
height=200

#Button size
b_width = 200
b_height = 50



# Socket settings
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

msg = [0, 14, 9, 2, 3, 4]


def main(prev_msg):
    pygame.init()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    pygame.display.set_caption('Single Bus Attack')
    window_surface = pygame.display.set_mode((width, height))


    background = pygame.Surface((width, height))
    background.fill(pygame.Color('#000000'))
    
    manager = pygame_gui.UIManager((width, height), 'theme.json')

    # label_layout = pygame.Rect(0, 50, 75, 50)
    # label = pygame_gui.elements.UITextBox("Bus: ", relative_rect=label_layout, manager=manager)
    rect = pygame.Rect(0, 50, 75, 50)
    pygame_gui.elements.UILabel(rect, text="Bus:", manager=manager)
    bus_list = list(range(int(prev_msg))) 
    bus_list = [str(i) for i in bus_list]
    rect = pygame.Rect(75, 50, 75, 50)
    bus_menu = pygame_gui.elements.UIDropDownMenu(bus_list, starting_option=bus_list[0], relative_rect=rect, manager=manager)

    rect = pygame.Rect(200, 50, 200, 50)
    pygame_gui.elements.UILabel(rect, text="Measurement type:", manager=manager)
    m_list = ["Voltage", "Active Power", "Reactive Power"]
    rect = pygame.Rect(400, 50, 200, 50)
    m_menu = pygame_gui.elements.UIDropDownMenu(m_list, starting_option=m_list[0], relative_rect=rect, manager=manager)

    rect = pygame.Rect(0, 100, 100, 50)
    pygame_gui.elements.UILabel(rect, text="Intensity:", manager=manager)

    
    rect = pygame.Rect(100, 100, 400, 50)
    intensity_bar = pygame_gui.elements.UIHorizontalSlider(rect, start_value=1.0, value_range=(0.0,2.0), manager=manager)
    
    rect = pygame.Rect(500, 100, 100, 50)
    intensity_label = pygame_gui.elements.UILabel(rect, text=str(intensity_bar.get_current_value()), manager=manager)

    rect = pygame.Rect(0, 150, 600, 50)
    run_button = pygame_gui.elements.UIButton(relative_rect=rect,
                                                text='Send attack',
                                                manager=manager)
    rect = pygame.Rect(0, 0, 75, 50) 
    back_button = pygame_gui.elements.UIButton(relative_rect=rect,
                                                text='Back',
                                                manager=manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            intensity_label.set_text(str(round(intensity_bar.get_current_value(), 3)))
            if event.type == pygame.QUIT:
                packed_msg = struct.pack("i 12x", msg[0])
                sock.sendto(packed_msg, (UDP_IP, UDP_PORT))
                is_running = False
                os._exit(0)
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == back_button:
                    is_running = False
                    controlPanel2.main(prev_msg)

                if event.ui_element == run_button:
                    bus = int(bus_menu.selected_option)
                    intensity = intensity_bar.get_current_value()
                    m_type = None
                    attack_struct = None
                    match m_menu.selected_option:
                        case "Voltage":
                            m_type = b'v'                            
                            attack_struct = struct.pack('i i s f', msg[3], bus, m_type, intensity)
                        case "Active Power": 
                            m_type = b'p'                                
                            attack_struct = struct.pack('i i s f', msg[3], bus, m_type, intensity)
                        case _:
                            m_type = b'q'    
                            attack_struct = struct.pack('i i s f', msg[3], bus, m_type, intensity)
                    
                    sock.sendto(attack_struct, (UDP_IP, UDP_PORT))


                    # sock.sendto(msg[3], (UDP_IP, UDP_PORT))

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()