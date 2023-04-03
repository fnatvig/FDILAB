import pygame
import pygame_gui
import socket
import controlPanel2
import os
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


def main():
    pygame.init()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    pygame.display.set_caption('Control Panel')
    window_surface = pygame.display.set_mode((width, height))


    background = pygame.Surface((width, height))
    background.fill(pygame.Color('#000000'))

    manager = pygame_gui.UIManager((width, height), 'theme.json')

    case14_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((width-b_width)/2, 0.75*b_height), (b_width, b_height)),
                                                text='Load case 14',
                                                manager=manager)


    case9_layout = pygame.Rect((width-b_width)/2, 0, b_width, b_height)
    case9_layout.bottom =  -0.75*b_height  
    case9_button = pygame_gui.elements.UIButton(relative_rect=case9_layout,
                                                text='Load case 9',
                                                manager=manager,
                                                anchors={'bottom': 'bottom'})
    


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
                if event.ui_element == case14_button:
                    packed_msg = struct.pack("i 12x", msg[1])
                    sock.sendto(packed_msg, (UDP_IP, UDP_PORT))
                    is_running = False
                    controlPanel2.main(msg[1])
                elif event.ui_element == case9_button:
                    packed_msg = struct.pack("i 12x", msg[2])
                    sock.sendto(packed_msg, (UDP_IP, UDP_PORT))
                    controlPanel2.main(msg[2])

            manager.process_events(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()