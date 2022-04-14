import matplotlib.pyplot as plt
import serial
import numpy as np
import os


UART_PORT = 'COM10'     # Serial port used for UART to PC
SAMPLES = 2000          # Number of ADC samples


# Function that converts ADC bits to a voltage value
def convert_to_voltage(adc_value):
    VLSB = 3.3/4096             # Voltage of Least Signifhicant Bit
    voltage = VLSB * adc_value  # VLSB * Number of bits
    return voltage


# Function to convert ms to s
def convert_to_seconds(time_value):
    return time_value / 1000    # Millisecond to seconds


# Function to convert linear voltage values to log-scale voltage values
def convert_to_log(voltage_array):
    log_array = []
    max_val = max(voltage_array)    # FInd max value of array as Vin
    for value in voltage_array:        
        log_array.append(np.log((max_val - value)/max_val))     # Log value equation
    return log_array


# Main function
def main():
    os.system("cls")    # Clear console
    np.seterr(divide = 'ignore') 
    raw_data = []       # Define lists
    time_vals = []
    voltage_vals = []
    

    # Open serial port and collect total number of ADC samples
    with serial.Serial(UART_PORT, 115200) as ser:
        for i in range(SAMPLES):
                    
            line = ser.readline()       # Read data until line termination: '\n'
            raw_data.append(line)       # Append data to list


    # Convert and separate raw data into time and ADC values
    for line in raw_data:
        time, adc = map(int, line.decode().strip('\r\n').split(','))    # Decode data
        time_vals.append(convert_to_seconds(time))      # Convert and append time values in seconds to list 
        voltage_vals.append(convert_to_voltage(adc))    # Convert and append adc values in volts to list
        

    # Plot 1: Linear step response
    plt.figure(1)
    plt.plot(time_vals, voltage_vals)
    plt.xticks(np.arange(min(time_vals), max(time_vals)+2, 0.25))   
    plt.xlim(0, 2)
    plt.title('Step Response of RC Circuit', fontsize=15)
    plt.xlabel("Time [sec]")
    plt.ylabel("Voltage [V]")
    plt.grid()
    
    # Calculate log-scale values
    log_vals = convert_to_log(voltage_vals)     # Convert linear voltage into log-scale voltage

    # Find slope of line
    slope, intercept = np.polyfit(log_vals[:int(SAMPLES/2)], time_vals[:int(SAMPLES/2)], 1)
    

    # Plot 2: log-scale step response
    plt.figure(2)
    plt.plot(time_vals, log_vals)
    plt.annotate('Slope = '+str(round(slope, 4)), xy=(0.75,-1.5), fontsize=15)
    plt.title('Log Scale Step Response of RC Circuit', fontsize=15)
    plt.xlabel("Time [sec]")
    plt.ylabel("Log Values [-]")
    plt.grid()
    plt.show()
    

# Run main function
if __name__ == '__main__':
    main()
