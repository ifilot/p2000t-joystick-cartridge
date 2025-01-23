# P2000T Joystick Cartridge for SLOT2

Connect Atari 2600 style joysticks to your P2000T

## PCB



## Working

The P2000T uses a matrix keyboard where each key lies at the intersection
of a row and a column. The rows are tied to the address pins and the columns
to the data pins. There are 10 rows and 8 columns. The P2000T polls the keyboard
in a two-step procedure. First, the P2000T writes a '1' at the BIT6 position
to I/O port `0x10`. This will tie all rows to GND. Next, the P2000T reads
from I/O port `0x00`. If at least one key is pressed, the resulting read will
be be unequal to `0xFF`. If this is the case, the P2000T is going to perform
another step wherein all rows are sequentially pulled down by reading from
`0x00 - 0x0A`. A zero-bit received for any of these reads operation would
correspond to a key being read, which is associated to a given key stroke.