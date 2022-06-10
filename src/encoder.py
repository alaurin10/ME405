'''!@file                   encoder.py
    @brief                  A driver for reading from Quadrature Encoders
    @details                Creates a class called Encoder that establishes
                            functions used for the encoder
    @author                 Ethan Nikcevich
    @author                 Johnathan Dietz
    @date                   2/13/22
'''

import pyb
import utime

class Encoder:
    '''!@brief              Interface with quadrature encoders
        @details            Creates a list of functions to be used
    '''
    
    def __init__(self):
        '''!@brief          Sets variables for the file and calls the hardware 
            @param timNum    
            @param period 
            @param pin1
            @param pin2
        '''
        self.period = 65535
         ## Sets the appropriate timer for encoder 2
        self.timer = pyb.Timer(8, prescaler = 0, period = self.period)
        
        ## Sets the appropriate pin 1 for encoder 2
        self.Pin1 = pyb.Pin(pyb.Pin.cpu.C6)
        ## Sets the appropriate pin 2 for encoder 2
        self.Pin2 = pyb.Pin(pyb.Pin.cpu.C7)
        
        
        self.tim = pyb.Timer (8, prescaler = 0 , period = self.period)
        self.t4ch1 = self.tim.channel(1 , pyb.Timer.ENC_AB , pin = self.Pin1)
        self.t4ch2 = self.tim.channel(2 , pyb.Timer.ENC_AB , pin = self.Pin2)
        self.prev = 0
        self.cur = 0
        self.delta = 0
        self.position = 0
        self.prev_time = 0
        self.time_delta = 0
        
    def zero(self): 
        '''!@brief Zeros the encoder value
            @param zero
        ''' 
        self.position = 0
        
    def update(self):
        '''!@brief  Updates the encoder postition
        ''' 
        # time since last update
        self.time_delta = utime.ticks_diff(utime.ticks_us(), self.prev_time)
        self.prev_time = utime.ticks_us()
        
        # calculate delta
        self.prev = self.cur
        self.cur = self.tim.counter()
        self.delta = self.cur - self.prev
        if self.delta >= self.period/2:
            self.delta -= self.period
        elif self.delta <= -self.period/2:
            self.delta += self.period
            
        # convert ticks to radians
        self.radians = self.delta *(2*3.14159)/4000
        
        # convert radians to rad/s
        if self.time_delta > 0:
            self.omega = self.radians/(self.time_delta/1e6)
        else:
            self.omega = 0.0
        
        # update the position
        self.position += self.radians
        
        return self.position
        
    def get_position(self):
        '''!@brief  Returns encoder position
            @return Encoder position
        ''' 
        return self.position
    
    def get_delta(self):
        '''!@brief  Returns encoder delta
            @return Encoder delta
        ''' 
        return self.delta
    
    def get_velocity(self):
        '''!@brief  Reports encoder angular velocity (rad/s)
            @return Encoder velocity
        ''' 
        return self.omega

