from morse.builder import *

from math import pi

class Minihummer(Robot):
    """
    A template robot model for MiniHummer, with a motion controller and a pose sensor.
    """
    def __init__(self, name = None, debug = True):

        # MiniHummer.blend is located in the data/robots directory
        Robot.__init__(self, 'RoverSim/robots/MiniHummer.blend', name)
        self.properties(classpath = "RoverSim.robots.MiniHummer.Minihummer")

        self.add_default_interface('socket')

        ###################################
        # Actuators
        ###################################

        self.motion = SteerForce()
        self.motion.add_stream('socket')
        self.append(self.motion)

        ###################################
        # Sensors
        ###################################

        self.odometry = Odometry()
        self.odometry.level('raw')
        self.odometry.frequency(10)
        #self.odometry.add_stream('socket')
        self.append(self.odometry)

        self.pose = Pose()
        #self.pose.frequency(10)
        #self.pose.add_stream('socket')
        self.append(self.pose)

        self.imu = IMU()
        #self.imu.frequency(10)
        #self.imu.add_stream('socket')
        self.append(self.imu)

        self.velocity = Velocity()
        self.append(self.velocity)

        self.compound_sensor = CompoundSensor([self.pose, self.imu, self.velocity])
        self.compound_sensor.frequency(100)
        self.compound_sensor.add_stream('socket')
        self.append(self.compound_sensor)

        if False:
            self.scanner = Hokuyo()
            self.scanner.translate(0, 2.5/3, 0)
            self.scanner.rotate(0, 0, pi/2)
            self.scanner.frequency(10)
            self.scanner.properties(scan_window=180);
            self.scanner.properties(laser_range=5)
            self.scanner.properties(resolution=5)
            self.scanner.properties(Visible_arc=True)
            self.append(self.scanner)
            self.scanner.add_stream('socket')
        elif True:
            self.range_left = Infrared()
            self.append(self.range_left)

            self.range_right = Infrared()
            self.append(self.range_right)

            for sensor, side in ((self.range_left, -1), (self.range_right, 1)):
                sensor.properties(scan_window=10)
                sensor.properties(laser_range=5)
                sensor.properties(resolution=0.1)
                sensor.translate(side*0.25, 2.3/3, 0)
                sensor.rotate(0, 0, pi/2 - side*0.1)
                #sensor.add_stream('socket')

            self.compound_range = CompoundSensor([self.range_left, self.range_right])
            self.append(self.compound_range)

