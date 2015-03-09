#!/usr/bin/env python3

import json
import re
import asyncio
import logging
import struct
import array

from logging import error, warning, info, debug
from math import radians

from sitl import SITL_Sensors
from line_client import LineClient
from pilot_client import PilotClient

def clamp(val, min_val, max_val):
    if val > max_val:
        return max_val
    if val < min_val:
        return min_val
    return val

class BridgeMain:
    def __init__(self, sim_host='localhost', sim_port=4000):
        self.sim_host = sim_host
        self.service_port = sim_port

        # MORSE service client, used for getting ports for the sensor and control services.
        self.service_client = LineClient(self.service_connect, self.service_message, self.service_disconnect)
        asyncio.async(self.service_client.connect(self.sim_host, self.service_port))

        # connections to MORSE components
        self.motion_client = LineClient(self.motion_connect, self.motion_message, self.motion_disconnect)
        #self.range_client = LineClient(self.range_connect, self.range_message, self.range_disconnect)
        self.compound_range_client = LineClient(self.compound_range_connect, self.compound_range_message, self.compound_range_disconnect)
        #self.odometry_client = LineClient(self.odometry_connect, self.odometry_message, self.odometry_disconnect)
        #self.pose_client = LineClient(self.pose_connect, self.pose_message, self.pose_disconnect)
        #self.imu_client = LineClient(self.imu_connect, self.imu_message, self.imu_disconnect)
        self.compound_client = LineClient(self.compound_connect, self.compound_message, self.compound_disconnect)

        # for receiving commands from the pilot
        self.pilot = PilotClient(self.pilot_message)

        # the sensor values that the pilot wants to receive.
        self.sensors = SITL_Sensors()

        # for mapping PWM values to MORSE steering angle and throttle force.
        self.max_steer_degrees = 45
        self.max_throttle_force = 10

    def exit(self):
        asyncio.get_event_loop().stop()

    def send_service_message(self, identifier, component, message, data=[]):
        msg = '%s %s %s %s\n' % (identifier, component, message, json.dumps(data))
        self.service_client.send(msg)

    def get_stream_port(self, return_id, sensor_name):
        self.send_service_message(return_id, 'simulation', 'get_stream_port', [sensor_name])

    def service_connect(self):
        info("Connected to morse service.")
        self.get_stream_port('motion_port', 'robot.motion')
        #self.get_stream_port('range_port', 'robot.scanner')
        self.get_stream_port('compound_range_port', 'robot.compound_range')
        #self.get_stream_port('odometry_port', 'robot.odometry')
        #self.get_stream_port('pose_port', 'robot.pose')
        #self.get_stream_port('imu_port', 'robot.imu')
        self.get_stream_port('compound_port', 'robot.compound_sensor')

    def service_disconnect(self):
        info("Disconnected from morse service.")
        self.exit()

    def service_message(self, line):
        m = re.match('^(?P<id>\w+) (?P<success>\w+) (?P<data>.*)$', line)
        if m is None:
            warning('Invalid service message:' + line)
            return

        if m.group('success') != 'SUCCESS':
            warning('Service command failed:' + line)
            return

        identifier = m.group('id')
        data = m.group('data')

        if identifier == 'motion_port':
            asyncio.async(self.motion_client.connect(self.sim_host, int(data)))
        elif identifier == 'range_port':
            asyncio.async(self.range_client.connect(self.sim_host, int(data)))
        elif identifier == 'compound_range_port':
            asyncio.async(self.compound_range_client.connect(self.sim_host, int(data)))
        elif identifier == 'odometry_port':
            asyncio.async(self.odometry_client.connect(self.sim_host, int(data)))
        elif identifier == 'pose_port':
            asyncio.async(self.pose_client.connect(self.sim_host, int(data)))
        elif identifier == 'imu_port':
            asyncio.async(self.imu_client.connect(self.sim_host, int(data)))
        elif identifier == 'compound_port':
            asyncio.async(self.compound_client.connect(self.sim_host, int(data)))
        else:
            warning("Unhandled identifier:" + identifier)

    def motion_connect(self):
        info("Connected to motion port.")

    def motion_disconnect(self):
        info("Disconnected from motion port.")

    def motion_message(self, client, line):
        warning("Got unhandled motion message:" + line)

    # morse convention is +steer to the left and +force is backwards.
    # The controls class is switched so +steer is to the right and +force is forwards.
    def send_motion_message(self, steer, throttle, brake):
        if self.motion_client is not None:
            # the sign of the throttle is reversed!
            d = {'steer':-steer, 'force':-throttle, 'brake':brake}
            line = json.dumps(d) + '\n'
            self.motion_client.send(line)
        #else:
        #    warning('Cannot send motion message without connection to motion controller.')

    def pilot_message(self, pwms):  
        steer_pwm = clamp(pwms[0], 1000, 2000)
        throttle_pwm = clamp(pwms[2], 1000, 2000)
        steer = (steer_pwm - 1500)/500.0*radians(self.max_steer_degrees)
        throttle = (throttle_pwm - 1500)/500.0*self.max_throttle_force
        #print("Pilot steer %d throttle %d to MORSE %0.2f %02.f" % (pwms[0], pwms[2], steer, throttle))
        self.send_motion_message(steer, throttle, 0)

    def compound_connect(self):
        info("Connected to cmpound port.")

    def compound_disconnect(self):
        info("Disconnected from compound port.")

    def compound_message(self, line):
        try:
            obj = json.loads(line)
            #print('Compound:' + str(obj))
            self.sensors.update_compound(obj)
            #print(self.sensors)
            self.pilot.send(self.sensors.pack())
        except ValueError as err:
            warning("Invalid compound message:" + str(err))

    def range_connect(self):
        info("Connected to range port.")

    def range_disconnect(self):
        info("Disconnected from range port.")

    def range_message(self, line):
        try:
            obj = json.loads(line)
            #print(obj)
        except ValueError as err:
            error('Invalid range message:' + str(err))
            return

    def compound_range_connect(self):
        info("Connected to range port.")

    def compound_range_disconnect(self):
        info("Disconnected from range port.")

    def compound_range_message(self, line):
        try:
            obj = json.loads(line)
            #print(obj)
            left_range = min(obj['robot.range_left']['range_list'])
            right_range = min(obj['robot.range_right']['range_list'])
            self.pilot.send(struct.pack('Iff', 0xef10ab20,
                                        left_range, right_range))
            #print('Ranges: %f, %f' % (left_range, right_range))
        except ValueError as err:
            error('Invalid range message:' + str(err))
            return

    def odometry_connect(self):
        info("Connected to odometry port.")

    def odometry_disconnect(self):
        info("Disconnected from odometry port.") 

    def odometry_message(self, line):
        try:
            obj = json.loads(line)
            #print('Odometry:' + str(obj))
        except ValueError as err:
            warning('Invalid odometry message:' + str(err))

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    main = BridgeMain()

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

