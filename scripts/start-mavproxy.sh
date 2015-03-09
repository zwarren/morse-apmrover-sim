#!/usr/bin/env bash

mavproxy.py --master=tcp:127.0.0.1:5760 --out=udp:127.0.0.1:14550 --console --map
