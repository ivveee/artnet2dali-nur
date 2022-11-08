import logging

import asyncio
import socket
import threading
import time

from stupidArtnet import StupidArtnetServer


def init_channel_data():
    channel_data = {}
    channel_data[1] = lambda X,Y: f'LW-SET=1:{0 if X == 0 else 1}!'  # Motorscreen

    channel_data[2] = lambda X,Y: f'KNX-SET=1:{0 if X == 0 else 1}!'  # Ceiling light Back
    channel_data[3] = lambda X,Y: f'KNX-SET=3:{0 if X == 0 else 1}!'  # Ceiling light front
    channel_data[4] = lambda X,Y: f'KNX-SET=18:{0 if X == 0 else 1}!'  # Light Front Right
    channel_data[5] = lambda X,Y: f'KNX-SET=20:{0 if X == 0 else 1}!'  # Light Front Left
    channel_data[6] = lambda X,Y: f'KNX-SET=24:{0 if X == 0 else 1}!'  # Light Back Right
    channel_data[7] = lambda X,Y: f'KNX-SET=22:{0 if X == 0 else 1}!'  # Light Back left

    channel_data[8] = lambda X,Y: f'KNX-SET=26:{0 if X == 0 else 1}!'  # Motorscreen
    channel_data[9] = lambda X,Y: f'KNX-SET=9:{0 if X == 0 else 1}!'  # Window Blinds

    # spots 01 to 18
    spot_data = {10: 14, 11: 1, 12: 18,
                 13: 9, 14: 17, 15: 10,
                 16: 7, 17: 8, 18: 2,
                 19: 13, 20: 11, 21: 15,
                 22: 6, 23: 3, 24: 4,
                 25: 12, 26: 16, 27: 5}

    for channel in spot_data:
        def closure(channel_num):
            def f(X, Y):
                return f'DALI-SET={channel_num}:{X}:{Y}!'
            return f

        channel_data[channel] = closure(spot_data[channel])
    return channel_data


channel_data = init_channel_data()


def start_simulator():
    artnet_header = b'Art-Net\x00\x00P\x00\x0e\x05\x04\x02\x00\x02\x08'
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send artnet data
    def thread_function(g):
        while True:
            print("sending")
            artnet_data = bytearray()
            artnet_data.extend(artnet_header)
            dmx_packet_bytes = [2, 2]
            artnet_data.extend(bytes(dmx_packet_bytes))
            sock2.sendto(artnet_data, ('localhost', 6454))
            time.sleep(5)

    x = threading.Thread(target=thread_function, args=(1,))
    x.start()


def start_min_server():
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind(('', 5000))  # Listen on any valid IP
    print(socket_server)

    def thread_function(g):
        while True:
            data, unused_address = socket_server.recvfrom(27)
            print(data, " ", unused_address)

    x = threading.Thread(target=thread_function, args=(1,))
    x.start()


def prod_output(string):
    back = "\b" * len(string)
    erase = " " * len(string)
    print(string, end="")
    print(back, end="")
    print(erase, end="")
    print(back, end="")


def send_to_controller(sock, channel, arg, arg2):
    data_to_controller: str = channel_data[channel](arg, arg2) + '\r'
    str1 = f'To controller:{data_to_controller}'
    # prod_output(str1)
    print(str1)
    sock.sendto(bytes(data_to_controller, 'ascii'), ('localhost', 5000))


def main():
    a = StupidArtnetServer()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # print(channel_data[1](1))

    last_data = [-10] * len(channel_data)

    def test_callback(input_from_artnet):
        for channel_number in range(1, len(channel_data)):
            nonlocal last_data
            if last_data[channel_number] != input_from_artnet[channel_number]:
                send_to_controller(sock, channel_number, input_from_artnet[channel_number], 2)
                time.sleep(0.1)
            last_data[channel_number] = input_from_artnet[channel_number]
    a.register_listener(universe=2, is_simplified=False, callback_function=test_callback)

    while True:
        channel, arg = map(int, input(">").split())
        send_to_controller(sock, channel, arg, 2)


if __name__ == '__main__':
    # start_simulator()
    # start_min_server()

    main()

"""
Device	Value	Artnet Channel	UDP String	Comment
				
Motorscreen 1	1 / 0	1	LW-SET=x!	X= Artnet Value
				
Ceiling light Back	1 / 0 	2	KNX-SET=1:X!	
Ceiling light front	1 / 0	3	KNX-SET=3:X!	
Light Front Right	1 / 0	4	KNX-SET=18:X!	
Light Front Left	1 / 0	5	KNX-SET=20:X!	
Light Back Right	1 / 0	6	KNX-SET=24:X!	
Light Back left	1 / 0	7	KNX-SET=22:X!	
				
Motorscreen 2	1 / 0	8	KNX-SET=26:X!	
Window Blinds	1 / 0	9	KNX-SET=9:X!	
				
				
Spot: 01	0 - 254	10	DALI-SET=014:X:z!	Z= timing for dimmer: should a a variable in the script to change this global
Spot: 02	0 - 254	11	DALI-SET=001:X:z!	
Spot: 03	0 - 254	12	DALI-SET=018:X:z!	
Spot: 04	0 - 254	13	DALI-SET=009:X:z!	
Spot: 05	0 - 254	14	DALI-SET=017:X:z!	
Spot: 06	0 - 254	15	DALI-SET=010:X:z!	
Spot: 07	0 - 254	16	DALI-SET=007:X:z!	
Spot: 08	0 - 254	17	DALI-SET=008:X:z!	
Spot: 09	0 - 254	18	DALI-SET=002:X:z!	
Spot: 10	0 - 254	19	DALI-SET=013:X:z!	
Spot: 11	0 - 254	20	DALI-SET=011:X:z!	
Spot: 12	0 - 254	21	DALI-SET=015:X:z!	
Spot: 13	0 - 254	22	DALI-SET=006:X:z!	
Spot: 14	0 - 254	23	DALI-SET=003:X:z!	
Spot: 15	0 - 254	24	DALI-SET=004:X:z!	
Spot: 16	0 - 254	25	DALI-SET=012:X:z!	
Spot: 17	0 - 254	26	DALI-SET=016:X:z!	
Spot: 18	0 - 254	27	DALI-SET=005:X:z!	
"""
