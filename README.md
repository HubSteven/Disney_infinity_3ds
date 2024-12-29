# Disney infinity 3DS
Emulation of the IR communication of the Disney Infinity 3DS base.
# Usage
To use the script enable the env modules and run the script:

<code>python3 disney_emu.py <serial port ex. /dev/ttyUSB0> <.bin file of character on roundpad> <.bin file  on hexagon pad></code>
# Examples
<code>python3 disney_emu.py /dev/ttyUSB0 Mater.bin</code>

<code>python3 disney_emu.py /dev/ttyUSB0 None Cars_Play_Set.bin</code>

To use round powerdiscs:
<code>python3 disney_emu.py /dev/ttyUSB0 Power_disc.bin</code>
Then terminate the script with Ctrl-c once it's loaded on the 3DS.
Then run the script again for another power disc.
After terminating the script again run the script for a third time with the character binary.


https://github.com/user-attachments/assets/c98d4441-8a4d-49c4-8120-5b44c30a4700

