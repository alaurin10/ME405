from pyb import Pin, Timer, ADC, ExtInt, UART, SPI
import pyb
import micropython
import time
import math

class TMC4210:

    def __init__(self, V_MIN, V_MAX, A_MAX, STEP_LENGTH):                    

        self.V_MIN = V_MIN
        self.V_MAX = V_MAX
        self.A_MAX = A_MAX
        self.STEP_LENGTH = STEP_LENGTH

        # TMC4210 constants
        self.CLK_FREQ = 20000000     # 20 MHz

        # SPI constants
        self.spi_bus = 2
        self.spi_BAUD = 1000000

        self.CS1 = Pin(Pin.cpu.C2, mode=Pin.OUT_PP, value=1)
        self.CS2 = Pin(Pin.cpu.C3, mode=Pin.OUT_PP, value=1)

        # Timer constants
        self.AUTO_RELOAD = 3
        self.COMPARE = 2
        self.tim_num = 4
        self.ch_num = 1
        self.clk_pin = Pin(Pin.cpu.B6, mode=Pin.OUT_PP)


        # Initialization functions
        self.enable()
        self.spi_init()
        self.timer_init()
        self.set_step_duration(STEP_LENGTH)
        self.set_pulseRamp_div(V_MAX, A_MAX)
        self.set_ramp_mode()
        self.set_movement_params(V_MIN, V_MAX, A_MAX)


    # Function to Enable the TMC4210
    def enable(self):
        self.EN1 = Pin(Pin.cpu.B0, mode=Pin.OUT_PP, value=0)
        self.EN2 = Pin(Pin.cpu.C0, mode=Pin.OUT_PP, value=0)

    def set_step_duration(self, step_length):
        step_duration = step_length  - 1

        en_sd = EMPTY
        en_sd[3] |= 1 << 5

        self.write_register(IF_CONF_W, en_sd)

        current_reg = self.read_register(GLOBAL_PARAMETERS_R)
        
        current_byte = current_reg[2]
        current_byte |= step_duration & 0x0F
        current_reg[2] = current_byte

        self.write_register(GLOBAL_PARAMETERS_W, current_reg)

    def enable_right_reference(self):
        current_reg = self.read_register(GLOBAL_PARAMETERS_R)
        
        current_byte = current_reg[1]
        current_byte |= 1 << 5
        current_reg[1] = current_byte
        
        self.write_register(GLOBAL_PARAMETERS_W, current_reg)

    def set_ramp_mode(self):
        ramp_mode = ~(0b11)
        current_reg = self.read_register(REFCONF_RM_R)
        
        current_byte = current_reg[3]
        current_byte &= ramp_mode
        current_reg[3] = current_byte
        
        self.write_register(REFCONF_RM_W, current_reg)

    def set_movement_params(self, v_min, v_max, a_max):
        
        v_min_val = EMPTY
        v_min_val[3] = v_min & 0xFF
        v_min_val[2] = (v_min & 0x700) >> 8
        
        v_max_val = EMPTY
        v_max_val[3] = v_max & 0xFF
        v_max_val[2] = (v_max & 0x700) >> 8
        
        a_max_val = EMPTY
        a_max_val[3] = a_max & 0xFF
        a_max_val[2] = (a_max & 0x700) >> 8
        
        self.write_register(V_MIN_W, v_min_val)
        self.write_register(A_MAX_W, a_max_val)

        self.set_max_speed(v_max_val)
        self.set_pmul_pdiv(a_max)

    def set_pulseRamp_div(self, v_max, a_max):
        arg = (self.CLK_FREQ * 2047) / (v_max * 2047 * 32)
        p_div = math.log(arg) / math.log(2)

        arg2 = (self.CLK_FREQ * self.CLK_FREQ * 2047) / (a_max * (2 ** (p_div + 29)))
        r_div = math.log(arg2) / math.log(2)
        
        current_byte = EMPTY
        current_byte[2] |= (int(r_div) & 0x0F)
        current_byte[2] |= (int(p_div) & 0x0F) << 4

        self.write_register(PDIV_RDIV_W, current_byte)
        self.p_div = p_div
        self.r_div = r_div
            
    def set_pmul_pdiv(self, accel):
        p = (accel) / (128 * 2 ** (self.r_div - self.p_div))
        p_reduced = p * 0.99

        for pdiv in range(14):
            pmul = p_reduced * 8 * 2**pdiv - 128
            if 0 <= pmul <= 127:
                pm = pmul + 128
                pd = pdiv
        P_MUL = pm
        P_DIV = pd

        current_byte = EMPTY
        current_byte[3] |= (int(P_DIV) & 0x0F)
        current_byte[2] |= (int(P_MUL) & 0x7F)
        current_byte[2] |= 1 << 7
    
        self.write_register(PMUL_PDIV_W, current_byte)

    def set_current_position(self, position):
        position_val = EMPTY
        position_val[3] |= position & 0xFF
        position_val[2] |= (position >> 8) & 0xFF
        position_val[1] |= (position >> 16) & 0xFF
        
        self.write_register(X_ACTUAL_W, position_val)

    def set_target_position(self, position):
        position_val = EMPTY
        position_val[3] |= position & 0xFF
        position_val[2] |= (position >> 8) & 0xFF
        position_val[1] |= (position >> 16) & 0xFF
        
        self.write_register(X_TARGET_W, position_val)

    def get_current_position(self):
        position = self.read_register(X_ACTUAL_R)
        return position

    def get_target_position(self):
        position = self.read_register(X_TARGET_R)
        return position

    def set_max_speed(self, speed):
        self.write_register(V_MAX_W, speed)

    def set_target_speed(self, speed):
        speed_val = EMPTY
        speed_val[3] = speed & 0xFF
        speed_val[2] = (speed & 0x700) >> 8
        self.set_max_speed(speed_val)
        
        speed_val = EMPTY
        speed_val[3] = speed & 0xFF
        speed_val[2] = (speed & 0xF00) >> 8
        
        self.write_register(V_TARGET_W, speed_val)

    def get_current_speed(self):
        speed = self.read_register(V_ACTUAL_R)
        return speed

    def get_current_accel(self):
        accel = self.read_register(A_ACTUAL_R)
        return accel

    def stop(self):
        self.set_max_speed(0)


    def spi_init(self):
        self.spi = SPI(self.spi_bus, mode=SPI.CONTROLLER, baudrate=self.spi_BAUD, polarity=1, phase=1, crc=None)

    def timer_init(self):
        # Create a timer running at 20 MHz
        tim = Timer(self.tim_num, period=self.AUTO_RELOAD, prescaler=0)
        self.clk = tim.channel(self.ch_num, pin=self.clk_pin , mode=Timer.PWM, pulse_width=self.COMPARE)

    def write_register(self, address, data):
        
        reg_val = EMPTY
        reg_val[0] = address[0]
        reg_val[1] = data[1]
        reg_val[2] = data[2]
        reg_val[3] = data[3]
        
        self.CS1.low()
        self.spi.send(reg_val)
        self.CS1.high()

    def read_register(self, address):
        buf = bytearray(4)
        self.CS1.low()
        self.spi.send_recv(address, buf, timeout=5000)
        self.CS1.high()
        return buf


