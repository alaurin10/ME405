import numpy as np
import math

l1 = 1
l2 = 1
l3 = 1

# Function representing g
def g(x, theta):
    x_pos = x[0]
    y_pos = x[1]
    
    theta1 = theta[0]
    theta2 = theta[1]
    
    f_x = l1 * math.cos(theta1) + l3 * math.cos(theta2 - 180)
    f_y = l1 * math.sin(theta1) + l3 * math.sin(theta2 - 180)
    
    g1 = x_pos - f_x
    g2 = y_pos - f_y
    
    return [g1, g2]
    
    

# Function representing derivative of g with respect to theta
def dg_dtheta(theta):
    theta1 = theta[0]
    theta2 = theta[1]
    
    dx_dtheta1 = -1 * l1 * math.sin(theta1)
    dx_dtheta2 = -1 * l3 * math.sin(theta2 - 180)
    dy_dtheta1 = l1 * math.cos(theta1)
    dy_dtheta2 = l3 * math.cos(theta2 - 180)
    
    return -1 * np.asarray([[dx_dtheta1, dx_dtheta2], [dy_dtheta1, dy_dtheta2]])

def NewtonRaphson(fcn, jacobian, guess, thresh):
    while thresh > 
        th_new = th_old - np.linalg.inv(jacobian) * fcn

