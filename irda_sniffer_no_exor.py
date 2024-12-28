import serial
import crc8
from colorama import Fore, Back, Style 
import sys
#ser = serial.Serial('/dev/ttyUSB0',115200)

max_package_size=0x20

def padded_hex(value):
 return '0x{0:0{1}X}'.format(value,2)#add 0x to every printed byte

if (len(sys.argv)<3):
    print("Usage: "+sys.argv[0]+"  <serial port> <output file>")
    exit()

ser = serial.Serial(sys.argv[1],115200)

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        for f in self.files:
            f.flush()

f = open(sys.argv[2], 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

while True:
 x=ser.read()
 if padded_hex(ord(x))!='0xA5': #for incompatible or corrupt data
  print(Fore.GREEN+padded_hex(ord(x)), end = ' ')
 else: #start packet if byte is 0xA5
  hash = crc8.crc8() #start CRC8 calculcation
  hash.update(x) #update CRC with first byte
  print("") #start new line for new byte
  print(Fore.RED+padded_hex(ord(x)), end = ' ')#print start byte in red
  print(Style.RESET_ALL, end = '')#reset print style
  for counter in range(2):
   x=ser.read()#read 2nd or 3rd byte
   hash.update(x) #update crc
   print(padded_hex(ord(x)), end = ' ')#print 2nd or 3rd byte
  if ord(x) & (1<<6):#check 6th bit of 3rd byte for long or short frame
   short_frame=False
  else:
   short_frame=True
  payload_size=0b00111111 & ord(x)#get payload size from 3rd byte
  if short_frame==False:#if long frame
   x=ser.read()#get 4th byte
   print(padded_hex(ord(x)), end = ' ')#print 4th byte
   hash.update(x)#update crc
   payload_size*=256
   payload_size+=ord(x)#add lower byte of payload size
  if payload_size>max_package_size: #reject package if size too large
    continue
  for counter in range(int(payload_size)):#read payload
   x=ser.read()
   hash.update(x)
   output=ord(x)
   if counter > 7: #if byte is part of layer 3 data
     print(Back.YELLOW+Fore.BLACK+padded_hex(output), end = ' ')#yellow if layer 3 data
   else:
     print(Back.WHITE+Fore.BLACK+padded_hex(output), end = ' ')#white if layer 2 data
  x=ser.read()
  if x==hash.digest():#print CRC byte
   print(Back.GREEN+padded_hex(ord(x))+Style.RESET_ALL)
  else:
   print(Back.RED+padded_hex(ord(x))+Style.RESET_ALL)
