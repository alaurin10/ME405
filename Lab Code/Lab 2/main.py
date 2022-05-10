from pyb import Pin, Timer, ADC, ExtInt, UART, SPI
import pyb
import micropython
from TMC4210_Class import *

# Allocate memory for emergency exceptions
micropython.alloc_emergency_exception_buf(100)

stepper = TMC4210(10, 80, 5, 5)
def main():
    stepper.set_target_position(100)
#     stepper.set_target_speed(5)
    
if __name__ == '__main__':
    main()
    
