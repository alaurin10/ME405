import matplotlib
import serial
import os


UART_PORT = 'COM10'

time_array = []
voltage_array = []


def main():
    os.system("cls")
    while True:
        with serial.Serial(UART_PORT, 115200) as ser:
            if not ser.isOpen():
                ser.open()
            line = ser.readline()
            line = str(line, 'utf-8')
            line = line.strip('\r\n')
            line = line.split(',')
            result = list(map(int, line))            
            
            print(result)




if __name__ == '__main__':
    main()
