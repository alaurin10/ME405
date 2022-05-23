import numpy as np
import math


l1 = 4 * 1016
l2 = 3 * 1016
l3 = 6 * 1016


# Function representing g
def g(x, theta):
    
    x_pos = x[0]
    y_pos = x[1]
    
    theta1 = theta[0]
    theta2 = theta[1]
    
    f_x = l1 * math.cos(theta1) + l3 * math.cos(theta2 - math.pi)
    f_y = l1 * math.sin(theta1) + l3 * math.sin(theta2 - math.pi)
    
    g1 = x_pos - f_x
    g2 = y_pos - f_y
    
    return np.asarray([g1, g2])


# Function representing derivative of g with respect to theta
def dg_dtheta(theta):
    theta1 = theta[0]
    theta2 = theta[1]
    
    dx_dtheta1 = -1 * l1 * math.sin(theta1)
    dx_dtheta2 = -1 * l3 * math.sin(theta2 - math.pi)
    dy_dtheta1 = l1 * math.cos(theta1)
    dy_dtheta2 = l3 * math.cos(theta2 - math.pi)
    
    return -1 * np.asarray([[dx_dtheta1, dx_dtheta2], [dy_dtheta1, dy_dtheta2]])


def solve(arg1, arg2):
    return np.matmul(np.linalg.inv(arg1), arg2)


def NewtonRaphson(fcn, jacobian, guess, thresh):
    
    theta = guess
    error = np.linalg.norm(fcn(theta))
    
    while error > thresh:
        theta -= solve(jacobian(theta), fcn(theta))
        error = np.linalg.norm(fcn(theta))
        
    return theta


def get_theta_values(x_coords, y_coords):

    theta_array = []

    coords = zip(x_coords, y_coords)
    
    for i, (x, y) in enumerate(coords):
        x = x+l1
        y = y-l3
        x_des = np.asarray([x, y])
        theta_guess = np.asarray([0, math.pi/2])
        
        theta = NewtonRaphson(lambda theta: g(x_des, theta), dg_dtheta, theta_guess, 1e-6)
        
        theta_array.append(theta)
    
    theta_values = np.asarray(theta_array)
    
    return theta_values
