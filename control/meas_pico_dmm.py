#!/usr/bin/python
import time
import control

control.initialize()

print " ".join(control.read_time_pico_dmm())

control.finalize()
