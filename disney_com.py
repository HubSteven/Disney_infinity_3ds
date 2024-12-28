import crc8
import serial
from colorama import Fore, Back, Style
from time import sleep
import pickle

class Connection:
 def __init__(self, port, bat_level, debug=False):
  self.port = port
  self.status = False
  self.debug = debug
  self.conn_id = 0xFF
  self.msg_id = 0xFF
  self.bat_level=bat_level
  self.sector = None
  self.block = None
  self.data = None
  try:
    self.order = pickle.load(open("var.pickle", "rb"))
  except (OSError, IOError) as e:
    self.order = 0x00
    pickle.dump(self.order, open("var.pickle", "wb"))
  #print(self.order)

 def open_port(self):
  self.ser = serial.Serial(self.port,115200)

 def connection_status(self):
  return self.status

 sector=None
 block=None
 def get_message(self):
  packet=get_rawdata(self, self.ser)
  if packet==None:
   return
  if (packet[1]==0x20): #hack for power disc, resume connection after program termination
    self.conn_id=packet[0]
  if (packet[0]==self.conn_id):#check connection id from 3DS
   self.status=True
  else:
   self.status=False
  if (packet[2]==0x01):#check if connection request
   self.conn_id = packet[5]
   return CONNECTION_REQUEST
  if (packet[0]==self.conn_id): #check if packet is meant for receiver
    if (packet[2]==0x0F):
      return DISCONNECTION_REQUEST
    elif (packet[4] in commands):
      self.msg_id = packet[5] #message ident byte
      if(packet[4]==READ_NFC or packet[4]==WRITE_NFC):
       self.sector=packet[7]
       self.block=packet[8]
      if (packet[4]==WRITE_NFC):
          self.sector=packet[7]
          self.block=packet[8]
          self.data=packet[9:25]
      return packet[4]
    
 
 def handshake(self):
  print("HANDSHAKE")
  self.ser.write(header(disney_header([self.msg_id, 0x00, 0x20, 0x01, 0x00, 0x03, 0x04, 0x0A, 0x03, 0x43, 0x21, 0x27, 0x68, 0x39, 0x35, 0x4E, 0x34, 0x1B, 0xA6, 0x26, 0x9C]), self.conn_id))
  return

 def batt_status(self):
  print("BATTERY_STATUS")
  self.ser.write(header(disney_header([self.msg_id, self.bat_level]), self.conn_id))#battery level
  return

 def connect(self):
  #self.get_message() #get most up to date connection id
  #print(header([0x02], self.conn_id, RFU_bit=True))
  self.order = 0x00
  self.ser.write(header([0x02], self.conn_id, RFU_bit=True))
  if (self.get_message()==HANDSHAKE):
   self.status=True
  else:
   self.status=False
  return self.status
 
 def ack(self):
  print("ACK")
  self.ser.write(header(disney_header([self.msg_id]), self.conn_id))
  return
 
 def alive(self):
  print("ALIVE")
  self.ser.write(header(disney_header([self.msg_id, 0xff, 0xff, 0xff]), self.conn_id)) #three bytes are random
  return

 def uid(self, uid):
  print("UID")
  self.ser.write(header(disney_header([self.msg_id, 0x00] + uid), self.conn_id)) #7 UID bytes
  return

 def read_succes(self, nfc_data):
  print("READ_SUCCES")
  self.ser.write(header(disney_header([self.msg_id, 0x00] + nfc_data), self.conn_id))
  return
 
 def write_succes(self):
  print("WRITE_SUCCES")
  self.ser.write(header(disney_header([self.msg_id, 0x00]), self.conn_id))
  return
 
 def position(self, position):
  print("POSITION")
  self.ser.write(header(disney_header([self.msg_id, position, 0x09]), self.conn_id)) #order is 0x00
  return

 def figure_status(self, position):
  print("FIGURE STATUS")
  self.ser.write(header(disney_header([position, 0x09, self.order, 0x00], True), self.conn_id)) #order byte hard set to 0x00
  self.order+=0x01
  pickle.dump(self.order, open("var.pickle", "wb"))
  #print(get_number(header(disney_header([position, 0x09, 0x00, 0x00], True), self.conn_id)))
  return

 def disconnect(self):
  print("DISCONNECTED!")
  return

