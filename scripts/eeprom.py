# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# P2000T keyboard matrix
#------------------------------------------------------------------------------
# The P2000T sequentially pulls the rows low by reading from I/O port 0x0X. The
# lower nibble is used to interface with the rows (0-9). For each row, the
# data line is read. When a key is pressed down, it creates a low-active
# signal on its corresponding data pin.

import numpy as np
import matplotlib.pyplot as plt

# mapping between keys and keyboard rows and columns
keyboard_matrix = [
    ['LEFT', '6', 'UP', 'Q', '3', '5', '7', '4'],
    ['TAB', 'H', 'Z', 'S', 'D', 'G', 'J', 'F'],
    ['NUMDOT', 'SPACE', 'NUM00', 'NUM0', '#', 'DOWN', ',', 'RIGHT'],
    ['SHLOCK', 'N', '<', 'X', 'C', 'B', 'M', 'V'],
    ['CODE', 'Y', 'A', 'W', 'E', 'T', 'U', 'R'],
    ['CLRLN', '9', 'NUM+', 'NUM-', 'BACKSPACE', '0', '1', '-'],
    ['NUM9', 'O', 'NUM8', 'NUM7', 'ENTER', 'P', '8', '@'],
    ['NUM3', '.', 'NUM2', 'NUM1', '->', '/', 'K', '2'],
    ['NUM6', 'L', 'NUM5', 'NUM4', '1/4', ';', 'I', ':'],
    ['LSHIFT', '__', '__', '__', '__', '__', '__', 'RSHIFT']
]

# mapping between joystick pins and EEPROM address bus
wiring = {
    'P1_UP': 0,
    'P1_DOWN': 1,
    'P1_LEFT': 2,
    'P1_RIGHT': 3,
    'P1_FIRE': 4,
    'P2_UP': 5,
    'P2_DOWN': 6,
    'P2_LEFT': 7,
    'P2_RIGHT': 8,
    'P2_FIRE': 9,
}

KBIEN = (1 << 14)

def main():
    # specify a key-mapping between joystick input and keyboard presses
    mapping = {
        'P1_UP': 'UP',
        'P1_DOWN': 'DOWN',
        'P1_LEFT': 'LEFT',
        'P1_RIGHT': 'RIGHT',
        'P1_FIRE': 'SPACE',
        'P2_UP': 'NUM8',
        'P2_DOWN': 'NUM2',
        'P2_LEFT': 'NUM4',
        'P2_RIGHT': 'NUM6',
        'P2_FIRE': 'NUM0',
    }
    
    # show key associations
    print_mapping(mapping)
    
    # build eeprom data
    eeprom_data = build_mapping_rom(mapping)
    
    with open('joystick_eeprom.bin', 'wb') as f:
        f.write(bytearray(eeprom_data))
    
    test_mapping(eeprom_data, 'P1_UP')
    test_mapping(eeprom_data, 'P1_DOWN')
    test_mapping(eeprom_data, 'P1_LEFT')
    test_mapping(eeprom_data, 'P1_RIGHT')
    test_mapping(eeprom_data, 'P1_FIRE')
    
    # visualize the eeprom_data
    data =np.array([bin(v).count('1') for v in eeprom_data]).reshape(256,128)
    plt.figure(dpi=144)
    plt.imshow(data, origin='lower', cmap='OrRd_r')
    plt.yticks(np.arange(0, 128, 8) + 4, ['ROW%i' % i for i in range(16)])
    plt.hlines(np.arange(0, 128, 8)-0.5, 0, 128, linestyle='--', color='black', linewidth=0.5)
    plt.xticks([])
    plt.xlim(0,128)
    plt.ylim(0,128+128//16-0.5)
    plt.title(r'Joystick $\rightarrow$ Keyboard mapping data')
    
def test_mapping(eeprom_data, pinname):
    """
    Test whether the mapping provides the expected result
    """
    pinid = wiring[pinname]
    for i in range(0,8): # loop over address lines
        addr = np.uint(i << 10) | (0x3FF ^ np.uint16(1 << pinid))
        val = eeprom_data[addr]
        if val != 0xFF:
            print(i, 7-format(val, '08b').find('0'), format(val, '08b'), format(addr, '016b'))
    
def print_mapping(mapping):
    """
    Print to terminal how the joystick keys are mapped to the keyboard matrix
    """
    lt = build_reverse_lookup_table()
    for k,v in mapping.items():
        pin = wiring[k]     # grab input EEPROM address pin (A0-A9)
        row = lt[v][0]      # grab keyboard row (A10-A13)
        col = lt[v][1]      # grab keyboard col (D0-D7)    
        t = lt[v][2]
        
        print('%i: %12s -> (%i,%i,%s)' % (pin, k, row, col, t))
    print()

def build_mapping_rom(mapping):
    """
    Build a mapping ROM based on a mapping table (dictionary)
    """
    lt = build_reverse_lookup_table()
    
    data = np.ones((32 * 1024), dtype=np.uint8) * 0xFF
    for i in range(16):             # loop over address lower address nibble (A10-A13)
        for j in range(1024):       # loop over joystick input (A0 - A9)
            val = np.uint8(0xFF)    # by default, no key press
            
            for k,v in mapping.items():
                pin = wiring[k]     # grab input EEPROM address pin (A0-A9)
                row = lt[v][0]      # grab keyboard row (A10-A13)
                col = lt[v][1]      # grab keyboard col (D0-D7)
                
                # joystick pins are active-low and rows are active-high
                if i == row and (j & (1 << pin) == 0):
                    val &= ~(1 << col)   # mask the data pin (cols are active low)
            
            data[(i << 10) | j] = val
    
    # build "row-0" response
    for j in range(1024):
        val = np.uint8(0xFF)    # by default, no key press
        for k,v in mapping.items():
            pin = wiring[k]     # grab input EEPROM address pin (A0-A9)
            row = lt[v][0]      # grab keyboard row (A10-A13)
            col = lt[v][1]      # grab keyboard col (D0-D7)
            
            if (j & (1 << pin) == 0):
                val &= ~(1 << col)   # mask the data pin (cols are active low)

        data[j | KBIEN] = val
    
    return data

def build_reverse_lookup_table():
    """
    Construct a reverse look-up table based on the keyboard matrix
    """
    lookup_table = {}
    for i,row in enumerate(keyboard_matrix):
        for j,el in enumerate(row):
            lookup_table[el] = (i,j,el)
            
    return lookup_table

if __name__ == '__main__':
    main()