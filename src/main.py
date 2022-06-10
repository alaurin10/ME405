'''!@file                   main.py
    @brief                  Main program for running pen plotter
    @details                Implements task architecture for controlling 
                            the motors and processing an HPGL file
    @author                 Ethan Nikcevich
    @author                 Andrew Laurin
    @author                 Rodrigo Gonzalez
    @date                   6/02/22
'''

from pyb import Pin, Timer, ADC, ExtInt, UART, SPI
import pyb
import micropython
from TMC4210_Class import *
import task_share
import cotask
import gc
import theta_generator
import math
import utime
from ulab import numpy as np
import motor
import encoder



'''
############################
Functions
############################
'''

# Function to interpolate coordinates between two points
def interpolate(STEP_SIZE, prev_coord, coord):

    # Initialize final arrays
    x_coords = []
    y_coords = []
    x_coords.append(prev_coord[0])
    y_coords.append(prev_coord[1])
    
    # Get start and end coordinates
    x = coord[0]
    y = coord[1]
    x_prev = prev_coord[0]
    y_prev = prev_coord[1]
    
    # Calculate distance between respective x and y coords
    x_dist = abs(x - x_prev)
    y_dist = abs(y - y_prev)

    # Return the max of the x dist and the y dist
    max_dist = max(x_dist, y_dist)

    # Interpolation points will be a function of the greatest distance
    steps = max_dist//STEP_SIZE
    
    # Interpolate if distance between coordinates is great enough
    if steps:
        try:
            # Generate linearly spaced coordinates between x coords
            x_vals = np.linspace(x_prev, x, steps)
            x_new = [int(x) for x in x_vals]

            # Add new x coords to list
            for x_ in x_new:
                x_coords.append(x_)

            # Generate linearly spaced coordinates between y coords
            y_vals = np.linspace(y_prev, y, steps)
            y_new = [int(x) for x in y_vals]

            # Add new x coords to list
            for y_ in y_new:
                y_coords.append(y_)

        except ValueError:
            return x_coords, y_coords
        

    return x_coords, y_coords


'''
################
Tasks
################
'''
# Task 1: Move motor 1: bottom linkage stepper motor
def motor1():
    while True:
        angle1 = theta1_share.get()
        steps1 = int(angle1*FULL_ROTATION/(2*math.pi))
        stepper1.set_target_position(int((steps1+52.5)/1.5))
        yield(0)

# Task 2: Move motor 2: top linkage stepper motor
def motor2():
    while True:
        angle2 = theta2_share.get()
        steps2 = int(angle2*FULL_ROTATION/(2*math.pi))
        stepper2.set_target_position(int(steps2/-1.5))
        yield(0)

# Task 3: Move motor 3: dc motor
def motor3():
    UP = 0
    DOWN = 1
    prev_command = UP
    while True:

        # Get command from share
        command = dc_share.get()

        # If command is same as previous, do nothing
        if command == prev_command:
            delay = utime.ticks_add(utime.ticks_ms(), 0)

        # If command is different and UP, set pen up by moving scissor lift down
        elif command == UP:
            dcmotor.set_duty(-80)
            delay = utime.ticks_add(utime.ticks_ms(), 1000)
            prev_command = UP

        # If command is different and DOWM, set pen dowm by moving scissor lift up
        elif command == DOWN:
            dcmotor.set_duty(80)
            delay = utime.ticks_add(utime.ticks_ms(), 1000)
            prev_command = DOWN

        # If command is none of the above, do nothing
        else:
            delay = utime.ticks_add(utime.ticks_ms(), 0)

        # Wait for timer to finish before stopping motor
        while utime.ticks_diff(delay, utime.ticks_ms()) > 0:
            pass    
        dcmotor.set_duty(0)        

        yield(0)
        


