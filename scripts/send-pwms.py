#!/usr/bin/env python3

import sys
import array
import socket

#send throttle and steer pwm values to APMrover
# the values should be in the range 1000...2000,
# 1500 is middle, so zero throttle and steering angle.

if __name__ == '__main__':
    steer = int(sys.argv[1])
    throttle = int(sys.argv[2])

    a = [0]*8
    a[0] = steer
    a[2] = throttle

    d = array.array('H', a)

    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(d, ('127.0.0.1', 5501))