EMPTY = bytearray([0,0,0,0])

# --------- Read Registers ----------

TYPE_VERSION = bytearray([0b01110011,0,0,0])

X_TARGET_R =   bytearray([0b00000001,0,0,0])   

X_ACTUAL_R =   bytearray([0b00000011,0,0,0])  

V_MIN_R =      bytearray([0b00000101,0,0,0])  

V_MAX_R =      bytearray([0b00000111,0,0,0])

V_TARGET_R =   bytearray([0b00001001,0,0,0])

V_ACTUAL_R =   bytearray([0b00001011,0,0,0])    

A_MAX_R =      bytearray([0b00001101,0,0,0])   

A_ACTUAL_R =   bytearray([0b00001111,0,0,0])

PMUL_PDIV_R =  bytearray([0b00010011,0,0,0])     

REFCONF_RM_R = bytearray([0b00010101,0,0,0])                          

PDIV_RDIV_R =  bytearray([0b00011001,0,0,0])     

GLOBAL_PARAMETERS_R = bytearray([0b01111111,0,0,0])                             


# --------- Write Registers ----------   
X_TARGET_W =   bytearray([0b00000000,0,0,0])   

X_ACTUAL_W =   bytearray([0b00000010,0,0,0])  

V_MIN_W =      bytearray([0b00000100,0,0,0])  

V_MAX_W =      bytearray([0b00000110,0,0,0])

V_TARGET_W =   bytearray([0b00001000,0,0,0])

A_MAX_W =      bytearray([0b00001100,0,0,0])   

PMUL_PDIV_W =  bytearray([0b00010010,0,0,0])     

REFCONF_RM_W = bytearray([0b00010100,0,0,0])                          

PDIV_RDIV_W =  bytearray([0b00011000,0,0,0])    

IF_CONF_W =    bytearray([0b01101000,0,0,0])      

GLOBAL_PARAMETERS_W = bytearray([0b01111110,0,0,0])

                                                                                                                                       

