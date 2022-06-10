'''!@file                   motor.py
    @brief                  Establishes pins for the motor and sets duty for the motor
    @details                Defines the motor class for setting motor speeds
    @author                 Ethan Nikcevich
    @author                 Johnathan Dietz
    @date                   3/17/22
'''
import pyb

class Motor:
    '''!@brief    A motor class for one channel of the DRV8847.
        @details  Objects of this class can be used to apply PWM to a given
                  DC motor.
    '''
    def __init__ (self, tim, pin1, pin2, ch1, ch2):
        '''!@brief       Initializes and returns an object associated with a DC Motor.
            @details     The motor needs a timer, 2 pins, and 2 channels to be created
            @param tim   Decides which timer will be used
            @param pin1  First pin used by motor
            @param pin2  Second pin used by motor
            @param ch1   First channel used by motor
            @param ch2   Second channel used by motor
        '''
        ## @brief   A timer used by the motor
        #  @details The timer is configured according to the input value (3), and has a frequency of 20000 Hz
        self.tim = pyb.Timer(tim, freq = 20_000)
        ## @brief   First pin used by the motor
        #  @details The attribute is assigned to the passed in pin1 value
        self.pin1 = pin1
        ## @brief   Second pin used by the motor
        #  @details The attribute is assigned to the passed in pin2 value
        self.pin2 = pin2
        ## @brief   First channel used by motor
        #  @details A motor needs two channels. The first channel is configured according to the passed in pin1 and ch1 values.
        self.tim_ch1 = self.tim.channel(ch1, pyb.Timer.PWM_INVERTED, pin=self.pin1)
        ## @brief   Second channel used by motor
        #  @details A motor needs two channels. The second channel is configured according to the passed in pin2 and ch2 values.
        self.tim_ch2 = self.tim.channel(ch2, pyb.Timer.PWM_INVERTED, pin=self.pin2)
    
    def set_duty (self, duty):        
        '''!@brief      Set the PWM duty cycle for the motor channel.
            @details    This method sets the duty cycle to be sent
                        to the motor to the given level. Positive values
                        cause effort in one direction, negative values
                        in the opposite direction.
            @param duty A signed number holding the duty
                        cycle of the PWM signal sent to the motor
        '''
        if duty > 0:
            self.tim_ch1.pulse_width_percent(0)
            self.tim_ch2.pulse_width_percent(duty)
        elif duty < 0:
            self.tim_ch1.pulse_width_percent(-duty)
            self.tim_ch2.pulse_width_percent(0)
        else:
            self.tim_ch1.pulse_width_percent(0)
            self.tim_ch2.pulse_width_percent(0)
