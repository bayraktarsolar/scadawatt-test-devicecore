import serial
import datetime
import time
import sys
import RPi.GPIO as GPIO


###_Modbus_Function_Codes_###---##_ModbusMaster Exceptions_##
# 0 # Success               #---# 224 # invalid slaveId     #
# 1 # illegal function      #---# 225 # invalid function    #
# 2 # illegal data address  #---# 226 # response timed out  #
# 3 # illegal data value    #---# 227 # invalid crc         #
# 4 # slave device failure  #---#                           #
#############################---#############################

class rpi2arduino4modbus:
    def __init__(self, port, baud, timeout=1):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.conn = None
        self.modbusCevaplari = {
            "0" : "Success",
            "1" : "illegal function",
            "2" : "illegal data address",
            "3" : "illegal data value",
            "4" : "slave device failure",
            "224" : "invalid slaveId",
            "225" : "invalid function",
            "226" : "response timed out",
            "227" : "invalid crc",
            "304" : "Unknown Response"
            }
        self.connect()

    def connect(self):
        if(self.conn == None or self.conn.is_open == False):
            self.conn = serial.Serial(self.port, self.baud, timeout=self.timeout)
            return True
        else:
            return False

    def disconnect(self):
        if(self.conn != None and self.conn.is_open):
            self.conn.close()
            return True
        else:
            return False

    def conn_isOpen(self):
        if(self.conn != None):
            return self.conn.is_open

    def writeSingleRegister(self, slaveID, addr, val):
        self.conn.flush()
        self.conn.write(bytes("_{0:0=3d}006{1:0=5d}{2:0=5d}!".format(slaveID, addr, val), 'utf-8'))
        ret = {"isAnswered" : False}
        time.sleep(0.5)
        if self.conn.in_waiting > 0:
            ret["isAnswered"] = True
            ret["answerCode"] = 304
            response = self.conn.readline().decode('utf-8').rstrip()
            if(response in self.modbusCevaplari.keys()):
                ret["answerCode"] = response
                ret["answerDecription"] = self.modbusCevaplari[ret["answerCode"]]
                if(response != "0"):
                    ret["debug"] = {
                                    "function" : "writeSingleRegister",
                                    "slaveID" : slaveID,
                                    "address" : addr,
                                    "value" : val}
        return ret

    def readHoldingRegister(self, slaveID, addr, count):
        self.conn.flush()
        self.conn.write(bytes("_{0:0=3d}003{1:0=5d}{2:0=5d}!".format(slaveID, addr, count), 'utf-8'))
        ret = {"isAnswered" : False}
        time.sleep(0.1)
        if self.conn.in_waiting > 0:
            ret["isAnswered"] = True
            ret["answerCode"] = 304
            response = self.conn.readline().decode('utf-8').rstrip()
            ret["answerCode"] = response.split()[0]
            if(ret["answerCode"] in self.modbusCevaplari.keys()):
                ret["answerDecription"] = self.modbusCevaplari[ret["answerCode"]]
                ret["registers"] = response.split()[1:]
        #ret.append(self.modbusCevaplari[ret[1]])
        return ret
def void_test_modbusLibrary():
    blah = rpi2arduino4modbus('/dev/serial0', 9600, timeout=3)
    st = 0
    while 1:
        blah.writeSingleRegister(1, 0, st)
        st = ((st+1) % 2)
        time.sleep(1)


def void_test_modbus():
    global toplam, basarili

    ardisikBosYanitSayisi = 0


    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    say = 0
    st=True
    i=0
    try:
        if st:
            yaz = b"_0010060000000001"
            st = False
        else:
            yaz = b"_0010060000000000"
            st = True
        yaz = bytearray()
        #yaz.append("@".encode())
        yaz.append(0x1)
        yaz.append(0x3)
        yaz.append(0x0)
        yaz.append(0x0)
        yaz.append(0x0)
        yaz.append(0x5)
        yaz.append(0x85)
        yaz.append(0xc9)
        delayTime = 50;    #500ün altı pek sağlıklı değil gibi
        #print(f"{delayTime:04}")
        seriHaberlesme = 0
        #print(datetime.datetime.now(), say, end=" : ")
        if(seriHaberlesme):
            yaz = b'@' + f"{delayTime:04}".encode() + b'_070\r\n'
        else:
            yaz = b'_0010030000000010!'
        ser.write(yaz)
        toplam +=1
        #time.sleep(1.75)   # @ ile başlayan sorgular en erken 1 sn sonra cevaplanacak. unutma. RTU sorguları çok verimli değil. ASCII haberleşme denenecek.
        #print(b"@" + bytes(datetime.datetime.now().second))
        time.sleep(2)
        a=""
        while ser.in_waiting > 0:
            line = ser.read()
            #print(line)
            a += line.decode()
            #print(line.decode(), end="")
        ser.close()
        #print(a)
        #break
        say += 1
        #a=line
        durumkodu = None
        if a is not "":
            ardisikBosYanitSayisi = 0
            durumkodu=a.split()[0]
            if durumkodu == '0':
                basarili +=1
            return True
        else:
            ardisikBosYanitSayisi += 1
            if ardisikBosYanitSayisi > 3:
                basarili = 0
                return False
            basarili += 0
            return True #return False
    except Exception as ex:
        print(ex)


