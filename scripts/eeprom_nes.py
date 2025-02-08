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
    'JS1': 0,
    'JS2': 1,
    'JS3': 2,
    'JS4': 3,
    'JS5': 4,
    'JS6': 5,
    'JS7': 6,
    'JS8': 7,
}

KBIEN = (1 << 12)

def main():
    # specify a key-mapping between joystick input and keyboard presses
    mappings = [
        # MAPPING 01
        {'JS1': 'A',
         'JS2': 'B',
         'JS3': 'C',
         'JS4': 'D',
         'JS5': 'E',
         'JS6': 'F',
         'JS7': 'G',
         'JS8': 'H'},
        # MAPPING 02
        {'JS1': 'A',
         'JS2': 'B',
         'JS3': 'C',
         'JS4': 'D',
         'JS5': 'E',
         'JS6': 'F',
         'JS7': 'G',
         'JS8': 'H'},
        # MAPPING 03
        {'JS1': 'A',
         'JS2': 'B',
         'JS3': 'C',
         'JS4': 'D',
         'JS5': 'E',
         'JS6': 'F',
         'JS7': 'G',
         'JS8': 'H'},
        # MAPPING 04
        {'JS1': 'A',
         'JS2': 'B',
         'JS3': 'C',
         'JS4': 'D',
         'JS5': 'E',
         'JS6': 'F',
         'JS7': 'G',
         'JS8': 'H'},
    ]
        
    # build eeprom data
    data = bytearray()
    for mapping in mappings:
        print_mapping(mapping)
        data.extend(build_mapping_rom(mapping))
    
    plt.figure(dpi=144)
    plt.imshow(np.array(data[0:8*1024]).reshape((256,-1)), origin='lower')
    
    with open('joystick_eeprom.bin', 'wb') as f:
        f.write(bytearray(data))
    
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
        pin = wiring[k]     # grab input EEPROM address pin (A0-A7)
        row = lt[v][0]      # grab keyboard row (A8-A11)
        col = lt[v][1]      # grab keyboard col (D0-D7)    
        t = lt[v][2]
        
        print('%i: %12s -> (%i,%i,%s)' % (pin, k, row, col, t))
    print()

def build_mapping_rom(mapping):
    """
    Build a mapping ROM based on a mapping table (dictionary)
    """
    lt = build_reverse_lookup_table()
    
    data = np.ones((8 * 1024), dtype=np.uint8) * 0xFF
    for i in range(16):             # loop over rows (A8-A11)
        for j in range(256):        # loop over joystick input (A0 - A7)
            val = np.uint8(0xFF)    # by default, no key press
            
            for k,v in mapping.items():
                pin = wiring[k]     # grab input EEPROM address pin (A0-A7)
                row = lt[v][0]      # grab keyboard row (A8-A11)
                col = lt[v][1]      # grab keyboard col (D0-D7)
                
                # joystick pins are active-low and rows are active-high
                if i == row and (j & (1 << pin) == 0):
                    val &= ~(1 << col)   # mask the data pin (cols are active low)
            
            data[(i << 8) | j] = val
    
    # build "row-0" response
    for j in range(256):
        val = np.uint8(0xFF)    # by default, no key press
        for k,v in mapping.items():
            pin = wiring[k]     # grab input EEPROM address pin (A0-A7)
            row = lt[v][0]      # grab keyboard row (A8-A11)
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