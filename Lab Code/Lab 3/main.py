# from pyb import Pin, Timer, ADC, ExtInt, UART, SPI
# import pyb
import numpy as np
import micropython
from Convert2Theta import get_theta_values
import matplotlib.pyplot as plt
import math
import imageio

# commands = [x.split() for x in open('line.hpgl').read().split(';')]
# commands = [x.split() for x in open('curve.hpgl').read().split(';')]
commands = [x.split() for x in open('bigcircle.hpgl').read().split(';')]
     
command_list = ['PU', 'PD']
for i, command in enumerate(commands): 
    if not any(operator in command[0] for operator in command_list):
        commands.pop(i)

commands = commands[:-1]

for command in commands:
    for i, letter in enumerate(command[0]):
        try:
            int(letter)
        except ValueError:
            if letter == 'U':
                command.append('PU')
            elif letter == 'D':
                command.append('PD')                
            if letter == ',':
                continue
            command[0] = command[0].replace(letter, "")

coordinates = []
for command in commands:
    x_coords = []
    y_coords = []
    numbers = command[0].split(',')
    for idx, number in enumerate(numbers):
        try:
            if int(idx) % 2 == 0:
                x_coords.append(int(number))
            else:
                y_coords.append(int(number))
        except ValueError:
            pass
    
    coordinates.append([command[-1], x_coords, y_coords])


def draw_line(coordinates):

    def interpolate(STEP_SIZE):

        while True:

            coords = zip(x_coords, y_coords)

            for idx, (x, y) in enumerate(coords):
                
                if  idx == 0:
                    x_prev = x
                    y_prev = y
                    continue

                x_dist = abs(x - x_prev)
                y_dist = abs(y - y_prev)

                max_dist = max(x_dist, y_dist)
                steps = max_dist//STEP_SIZE

                if steps:
                    x_vals = np.linspace(x_prev, x, steps+10)
                    x_new = [int(x) for x in x_vals]

                    for x_idx, x_ in enumerate(x_new):
                        x_coords.insert(idx + x_idx, x_)

                    y_vals = np.linspace(y_prev, y, steps+10)
                    y_new = [int(x) for x in y_vals]

                    for y_idx, y_ in enumerate(y_new):
                        y_coords.insert(idx + y_idx, y_)

                    break
                x_prev = x
                y_prev = y

            break


    theta_values = []
    for command in coordinates:
        pen_mode = command[0]

        if pen_mode == 'PU':
            pass
            # Move pen up

        elif pen_mode == 'PD':
            pass
            # Move pen down

        x_coords = command[1]
        y_coords = command[2]

        if not x_coords and y_coords:
            continue

        interpolate(30)

        theta = get_theta_values(x_coords, y_coords)        

        theta_values.append(theta)
    print(theta_values)
    return theta_values
        


l1 = 4
l2 = 3
l3 = 6

def get_corner_points(theta):
    theta1 = theta[0]
    theta2 = theta[1]
    
    Ax = l1 * math.cos(theta1)
    Ay = l1 * math.sin(theta1)
    P1 = (Ax, Ay)
    
    Bx = l1 * math.cos(theta1) + l3 * math.cos(theta2 - math.pi)
    By = l1 * math.sin(theta1) + l3 * math.sin(theta2 - math.pi)
    P2 = (Bx, By)
    
    Cx = l2 * math.cos(theta2)
    Cy = l2 * math.sin(theta2)
    P3 = (Cx, Cy)
    
    Dx = l1 * math.cos(theta1) + l2 * math.cos(theta2)
    Dy = l1 * math.sin(theta1) + l2 * math.sin(theta2)
    P4 = (Dx, Dy)
    
    return P1, P2, P3, P4


def get_xy_coords(theta):
    theta1 = theta[0]
    theta2 = theta[1]
    
    x = l1 * math.cos(theta1) + l3 * math.cos(theta2 - math.pi)
    y = l1 * math.sin(theta1) + l3 * math.sin(theta2 - math.pi)
    
    return x, y


def main():
    
    def plot_frame():
        plt.plot([0, P1[0]], [0, P1[1]], 'b')
        plt.plot([P1[0], P2[0]], [P1[1], P2[1]], 'b')
        plt.plot([0, P3[0]], [0, P3[1]], 'b')
        plt.plot([P3[0], P4[0]], [P3[1], P4[1]], 'b')
        plt.plot([P4[0], P1[0]], [P4[1], P1[1]], 'b')
        
    def plot_coords():
        # plt.figure()
        plt.plot(x_coords, y_coords, 'g')   
        # plt.show()     
        
    filenames = []
        
    theta_array = draw_line(coordinates)

    theta_values = theta_array[2]
    

    for i in range(len(theta_values)):
        theta = theta_values[i]
        P1, P2, P3, P4 = get_corner_points(theta)
        
        x_coords = []
        y_coords = []
        for j in range(i):
            x, y = get_xy_coords(theta_values[j])
            x_coords.append(x)
            y_coords.append(y)
        
    # plot_coords()

        plot_frame()
        plot_coords()
        plt.xlim(-3, 10)
        plt.ylim(-10, 10)
        filename = f'{i}.png'
        filenames.append(filename)
        
        plt.savefig(filename)
        plt.close()
        
    # Build gif
    with imageio.get_writer('circle.gif', mode='I') as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)  
   
                  
    
    
if __name__ == '__main__':
    main()