#CONNECTED,CONNECTION_REQUEST,DISCONNECTION_REQUEST,BATT_RQST,LED_FADE,LED_POSITION,CONNECTION_ALIVE=range(7)
commands=HANDSHAKE,DISCONNECTION_REQUEST,BATT_RQST,LED_POSITION,CONNECTION_ALIVE,LED_COLOR,LED_PULSE,LED_STROBE,NFC_POSITION,READ_NFC,WRITE_NFC,UID_REQUEST=[0x80, 0x84, 0x85, 0x90, 0x91, 0x92, 0x93, 0x94, 0xA1, 0xA2, 0xA3, 0xB4]
CONNECTION_REQUEST,DISCONNECTION_REQUEST=range(2)

#layer 1 header and crc
def header(data, session_id, RFU_bit=False):
 high, low =divmod(len(data), 0x100)
 high|=0b01000000 #set long frame bit
 if RFU_bit:#set RFU bit
  high|=0b10000000
  low|=0b10000000
 if (len(data)<64):
  data=[0xA5,session_id,low]+data
 else:
  data=[0xA5,session_id,high,low]+data
 hash = crc8.crc8()
 for x in range(len(data)):#add crc8 as last data byte to frame
  data[x]&=(1 << 8) - 1 #remove any signage
  hash.update(int.to_bytes(data[x], byteorder='little', length=1))
 data.append(ord(hash.digest()))
 #for x in range(len(data)):
  #data[x]=int.to_bytes(data[x], byteorder='little', length=1)
 return bytes(data)

#layer 2 checksum, packet length and padding
def disney_header(data, figure=False):
 data= [len(data)] + data#add data lentgh byte
 if figure:
  data= [0xAB]+data
 else:
  data= [0xAA]+data
 data.append(sum(data))
 while len(data) < 32: #padding
  data.append(0x00)
 #print(list(map(hex, data)))
 return data

def padded_hex(value):
 return '0x{0:0{1}X}'.format(value,2)

def get_rawdata(self, port):
 while True:
  data=[]
  x=port.read()
  if padded_hex(ord(x))!='0xA5': #for incompatible or corrupt data
   if self.debug: 
    print(Fore.GREEN+padded_hex(ord(x)))
  else: #start packet if byte is 0xA5
   hash = crc8.crc8() #start CRC8 calculcation
   hash.update(x) #update CRC with first byte
   if self.debug: 
    print("") #start new line for new byte
    print(Fore.RED+padded_hex(ord(x)), end = ' ')#print start byte in red
    print(Style.RESET_ALL, end = '')#reset print style
   for counter in range(2):
    x=port.read()#read 2nd or 3rd byte
    hash.update(x) #update crc
    if self.debug:
     print(padded_hex(ord(x)), end = ' ')#print 2nd or 3rd byte
    data.append(int.from_bytes(x, byteorder='big'))
   if ord(x) & (1<<6):#check 6th bit of 3rd byte for long or short frame
    short_frame=False
   else:
    short_frame=True
   payload_size=0b00111111 & ord(x)#get payload size from 3rd byte
   if short_frame==False:#if long frame
     x=port.read()#get 4th byte
     if self.debug:
      print(padded_hex(ord(x)), end = ' ')#print 4th byte
     hash.update(x)#update crc
     data.append(int.from_bytes(x, byteorder='big'))
     payload_size*=256
     payload_size+=ord(x)#add lower byte of payload size
   if payload_size>0x20: #reject package if size too large
    return None
   for counter in range(int(payload_size)):#read payload
     x=port.read()
     if self.debug:
      output=ord(x)
      if counter > 7: #if byte is part of layer 3 data
       print(Back.YELLOW+Fore.BLACK+padded_hex(output), end = ' ')#yellow if layer 3 data
      else:
       print(Back.WHITE+Fore.BLACK+padded_hex(output), end = ' ')#white if layer 2 data
     hash.update(x)
     data.append(int.from_bytes(x, byteorder='big'))
   x=port.read()
   if x==hash.digest():#check CRC byte
    if self.debug:
     print(Back.GREEN+padded_hex(ord(x))+Style.RESET_ALL)
    return data
   else:
    if self.debug:
     print(Back.RED+padded_hex(ord(x))+Style.RESET_ALL)
     return None
 
def get_number(values):
    b=[]
    for item in values:
     b.append(hex(item))
    return b