import os
import pygame
import pygame_gui
import socket
import controlPanel_lv2
import controlPanel
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
PLOT_PORT = 5006

msg = [0, 14, 9, 2, 3, 4]


def main(prev_msg):
    pygame.init()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    pygame.display.set_caption('Control Panel')
    window_surface = pygame.display.set_mode((width, height))


    background = pygame.Surface((width, height))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((width, height), 'theme.json')
    rect = pygame.Rect((width-b_width)/2, 0.75*b_height, b_width, b_height)
    single_button = pygame_gui.elements.UIButton(relative_rect=rect,
                                                text='Single Bus Attack',
                                                manager=manager)
    
    rect = pygame.Rect((width-b_width)/2, 0, b_width, b_height)
    rect.bottom =  -0.75*b_height  
    plot_button = pygame_gui.elements.UIButton(relative_rect=rect,
                                                text='Show Plot (bus 0)',
                                                manager=manager,
                                                anchors={'bottom': 'bottom'})
    
    # multi_layout = pygame.Rect((width-b_width)/2, 0, b_width, b_height)
    # multi_layout.bottom =  -0.75*b_height  
    # multi_button = pygame_gui.elements.UIButton(relative_rect=multi_layout, 
    #                                             text='Multiple Bus attack',
    #                                             manager=manager,
    #                                             anchors={'bottom': 'bottom'})
    rect = pygame.Rect(0, 0, 75, 50) 
    back_button = pygame_gui.elements.UIButton(relative_rect=rect,
                                                text='Back',
                                                manager=manager)


    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                packed_msg = struct.pack("i 12x", msg[0])
                sock.sendto(packed_msg, (UDP_IP, UDP_PORT))
                is_running = False
                os._exit(0)


            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == back_button:
                    is_running = False
                    controlPanel.main(prev_msg)
                if event.ui_element == single_button:
                    is_running = False
                    controlPanel_lv2.main(prev_msg)
                if event.ui_element == plot_button:
                    packed_msg = struct.pack("i 12x", msg[4])
                    sock.sendto(packed_msg, (UDP_IP, UDP_PORT))

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()