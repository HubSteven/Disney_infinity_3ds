import disney_com as disney
import disney_nfc as nfc
from time import sleep
import sys

if (len(sys.argv)<2):
    print("Usage: "+sys.argv[0]+"  <serial port> <character file on round pad> <character file on hexagon pad>")
    exit()

def get_number(values):#file list conversion
    b=[]
    for item in values:
     b.append(item)
    return b

position=None
if (len(sys.argv)>=3): #read figurine binary at set postion byte
    if (sys.argv[2]!="None"):
        nfc_tag_round=[]
        with open(sys.argv[2], mode="rb") as tag:
         nfc_tag_round=get_number(tag.read())
    if (len(sys.argv)>=4):
        nfc_tag_hex=[]
        with open(sys.argv[3], mode="rb") as tag:
         nfc_tag_hex=get_number(tag.read())

ir = disney.Connection(sys.argv[1], bat_level=0xff, debug=False) #battery level @ 0x4c gives low bat warning
ir.open_port()
i=0

while True:
    message = ir.get_message()
    if (message==disney.CONNECTION_REQUEST and not(ir.connection_status())):
        while not(ir.connection_status()):#keep trying until connected
            sleep(0.01)
            ir.connect()
    elif (message==disney.HANDSHAKE and ir.connection_status()):
        sleep(0.01)
        ir.handshake()
    elif (message==disney.BATT_RQST and ir.connection_status()):
        sleep(0.01)
        ir.batt_status()
    elif (message==disney.LED_COLOR or message==disney.LED_POSITION or message==disney.LED_PULSE or message==disney.LED_STROBE and ir.connection_status()): #must be different when figurine placed
        sleep(0.01)
        ir.ack()
        '''if (len(sys.argv)>2 and disney.LED_COLOR and i==0):
            i+=1
            if (sys.argv[2]!="None"):
                sleep(0.01)
                ir.figure_status(0x02)
            if (len(sys.argv)>3):
                sleep(0.01)
                ir.figure_status(0x01)'''
    elif (message==disney.CONNECTION_ALIVE and ir.connection_status()):
        sleep(0.01)
        ir.alive()
        if (i==0):
            i+=1
            if (len(sys.argv)>2 and sys.argv[2]!="None"):
                sleep(0.01)
                ir.figure_status(0x02)
            if (len(sys.argv)>3):
                sleep(0.01)
                ir.figure_status(0x01)
    elif (message==disney.UID_REQUEST and ir.connection_status()):
        sleep(0.01)
        if (sys.argv[2]!="None"):
                sleep(0.01)
                ir.uid(nfc_tag_round[0:7])
        if (len(sys.argv)>3):
                sleep(0.01)
                ir.uid(nfc_tag_hex[0:7])
    elif (message==disney.NFC_POSITION and ir.connection_status()):
        if (sys.argv[2]!="None"):
                sleep(0.01)
                ir.position(0x20)
        if (len(sys.argv)>3):
                sleep(0.01)
                ir.position(0x10)
    elif (message==disney.DISCONNECTION_REQUEST and ir.connection_status()):
        ir.disconnect()
        exit()
    elif (message==disney.READ_NFC and ir.connection_status()):
        if (sys.argv[2]!="None"):
                sleep(0.01)
                ir.read_succes(nfc.read_nfc(nfc_tag_round, ir.sector, ir.block))
        if (len(sys.argv)>3):
                sleep(0.01)
                ir.read_succes(nfc.read_nfc(nfc_tag_hex, ir.sector, ir.block))
    elif (message==disney.WRITE_NFC and ir.connection_status()):
        sleep(0.01)
        nfc_tag_round=nfc.write_nfc(nfc_tag_round, ir.data, ir.sector, ir.block)
        f = open(sys.argv[2], mode="wb")
        f.write(bytearray(nfc_tag_round))
        f.close()
        ir.write_succes()