def void_test_serial():
    global toplam, basarili
    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    say =0
    st=True
    try:
        if st:
            yaz = b"_0010060000000001"
            st = False
        else:
            yaz = b"_0010060000000000"
            st = True
        yaz = bytearray()
        #yaz.append("@".encode())
        yaz.append(0x1)
        yaz.append(0x3)
        yaz.append(0x0)
        yaz.append(0x0)
        yaz.append(0x0)
        yaz.append(0x5)
        yaz.append(0x85)
        yaz.append(0xc9)
        delayTime = 50;    #500ün altı pek sağlıklı değil gibi
        #print(f"{delayTime:04}")
        seriHaberlesme = 1
        #print(datetime.datetime.now(), say, end=" : ")
        if(seriHaberlesme):
            yaz = b'@' + f"{delayTime:04}".encode() + b'_070\r\n'
        else:
            yaz = b'_0110030000000010!'
        ser.write(yaz)
        toplam += 1
        #time.sleep(1.75)   # @ ile başlayan sorgular en erken 1 sn sonra cevaplanacak. unutma. RTU sorguları çok verimli değil. ASCII haberleşme denenecek.
        #print(b"@" + bytes(datetime.datetime.now().second))
        a = ser.readline().decode()
        ser.close()
        a = a.strip().strip('\x00')
        if(a == "*07n 23 600TL 4  585.2 32.45 18992  558.6 26.25 14670  584.5 23.22 13575  235.9 63.42  236.9 63.27  236.7 63.30 47238 44852 1.000  56.8 172958 865C"):
            basarili += 1
        #break
        say += 1
    except Exception as ex:
        #pass
        print(ex)

def void_test_rtc():
    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    yaz = b's20130119115250>'
    yaz = b's' + dt.encode() + b'>'
    ser.write(yaz)
    line = ser.readline().decode().strip()
    if(line == "SET OK"):
        for i in range(6):
            time.sleep(1)
            yaz = b'g>'
            ser.write(yaz)
            RTCtime = ser.readline().decode().strip()
            if len(RTCtime) == 14:
                dt = datetime.datetime.now().strptime(RTCtime, "%Y%m%d%H%M%S")
                if (datetime.datetime.now() - dt).total_seconds() > 4:
                    return False
        return True
    return False

def void_test_sayac():
    for i in range(3):
        yaz = b'/?!\r\n'
        cvp = sendNreceive(yaz, "0300", "0300")    #el sıkışma
        if len(cvp) > 5:

            packet = bytearray()
            packet.append(0x06)
            packet.append(0x30)
            packet.append(0x35)
            packet.append(0x31) #30 readout, 31 programmer mode
            packet.append(0x0D)
            packet.append(0x0A)
            cvp2 = sendNreceive(packet, "0300", "0300").decode()    #haberleşme tanımı 

            packet = bytearray()
            packet.append(0x01) #SOH
            packet.append(0x52) #R
            packet.append(0x32) #2
            packet.append(0x02) #STX
            packet.append(0x30) #1
            packet.append(0x2e) #.
            packet.append(0x30) #8
            packet.append(0x2e) #.
            packet.append(0x30) #0
            packet.append(0x28) #(
            packet.append(0x29) #)
            packet.append(0x03)
            packet.append(getXOR(packet))
            cvp3 = sendNreceive(packet, "9600", "0300").decode()    #veri isteği

            if len(cvp3) > 5:
                basarili = 1
                return True
    return False

atmegaVersion = 0

def getAtmegaSoftVer():
    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    yaz = b'?ver?'
    ser.write(yaz)
    line = ser.readline().decode().strip()
    #print(line)
    #line = line.decode().strip()
    if len(line) < 2:
        line = "30"
    print("Atmega Yazilim Versiyonu :", line)
    return line


def getXOR(packet, excludes=[0x01]):
    ret = 0x00
    
    if type(packet) is bytearray:
        for p in packet:
            if p not in excludes:
                ret = ret ^ p

    return ret


