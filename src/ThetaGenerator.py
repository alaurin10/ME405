'''!@file                   ThetaGenerator.py
    @brief                  Class for Inverse Kinematics
    @details                Class to compute theta values using
                            the Newton-Raphson method
    @author                 Ethan Nikcevich
    @author                 Andrew Laurin
    @author                 Rodrigo Ronzalez
    @date                   6/02/22
'''

import math
from ulab import numpy as np

class ThetaGenerator():
    
    def __init__(self):

        # Length of Linkage 1 in inches
        self.l1 = 4
        # Length of Linkage 2 in inches
        self.l2 = 3
        # Length of Linkage 3 in inches
        self.l3 = 6

    # Function representing g
    def g(self, x, theta):
        
        x_pos = x[0]
        y_pos = x[1]
        
        theta1 = theta[0]
        theta2 = theta[1]
        
        f_x = self.l1 * math.cos(theta1) + self.l3 * math.cos(theta2 + math.pi)
        f_y = self.l1 * math.sin(theta1) + self.l3 * math.sin(theta2 + math.pi)
        
        g1 = x_pos - f_x
        g2 = y_pos - f_y
        
        return np.asarray([g1, g2])

    # Function representing derivative of g with respect to theta
    def dg_dtheta(self, theta):
        theta1 = theta[0]
        theta2 = theta[1]
        
        dx_dtheta1 = -1 * self.l1 * math.sin(theta1)
        dx_dtheta2 = -1 * self.l3 * math.sin(theta2 + math.pi)
        dy_dtheta1 = self.l1 * math.cos(theta1)
        dy_dtheta2 = self.l3 * math.cos(theta2 + math.pi)
        
        return -1 * np.asarray([[dx_dtheta1, dx_dtheta2], [dy_dtheta1, dy_dtheta2]])

    # Function to multiply matricies 
    def solve(self, arg1, arg2):
        return np.dot(np.linalg.inv(arg1), arg2)     

    # Function to implement Newton-Raphson root finding method
    def NewtonRaphson(self, fcn, jacobian, guess, thresh):
        
        theta = guess
        error = np.linalg.norm(fcn(theta))
        
        while error > thresh:
            theta -= self.solve(jacobian(theta), fcn(theta))
            error = np.linalg.norm(fcn(theta))
            
        return theta           

    # Main function to compute and return theta values from xy-coords
    def get_theta_values(self, x_coord, y_coord):
        
        x = x_coord
        y = y_coord
        x_des = np.asarray([x, y])
        theta_guess = np.asarray([math.pi/2, 0])
        
        theta = self.NewtonRaphson(lambda theta: self.g(x_des, theta), self.dg_dtheta, theta_guess, 1)
            
        return theta[0], theta[1]        

    


