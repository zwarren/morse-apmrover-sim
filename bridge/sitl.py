#!/usr/bin/env python

import struct
import collections

import socket
import select
import time

from math import sqrt,atan2,degrees
from geomath import GeoPoint, point_from_xy

# from SITL.h struct sitl_fdm
# all fields are doubles except for magic which is uint32

SITL_Fields = [
    'latitude', 'longitude', # degrees
    'altitude', # MSL
    'heading', # degrees
    'speedN', 'speedE', 'speedD', # m/s
    'xAccel', 'yAccel', 'zAccel', # m/s/s in body frame
    'rollRate', 'pitchRate', 'yawRate',  # degrees/s/s in earth frame
    'rollDeg', 'pitchDeg', 'yawDeg', # euler angles, degrees
    'airspeed', # m/s
]

SITL_FDM_DATA_FIELDS=17

class SITL_Sensors(object):
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.heading = 0
        self.speedN = 0
        self.speedE = 0
        self.speedD = 0
        self.xAccel = 0
        self.yAccel = 0
        self.zAccel = 0
        self.rollRate = 0
        self.pitchRate = 0
        self.yawRate = 0
        self.rollDeg = 0
        self.pitchDeg = 0
        self.yawDeg = 0
        self.airspeed = 0
        self.magic = 0x4c56414f

        self.struct = struct.Struct('d'*SITL_FDM_DATA_FIELDS + 'I')

        #self.origin = GeoPoint(-33.80784, 151.176614)
        self.origin = GeoPoint(-35.362938, 149.165085)

    def pack(self):
        return self.struct.pack(
            self.latitude, self.longitude, self.altitude,
            self.heading,
            self.speedN, self.speedE, self.speedD,
            self.xAccel, self.yAccel, self.zAccel,
            self.rollRate, self.pitchRate, self.yawRate,
            self.rollDeg, self.pitchDeg, self.yawDeg,
            self.airspeed, self.magic)

    def update_compound(self, d):
        pose = d['robot.pose']
        imu = d['robot.imu']
        velocity = d['robot.velocity']

        # MORSE X-axis is east Y-axis is north, speedD probably needs to be inverted but for car doesn't matter.

        self.latitude, self.longitude = point_from_xy(self.origin, pose['x'], pose['y'])
        self.altitude = pose['z']

        self.heading = -degrees(pose['yaw'])

        self.speedE, self.speedN, self.speedD = velocity['world_linear_velocity']

        self.xAccel, self.yAccel, self.zAccel = imu['linear_acceleration']
        self.zAccel *= -1 # switch otherwise the car is inverted.

        ang_vel = imu['angular_velocity']
        #self.rollRate = degrees(ang_vel[0])
        #self.pitchRate = degrees(ang_vel[1])
        self.yawRate = -degrees(ang_vel[2])

        #self.rollDeg = degrees(pose['roll'])
        #self.pitchDeg = degrees(pose['pitch'])
        self.yawDeg = -degrees(pose['yaw'])

    def __str__(self):
        l = []
        for name in SITL_Fields:
            l.append(name + ':' + str(getattr(self, name)))
        return ', '.join(l)