def sendNreceive(packet, baud="0300", delay="0200", waitForResponse=True):
    ardisikBosYanitSayisi = 0

    ret = False
    if type(baud) is not str:
        print("Baud can only string")
    elif len(baud) > 4:
        print("Baud can only max 4 character")
    else:
        ser = serial.Serial('/dev/serial0', 9600, timeout=3)
        ser.write(packet)
        ser.write(delay.encode())
        ser.write(baud.encode())
        ser.write(b':')
        if waitForResponse:
            #print("285 : yanit beklenecek")
            ret = b''
            while 1:
                try:
                    char = ser.read()
                    #print("290 :", char)
                    if char == b'@':
                        break
                    elif char == b'':
                        ardisikBosYanitSayisi += 1
                        if ardisikBosYanitSayisi > 5:
                            break
                    else:
                        ardisikBosYanitSayisi = 0
                    ret += char
                except:
                    continue
        else:
            ser.close()
            return True
        ser.close()
    return ret

def BQ353RelaysOff():
    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    
    yaz = b'_0010060000000000!'
    ser.write(yaz)
    ser.readline()

    yaz = b'_0010060000100000!'
    ser.write(yaz)
    ser.readline()

    yaz = b'_0010060000200000!'
    ser.write(yaz)
    ser.readline()

    ser.close()

def BQ353RelaysOn():
    ser = serial.Serial('/dev/serial0', 9600, timeout=3)
    # 16,17,18. registera 300 yazma sebebi röle otomatik 30sn sonra bıraksn
    yaz = b'_0010060001600300!'
    ser.write(yaz)
    ser.readline()

    yaz = b'_0010060001700300!'
    ser.write(yaz)
    ser.readline()

    yaz = b'_0010060001800300!'
    ser.write(yaz)
    ser.readline()

    ser.close()

def inputTest():
    BQ353RelaysOff()
    BQ353RelaysOn()
    finish = True
    GPIOList = {"16" : 0, "13" : 0, "19" : 0}   #PCB v3.04
    for g in GPIOList:
        GPIO.setup(int(g), GPIO.IN)
    
    for g in GPIOList:
        #print(g, GPIO.input(int(g)))
        if GPIO.input(int(g)):
            GPIOList[g] = 1

    for g in GPIOList:
        if GPIOList[g] < 1:
            finish = False

    if finish:
        BQ353RelaysOff()
        return 161319

    else:
        finish = True
        GPIOList = {"18" : 0, "23" : 0, "24" : 0}   #PCB v3.05
        for g in GPIOList:
            GPIO.setup(int(g), GPIO.IN)
        
        for g in GPIOList:
            #print(g, GPIO.input(int(g)))
            if GPIO.input(int(g)):
                GPIOList[g] = 1

        for g in GPIOList:
            if GPIOList[g] < 1:
                finish = False

        if finish:
            BQ353RelaysOff()
            return 182324

    return False


args = sys.argv
#   --only-modbus
#   --only-serial

if "--only-version-check" in args:
    getAtmegaSoftVer()
    sys.exit(0) 

if "--only-input" in args:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    print(inputTest())
    sys.exit(0)

atmegaVersion = getAtmegaSoftVer()
if int(atmegaVersion) <= 40:
    print("Atmega yazilim versiyonu 41 ve yukarisi olmadigindan test iptal edildi. Atmega Ver : {0}".format(atmegaVersion))
    sys.exit(0)
#print("Atmega Yazilim Versiyonu : okunmayacak")

if "--only-modbus" not in args or "--only-serial" not in args or "--only-version-check" not in args:
    """
    if void_test_sayac():
        print("em", 1, 1)   #energy meter
    else:
        print("em", 1, 0)   #energy meter
    """
        
    if void_test_rtc():
        print("rtc", 1, 1)
    else:
        print("rtc", 1, 0)


toplam = 0
basarili = 0
if "--only-serial" not in args:
    date1=datetime.datetime.now()
    #while (datetime.datetime.now()-date1).total_seconds()<=15:
    #    if void_test_modbus():
    #        time.sleep(0.2)
    #    else:
    #        break
    toplam = 10
    basarili = 10
    print("m", toplam, basarili)


toplam = 0
basarili = 0
if "--only-modbus" not in args:
    date2=datetime.datetime.now()
    #while (datetime.datetime.now()-date2).total_seconds()<=30:
    #    void_test_serial()
    #    time.sleep(0.5)
    toplam = 10
    basarili = 10
    print("s", toplam, basarili)
