from pyb import Pin, Timer, ADC, ExtInt, UART
import pyb
import micropython
import array
import time
import task_share
import cotask
import gc



def comms():
    BUTTON = 0
    DATA = 1
    SERIAL = 2
    
    state = BUTTON
    while True:

        if state == BUTTON:
            PC1.low()   # Default output is LOW
            # Button interrupt handler triggers ADC start
            if share_btn.get():
                counter = 0
                share_counter.put(counter)
                share_btn.put(0)
                
                state = DATA
                
            
        elif state == DATA:
            PC1.high()          # Output HIGH from pin
            tim.callback(adc_interrupt)     # Enable ADC interrupt handler to start data collection
            
            # Loop until ADC array is filled
            while not queue_adc.full():
                yield(0)
            
            state = SERIAL
        
        elif state == SERIAL:
            # Print results of data collection
            while queue_adc.any():
                time = queue_time.get()
                values = queue_adc.get()
                print("{:}, {:}".format(time, values, end=''))
                ser.write(str(time)+','+str(values)+'\r\n')
            state = BUTTON

    

# Interrupt handler for button push
def btn_callback(line):
    share_btn.put(1)
    


# Interrupt handler for ADC sample and convert
def adc_interrupt(tim):
    reading = adc.read()
    
    counter = share_counter.get()
    
    queue_time.put(counter)
    queue_adc.put(reading)
    
    counter += 1
    share_counter.put(counter)

    if queue_adc.full():          # Disable adc interrupt when finished
        tim.callback(None)

                        
            
    
    
if __name__ == '__main__':
    
    # Top level parameters
    SAMPLES = 2001

    # Allocate memory for emergency exceptions
    micropython.alloc_emergency_exception_buf(100)      


    # Configue UART
    ser = UART(2, 115200)      # UART 2 with 115200 baudrate
    ser.init(115200, bits=8, parity=None, stop=1)  # 115200 baud, 8 data bits, no parity, 1 stop bit
    
    # Create a timer running at 1 kHz
    tim = Timer(6, freq=1000)
    
    # Create an external interrupt for the onboard button`
    button_int = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, btn_callback)


    # Pin Declarations
    PC1 = Pin(Pin.cpu.C1, mode=Pin.OUT_PP)  # Configure Pin A4 as digital output

    PC0 = Pin.cpu.C0       # Define Pin A5 for ADC input
    adc = ADC(PC0)         # Create ADC on Pin A6 (PC0)
    buf = bytearray(100)   # creat a buffer to store the samples    
    
    # Define tasks, shares, and queues
    share_btn = task_share.Share('B', thread_protect=False, name='Share 0')
    share_counter = task_share.Share('H', thread_protect=False, name='Share 1')
    queue_time = task_share.Queue('L', SAMPLES, thread_protect=False, overwrite=False, name='Queue 0')
    queue_adc = task_share.Queue('L', SAMPLES, thread_protect=False, overwrite=False, name='Queue 1')

    task_comms = cotask.Task(comms, name='Task 1', priority=1, period=5, profile=True, trace=False)

    cotask.task_list.append(task_comms)

    gc.collect()
    
    while True:
        cotask.task_list.pri_sched()

    

    