# Task 4: Generate theta values from HPGL file
def theta_gen():
    # Boolean variable to state whether the HPGL file is finished or not
    processing = True

    # Define empty string for processing the characters of the HPGL file
    buffer = ""

    # Variable for a non-blocking timer
    delay = utime.ticks_ms()
    
    while True:

        # Wait for button to start plotting
        active = False
        if start_btn.get():
            active = True
        
        while active:

            # Open the HPGL file
            with open('circle.hpgl', 'r') as file:
                
                # Loop to process the HPGL file
                while processing:
                    # Boolean variable that will allow one full instruction to be processed at a time
                    instruction_flag = True
                    
                    # Populate the buffer with the instruction
                    while instruction_flag:
                        
                        # If the next character is number or letter, continue appending the instruction
                        # If ; end the instruction. If empty, file is done being processed
                        char = file.read(1)
                        if char == "":
                            processing = False
                            instruction_flag = False
                        elif char == ";":
                            instruction_flag = False
                        else:
                            buffer += char
                                    
                    
                    # Read the command of each string
                    if buffer[0:2] == "IN":
                        # Turn on LEDs when program starts
                        PA4.value(True)
                        # Clear the command from the string
                        buffer = buffer.replace('IN', "")
                        print("Initializing")
                    
                    # Read the command of each string
                    elif buffer[0:2] == "PU":
                        # Clear the command from the string
                        buffer = buffer.replace('PU', "")
                        print("Setting Pen Up")

                        # Add command to share to be processed in motor3 task
                        dc_share.put(0)

                        # Set the delay to resume the task after 1500ms
                        delay = utime.ticks_add(utime.ticks_ms(), 1500)
                        
                    # Read the command of each string
                    elif buffer[0:2] == "PD":
                        # Clear the command from the string
                        buffer = buffer.replace('PD', "")
                        print("Setting Pen Down")

                        # Add command to share to be processed in motor3 task
                        dc_share.put(1)

                        # Start playing audio file on PD command
                        PA1.value(True)

                        # Set the delay to resume the FSM after 1500ms
                        delay = utime.ticks_add(utime.ticks_ms(), 1500)
                        
                    # Read the command of each string
                    elif buffer[0:2] == "SP":
                        # If command is SP, clear buffer and restart
                        buffer = ""
                        continue
                    
                    # Wait for non-blocking timer to complete
                    while utime.ticks_diff(delay, utime.ticks_ms()) > 0:
                        pass
                        yield(0)
                    # When timer is up, stop playing audio file
                    PA1.value(False)
                        
                    # If buffer is small enough, there is only one point so no need for interpolate
                    # Process HPGL code with a simpler method instead
                    if len(buffer) <= 8:
                        # Split points by the comma
                        coord = buffer[:].split(',')                    
                        # Run if there is still a pair of coordinates
                        if len(coord) >= 2:
                            x = 0
                            y = 1
                            for _ in range(len(coord)//2):
                                x_plot = (x / max_hpgl * draw_width) + draw_zero_x
                                y_plot = (y / max_hpgl * draw_height) + draw_zero_y
                                
                                # Solve for theta values with Newton-Raphson
                                thetas = NR.get_theta_values(x_plot, y_plot)
                                
                                # Add pair of theta values to share
                                theta1_share.put(thetas[0])
                                theta2_share.put(thetas[1])
                                x += 2
                                y += 2
                                
                                yield(0)                 
                            
                    # Initialize flags 
                    coord_flag = False
                    first_flag = True
                    last_flag = False

                    # Define interpolate step size
                    STEP_SIZE = 10
                    
                    coord = []
                    number = ""
                    # Iterate through each character in current buffer
                    for letter in buffer:
                        # If character is a comma, append current coord to list
                        if letter == ',':
                            coord.append(int(number))
                            number = ""                        
                            
                            # If there are two coordinates (xy pair), interpolate
                            if coord_flag:                                
                                
                                # If it is the first coordinate, define initial coord and continue
                                if first_flag:
                                    prev_coord = coord[:]
                                    first_flag = False
                                    coord_flag = False
                                    last_flag = True
                                    coord.clear()
                                    continue                                                     
                                
                                # Interpolate between current and previous coordinates
                                x_coords, y_coords = interpolate(STEP_SIZE, prev_coord, coord)
                                                            
                                # Iterate through interpolated list                                                        
                                for x, y in zip(x_coords, y_coords):      
                                    # Get xy values to plot                          
                                    x_plot = (x / max_hpgl * draw_width) + draw_zero_x
                                    y_plot = (y / max_hpgl * draw_height) + draw_zero_y

                                    # Solve for motor angles with Newton-Raphson method
                                    thetas = NR.get_theta_values(x_plot, y_plot)

                                    # Add angles to shares
                                    theta1_share.put(thetas[0])
                                    theta2_share.put(thetas[1])
        
                                    yield(0)

                                # Copy the current coord to new variable at end of every iteration
                                prev_coord = coord[:]                                             
                                # Clear current coord   
                                coord.clear()
                                coord_flag = False
                                continue

                            # Flag to build up two points for x and y before processing
                            coord_flag = True
                                            
                        # If character if a number, append to string                                        
                        else:
                            number += letter
                            
                    # Interpolate code to run for the last coordinate                        
                    if last_flag:
                        coord.append(int(number))
                        
                        x_coords, y_coords = interpolate(STEP_SIZE, prev_coord, coord)
                                                                
                        for x, y in zip(x_coords, y_coords):                                
                            x_plot = (x / max_hpgl * draw_width) + draw_zero_x
                            y_plot = (y / max_hpgl * draw_height) + draw_zero_y

                            thetas = NR.get_theta_values(x_plot, y_plot)
        
                            theta1_share.put(thetas[0])
                            theta2_share.put(thetas[1])

                            yield(0)

                        last_flag = False

                    
                    # Once instruction is done processing, reset buffer for next instruction
                    buffer = ""
                    instruction_flag = True
                    
                    yield(0)
                    
            # When HPGL file is finished, turn off LEDs
            PA4.value(False)
                
        yield(0)

# Task 5: button input to start plotting
def button():
    while True:
        # If button is pushed, put it in share
        if PA0.value():
            start_btn.put(1)
        yield(0)
        

if __name__ == '__main__':
    # Allocate memory for emergency exceptions
    micropython.alloc_emergency_exception_buf(100)

    # Initialize both stepper motor drivers
    stepper1 = TMC4210(V_MIN=50, V_MAX=300, A_MAX=1000, STEP_LENGTH=1.6, MOTOR=1)
    stepper2 = TMC4210(V_MIN=50, V_MAX=300, A_MAX=1000, STEP_LENGTH=1.6, MOTOR=2)
    FULL_ROTATION = 390

    # Define pins and driver for DC motor
    pinB4 = Pin(Pin.cpu.B4)
    pinB5 = Pin(Pin.cpu.B5)
    dcmotor = motor.Motor(3, pinB4, pinB5, 1, 2)
    motor_encoder = encoder.Encoder()
    motor_encoder.zero()

    # Create instance of Newton-Raphson
    NR = theta_generator.ThetaGenerator()
    
    # Define all other GPIO
    PA4 = Pin(Pin.cpu.A4, mode=Pin.OUT_PP, value=0)  # Configure Pin A4 as output for LEDs
    PA1 = Pin(Pin.cpu.A1, mode=Pin.OUT_PP)  # Configure Pin A4 as output for Speaker
    PA0 = Pin(Pin.cpu.A0, mode=Pin.IN, pull=Pin.PULL_NONE)  # Configure Pin A4 as input for button

    # Define all shares 
    start_btn = task_share.Share('f', thread_protect=False, name='Share 0')
    stop_btn = task_share.Share('f', thread_protect=False, name='Share 1')
    theta1_share = task_share.Share('f', thread_protect=False, name='Share 2')
    theta2_share = task_share.Share('f', thread_protect=False, name='Share 3')
    dc_share = task_share.Share('f', thread_protect=False, name='Share 4')

    start_btn.put(0)

    # Define all tasks
    motor1_task = cotask.Task(motor1, name='Task 1', priority=1, period=5, profile=True, trace=False)
    motor2_task = cotask.Task(motor2, name='Task 2', priority=1, period=5, profile=True, trace=False)
    motor3_task = cotask.Task(motor3, name='Task 3', priority=1, period=5, profile=True, trace=False)
    theta_task = cotask.Task(theta_gen, name='Task 4', priority=0, period=100, profile=True, trace=False)
    button_task = cotask.Task(button, name='Task 5', priority=1, period=5, profile=True, trace=False)

    # Append all tasks to cotask
    cotask.task_list.append(theta_task)
    cotask.task_list.append(motor1_task)
    cotask.task_list.append(motor2_task)
    cotask.task_list.append(motor3_task)
    cotask.task_list.append(button_task)
    
    gc.collect ()

    
    # Value to represent the width of the drawing in inches
    draw_width = 82 / 25.4                    
    # Value to represent the height of the drawing in inches
    draw_height = 80 / 25.4                

    # Location fo the x-axis relative to the center of the linkage in inches
    draw_zero_x = -6                
    # Location fo the y-axis relative to the center of the linkage in inches
    draw_zero_y = 4                 
    
    # Value for the largest value in the HPGL file used to scale the drawing
    max_hpgl = 2039

    # Run cotask schedule
    while True:
        cotask.task_list.pri_sched()
        

