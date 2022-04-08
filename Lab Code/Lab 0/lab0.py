from pyb import Pin, Timer, ADC, ExtInt, UART
import pyb
import micropython
import array


# Top level parameters
SAMPLES = 20

# Allocate memory for emergency exceptions
micropython.alloc_emergency_exception_buf(100)      


# Configue UART
pyb.repl_uart(None)         # Disable Thonny REPL
uart = UART(2, 115200)      # UART 2 with 115200 baudrate
uart.init(115200, bits=8, parity=None, stop=1)  # 115200 baud, 8 data bits, no parity, 1 stop bit


# Pin Declarations
PA4 = Pin(Pin.cpu.A4, mode=Pin.OUT_PP)  # Configure Pin A4 as digital output

PA6 = Pin.cpu.A6       # Define Pin A6 for ADC input
adc = ADC(PA6)         # Create ADC on Pin A6 (PC0)
buf = bytearray(100)   # creat a buffer to store the samples


# Interrupt handler for button push
button_push = 0
def btn_callback(line):
    global button_push
    button_push = 1         # Set global variable to 1
    
button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, btn_callback)


# Interrupt handler for ADC sample and convert
def adc_interrupt(tim):
    global row_idx
    reading = adc.read_timed(buf, tim)      # sample 100 values, taking 1s
    time_array[row_idx] = row_idx           # Add current index to list
    adc_array[row_idx] = reading            # Add ADC reading to list
    row_idx += 1

    if row_idx == len(time_array):          # Disable adc interrupt when finished
        tim.callback(None)

tim = Timer(6, freq=1000)     # Create a timer running at 1 kHz


# Create empty lists for time and adc values
row_idx = 0
time_array = array.array('H', SAMPLES*[0])
adc_array = array.array('H', time_array)


def main():
    global row_idx
    global button_push
    
    # Main loop
    while True:
        PA4.low()   # Default output is LOW

        # Button interrupt handler triggers ADC start
        if button_push:
            uart.writechar(42)  
            button_push = 0     # Clear button press variable
            PA4.high()          # Output HIGH from pin
            tim.callback(adc_interrupt)     # Enable ADC interrupt handler to start data collection
            
            # Loop until ADC array is filled
            while row_idx < len(time_array):                
                pass
            

            PA4.low()       # Clear output back to LOW
            row_idx = 0     # Reset array index
            
            # Print results of data collection
            for i in range(len(time_array)):
                print(str(time_array[i])+',', adc_array[i])
                
            
    
    
if __name__ == '__main__':
    main()
