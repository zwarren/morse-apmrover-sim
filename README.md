This is an attempt at hooking the MORSE robotics simulator up to the Ardupilot APMRover2 program.

It's a SITL (Software-In-The-Loop) system, based on Ardupilot's JSBSim SITL system. Info about the JSBSim SITL system here: 
http://dev.ardupilot.com/wiki/simulation-2/setting-up-sitl-on-linux/

The code in this repository includes:
* a MORSE simulation environment with a shrunken version of MORSE's Hummer vehicle with some sensors attached.
* a Python script that receives sensor data from the simulation in JSON format and converts it to Ardupilot's SITL format and vice-versa (the bridge).

# Setup

MORSE is only supported on Linux. The steps of the Ardupilot SITL setup on Windows describe setting up an Ubuntu VM. Follow those instructions to get a Linux VM on windows:
http://dev.ardupilot.com/wiki/simulation-2/setting-up-sitl-on-windows/

## Install MORSE

Instructions are here:
https://www.openrobots.org/morse/doc/stable/user/installation.html

This simulation was last run using MORSE version 1.2.2.

MORSE relies on Python3. The bridge script uses Python's new asyncio module which was introduced in Python 3.4 so use at least 3.4. Ubuntu 14.04 and Fedora 21 provide Python 3.4 so it should be no trouble.

## Install MAVProxy

The JSBSim instructions use MAVProxy, so that's what's used here:
http://tridge.github.io/MAVProxy/

## Clone this repo

Clone it!

## Build APMRover2

The Ardupilot APMRover2 setup is based on the JSBsim. Follow the Ardupilot instructions up to installing JSBSim:
http://dev.ardupilot.com/wiki/simulation-2/setting-up-sitl-on-linux/

There are some small changes in the APM code to get the range finder sensors working in simulation. Apply the patch:
```
cd ardupilot
patch -p1 -i ~/src/morse-apmrover-sim/patches/ardupilot-sitl-recv-rngfnd.diff
```

Build the APMRover2 executable:
```
cd APMRover2
make sitl
```

# Running

Running the simulation involves running 4 programs in parallel. A few of these write a lot to the console so it's easier to run them in separate terminals.

```
# in term 1, start the simulator
cd rover-sim/simulation
./run.sh

# in term 2, start the bridge script
./rover-sim/bridge/bridge.py

# in term 3, start APMRover2
cd ardupilot/APMRover2
./APMRover2

# in term 4, start MAVProxy.
./rover-sim/scripts/start-mavproxy.sh
```

To check it's working, on the MAVProxy map window, right click and select "Fly to". You should see the car move on the map and also move in the MORSE window.

## Manual Control

The vehicle's throttle and steering can be set directly using the send-pwms.py in the scripts directory. The script must be provided two values in the range 1000 to 2000. The first value is the steering, the second is the throttle.
```
./scripts/send-pwms.py 1500 1500 # steering straight ahead, zero throttle
./scripts/send-pwms.py 1600 1500 # turn the wheels to the right, zero throttle.
./scripts/send-pwms.py 1500 1600 # straight ahead with a small amount of throttle.
```

## Setting up Collision Sensors

The MORSE simulation provides collision sensors but APMRover2 does not have them enabled by default.

To enable the collision sensors, in MAVproxy's command window write:
```
param set RNGFND_TYPE 1
param set RNGFND2_TYPE 1
param set RNGFND_PIN 2
param set RNGFND2_PIN 3
param set RNGFND_SCALING 1
param set RNGFND2_SCALING 1
param set SIM_SONAR_SCALE 1
```

It's important to use pins 2 and 3. If other pin numbers are used the simulation won't work.

These settings are saved in the "eeprom.bin" created by APMRover2.elf so they don't need to be run every time.

The default obstacle trigger distance, turn angle and turn time don't work so well for the simulated car. These parameters can be tuned as follows (the given values aren't great either!).
```
param set RNGFND_TRIGGR_CM 300
param set RNGFND_TURN_ANGL 70
param set RNGFND_TURN_TIME 1.5
```

