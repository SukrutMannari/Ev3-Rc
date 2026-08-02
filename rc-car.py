#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_1
from evdev import InputDevice, list_devices, ecodes
import sys

drive_a = LargeMotor(OUTPUT_A)
drive_b = LargeMotor(OUTPUT_B)
steer = MediumMotor(OUTPUT_C)
light_sensor = ColorSensor(INPUT_1)

steer.reset()

devices = [InputDevice(p) for p in list_devices()]
gamepad = next((d for d in devices if 'pad' in d.name.lower() or 'controller' in d.name.lower()), None)

if not gamepad:
    print("Controller not found.")
    sys.exit()

def scale(val, in_min, in_max, out_min, out_max):
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

gas_val = 0
brake_val = 0
last_speed = 0
last_angle = 0
lights_on = False

# Start with sensor light off (Ambient Mode)
light_sensor.mode = ColorSensor.MODE_COL_AMBIENT

for event in gamepad.read_loop():
    
    if event.type == ecodes.EV_ABS:
        
        # Right D-Pad (Toggle Sensor Light)
        if event.code == ecodes.ABS_HAT0X:
            if event.value == 1:  
                lights_on = not lights_on
                if lights_on:
                    light_sensor.mode = ColorSensor.MODE_COL_COLOR  # RGB on (Looks White)
                else:
                    light_sensor.mode = ColorSensor.MODE_COL_AMBIENT  # Light off

        # Driving Inputs
        elif event.code == ecodes.ABS_RZ:
            gas_val = event.value
        elif event.code == ecodes.ABS_Z:
            brake_val = event.value
        elif event.code == ecodes.ABS_X: 
            target_angle = scale(event.value, 0, 255, -60, 60)
            if abs(target_angle - last_angle) >= 3:
                steer.on_to_position(speed=100, position=target_angle, block=False)
                last_angle = target_angle

        forward = scale(gas_val, 0, 255, 0, 100)
        reverse = scale(brake_val, 0, 255, 0, 100)
        speed = forward - reverse
        
        if abs(speed) < 3:
            speed = 0

        if abs(speed - last_speed) >= 3:
            drive_a.on(speed)
            drive_b.on(speed)
            last_speed = speed