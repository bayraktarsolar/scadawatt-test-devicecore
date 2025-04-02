print("importing OS")
import os
print("importing traceback")
import traceback
print("importing paramiko")
import paramiko
print("importing requests")
import requests
print("importing json")
import json
print("importing time")
import time
print("importing GPIO")
import RPi.GPIO as GPIO
print("importing decodebytes")
from base64 import decodebytes
print("importing sys signal")
import sys, signal
print("importing datetime")
import datetime
print("importing threading")
import threading
print("importing netaddr")
from netaddr import *
print("importing get_mac")
from uuid import getnode as get_mac
print("importing connect")
import connect
print("importing ModbusClient")
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from random import randint

print("All modules imported")



class boxController():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        #ledlerin sırasıyla adreslerinin tanımlanması
        self.ledList = {1:9, 2:20, 3:22, 4:22, 5:27, 6:4, 7:23, 8:26}  #[11, 9, 10, 22, 27, 17, 5]
        self.buttonList = {1:24, 2:25}

        #self.led_program = 2
        self.led_baglanti = 1
        self.led_update = 2
        self.led_upgrade = 2
        self.led_otherDevices = 3 #RTC-EM...
        self.led_modbus = 4
        self.led_serial = 5
        self.led_success = 8
        
        self.continueFlag = True
        self.threadParams = {}
        self.blinkThreadList = {}

        #ledlerin OUT olarak tanımlanması
        for ledNo, GPIOno in self.ledList.items():
            GPIO.setup(GPIOno, GPIO.OUT)
            self.threadParams[ledNo] = False

        #Butonların IN olarak tanımlanması
        for btNo, GPIOno in self.buttonList.items():
            GPIO.setup(GPIOno, GPIO.IN)

        self.ledTest()

        #başlangıçta tüm ledlerin kapatılması
        self.turnOff()

    def getButtonState(self, btNo):
        if btNo in self.buttonList.keys():
            return GPIO.input(self.buttonList[btNo])
        else:
            print(btNo, "adında bir buton yok")
            return 1

    def ledTest(self):
        for ledNo, GPIOno in self.ledList.items():
            self.turnOn(ledNo)
            time.sleep(0.2)
        time.sleep(1)
        self.turnOff()
        

    def setLedVal(self, ledNo, val):
        #print("setLedVal", ledNo, self.ledList[ledNo], val)
        self.blinkThreadStop(ledNo)
        if(ledNo in self.ledList.keys()):
            GPIO.output(self.ledList[ledNo], val)
        else:
            print(ledNo, "adinda bir led yok")

    def turnOff(self, ledNo=None):
        if(ledNo is None):
            for ledNo, GPIOno in self.ledList.items():
                self.setLedVal(ledNo, 0)
        else:
            self.setLedVal(ledNo, 0)

    def turnOn(self, ledNo=None):
        if(ledNo is None):
            for ledNo, GPIOno in self.ledList.items():
                self.setLedVal(ledNo, 1)
        else:
            self.setLedVal(ledNo, 1)

    def blink(self, ledNo, delay, param=1):
        say = -1
        while self.threadParams[ledNo]:
            if(param != 0):
                say += 1
            if(say >= param):
                break
            if(ledNo in self.ledList.keys()):
                GPIO.output(self.ledList[ledNo], 1)
                time.sleep(delay)
                GPIO.output(self.ledList[ledNo], 0)
                time.sleep(delay)
            else:
                break
        #print(ledNo, "için Blink sonlandı")

    def blinkThreadStart(self, ledNo, delay, param):
        self.threadParams[ledNo] = False
        if(ledNo in self.blinkThreadList.keys()):
            self.blinkThreadList[ledNo].join()
        self.threadParams[ledNo] = True
        th = threading.Thread(name=str(ledNo)+"_ledBlink", target=self.blink, args=[ledNo, delay, param], daemon=True)
        th.start()
        self.blinkThreadList[ledNo] = th
        return th

    def blinkThreadStop(self, ledNo):
        if(ledNo in self.blinkThreadList.keys()):
            self.threadParams[ledNo] = False
            self.blinkThreadList[ledNo].join()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

args = sys.argv
#   --only-update
#   --no-modbus #not available
#   --no-serial #not available
#   --no-update
#   --no-test
#   --force-test

bc = boxController()
"""GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
while 1:
    input_state=GPIO.input(26)  
    print(input_state)
    time.sleep(1)

sys.exit(0)"""

def receiveSignal(signalNumber, frame):
    print(" Durdurma Sinyali :", signalNumber)
    bc.turnOff()
    sys.exit(signalNumber)  

signal.signal(signal.SIGHUP, receiveSignal)
signal.signal(signal.SIGINT, receiveSignal)
signal.signal(signal.SIGQUIT, receiveSignal)
signal.signal(signal.SIGILL, receiveSignal)
signal.signal(signal.SIGTRAP, receiveSignal)
signal.signal(signal.SIGABRT, receiveSignal)
signal.signal(signal.SIGBUS, receiveSignal)
signal.signal(signal.SIGFPE, receiveSignal)
#signal.signal(signal.SIGKILL, receiveSignal)
signal.signal(signal.SIGUSR1, receiveSignal)
signal.signal(signal.SIGSEGV, receiveSignal)
signal.signal(signal.SIGUSR2, receiveSignal)
signal.signal(signal.SIGPIPE, receiveSignal)
signal.signal(signal.SIGALRM, receiveSignal)
signal.signal(signal.SIGTERM, receiveSignal)


gecerlilik_modbus = 0.9
gecerlilik_serial = 0.3

time.sleep(0.5)
#bc.turnOn(bc.led_program)
bc.threadParams[0] = True
"""
bc.blinkThreadStart(3, 0.5, 0)

time.sleep(2)

bc.blinkThreadStart(3, 0.1, 0)
time.sleep(2)
bc.turnOn(3)

time.sleep(3)

bc.blinkThreadStop(3)

bc.turnOff()
print("ana thread kapandı")
sys.exit(0)
"""

def print_okgreen(text):
    print("{start}{text}{end}".format(start=bcolors.OKGREEN, text=str(text), end=bcolors.ENDC))

def print_fail(text):
    print("{start}{text}{end}".format(start=bcolors.FAIL, text=str(text), end=bcolors.ENDC))

def print_okblue(text):
    print("{start}{text}{end}".format(start=bcolors.OKBLUE, text=str(text), end=bcolors.ENDC))

def print_okcyan(text):
    print("{start}{text}{end}".format(start=bcolors.OKCYAN, text=str(text), end=bcolors.ENDC))

def print_success(text):
    print("{start}{text}{end}".format(start=bcolors.HEADER, text=str(text), end=bcolors.ENDC))

def print_warning(text):
    print("{start}{text}{end}".format(start=bcolors.WARNING, text=str(text), end=bcolors.ENDC))

scd_test_mac_s = [['74', 'be'], ['7a', '47'], ['7d', '71']]
clients_path = "/root/scd_tester/clients/"

def getMacAddress(ssh):
    try:
        stdin,stdout,stderr = ssh.exec_command("ifconfig |grep ether")
        exit_status = stdout.channel.recv_exit_status()
        stdout.channel.set_combine_stderr(True)
        if exit_status == 0:
            sonuc = stdout.readlines()
            return sonuc[0].split()[1]
    except Exception as ex:
        print_fail("getMacAddress : {0}".format(str(ex)))
        return False

def controlClientFiles():
    print("Checking client files")
    try:
        dir_list = os.listdir(clients_path)
        mac_list = {}
        for client_file in dir_list:
            with open("clients/" + client_file) as f:
                client_file_data = f.readlines()
                for line in client_file_data:
                    mac = None
                    if "scd_" in line:
                        if '_' in line.split('=')[1]:
                            mac = line.split('=')[1].split('_')[1].strip()
                        else:
                            mac = line.split('=')[1].strip()
                        if mac is not None:
                            if mac in mac_list:
                                mac_list[mac].append(client_file)
                            else:
                                mac_list[mac] = [client_file]
                            break
        ret = True
        for mac in mac_list:
            if len(mac_list[mac]) > 1:
                ret = False
                print_fail("{mac} sonlu MAC adresinin Clients altinda birden fazla profili bulunuyor. Lutfen asagidaki dosyalari kontrol edin 1 tane kalacak sekilde silin!".format(mac=mac))
                i = 1
                for client_file in mac_list[mac]:
                    print_warning("{i}) {client_file}\t=> {mac}".format(i=i, client_file=client_file, mac=mac))
                    i += 1
        return ret

    except Exception as ex:
        print_fail("controlClientFiles : {0}".format(str(ex)))
        return False

def getNewMacAddressFromVpnClientFile():
    try:
        dir_list = os.listdir(clients_path)
        if len(dir_list) > 0:
            return dir_list[0]
        else:
            return False
    except Exception as ex:
        print_fail("getNewMacAddressFromVpnClientFile : {0}".format(str(ex)))
        return False

def decodeClientFile(client_file):
    print_success("Checking Clone Client Files")
    try:
        with open("clients/" + client_file) as f:
            client_file_data = f.readlines()

            for line in client_file_data:
                if "scd_" in line:
                    if '_' in line.split('=')[1]:
                        return line.split('=')[1].split('_')[1].strip()
                    else:
                        return line.split('=')[1].strip()
    except Exception as ex:
        print_fail("decodeClientFile : {0}".format(str(ex)))
        return False
    
def overlay_control(ssh):
    stdin, stdout, stderr = ssh.exec_command("df -h | egrep overlay | tr -s ' ' | cut -d ' ' -f 5")
    if len(stdout.read().decode("utf-8")) >= 2:
        print("Cihaz hafızası yazmaya karşı korumalı.")
        return True
    else:
        return False
    
def disable_overlay(ssh):
    print("Yazma koruması kapatıldı. Yeniden başlatılıyor...")
    ssh.exec_command("raspi-config --disable-overlayfs && reboot")
    
def enable_overlay(ssh):
    print("Yazma koruması yeniden etkinlestiriliyor. Bu biraz zaman alacak...")
    stdin, stdout, stderr = ssh.exec_command("raspi-config --enable-overlayfs && reboot")
    exit_status = stdout.channel.recv_exit_status()
    stdout.channel.set_combine_stderr(True)
    print("Yazma koruması yeniden etkinlestirildi. Cihaz yeniden baslatiliyor.")

def setHostname(ssh, sf):
    try:
        ssh.exec_command("hostnamectl set-hostname scadawatt-" + sf.lower())
        print_okgreen("OK ... Device hostname updated : scadawatt-{0}".format(sf.lower()))
    except Exception as ex:
        print_fail("setHostname : {0}".format(str(ex)))
        return False

def setMacAddress(ssh, last4):
    return setDHCPCDconfig(last4)
    try:
        file = ['# interfaces(5) file used by ifup(8) and ifdown(8)\n', '\n', '# Please note that this file is written to be used with dhcpcd\n', "# For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'\n", '\n', '# Include files from /etc/network/interfaces.d:\n', 'source-directory /etc/network/interfaces.d\n', '\n', '# Network interfaces\n', 'auto eth0\n', 'allow-hotplug eth0\n', 'iface eth0 inet dhcp\n']
        interfaces = open("/root/scd_tester/cache/interfaces", "w")
        for line in file:
            interfaces.write(line)
        interfaces.write("hwaddress ether 5c:ad:a3:a7:{0}:{1}\n".format(last4[0:2], last4[2:4]))
        interfaces.close()

        sftp=ssh.open_sftp()
        sftp.put('/root/scd_tester/cache/interfaces','/etc/network/interfaces')
        sftp.close()

        print_okgreen("OK ... setMacAddress : 5c:ad:a3:a7:{0}:{1}".format(last4[0:2], last4[2:4]))

        return True
    except Exception as ex:
        print_fail("setMacAddress : {0}".format(str(ex)))
        return False

def setDHCPCDconfig(last4):
    global ssh
    try:
        sftp=ssh.open_sftp()
        sftp.put("/root/scd_tester/mac2.py", "/root/mac2.py")
        sftp.close()
        print_okgreen("OK ... copy mac2 file")
        stdin,stdout,stderr = ssh.exec_command("python3 /root/mac2.py -m " + last4.replace(":", ""), timeout=10)

        print("Network yapilandirmasi degistirildi. Baglanti yeniden kurulacak.")

        exit_status = stdout.channel.recv_exit_status()

        for a in range(120):
            ssh = connectSSH(ip, kullanici, sifre, False)
            if ssh:
                print_okgreen("Bağlantı yeniden sağlandı")
                break
            time.sleep(1)
        if exit_status == 0:
            return True
        else:
            print("setDHCPCDconfig icin cikis kodu hatali!!!", exit_status)
            return False
    except Exception as ex:
        print_fail("setDHCPCDconfig : {0}".format(str(ex)))
        print(traceback.format_exc())
        return False

def sendVpnProfile(ssh, client_file):
    try:
        sftp=ssh.open_sftp()
        sftp.put("/root/scd_tester/clients/" + client_file, "/etc/openvpn/client.ovpn")
        sftp.close()
        print_okgreen("OK ... sendVpnProfile : " + client_file)
        os.remove("/root/scd_tester/clients/" + client_file)
        print_okgreen("OK ... delete VPN profile from cache : " + client_file)
        return True
    except Exception as ex:
        print_fail("sendVpnProfile : {0}".format(str(ex)))
        return False

def setRootPassword(ssh, last4):
    try:
        print(last4)
        ssh.exec_command('echo "root:scd_{0}" | chpasswd'.format(last4.lower()))
        print_okgreen("OK ... Root Password Updated : scd_{0}".format(last4.lower()))
    except Exception as ex:
        print_fail("setRootPassword : {0}".format(str(ex)))
        return False

def setPiPassword(ssh):
    try:
        ssh.exec_command('echo "pi:Sc@d@w@++" | chpasswd')
        print_okgreen("OK ... Pi Password Updated : Sc@d@w@++")
    except Exception as ex:
        print_fail("setPiPassword : {0}".format(str(ex)))
        return False

def connectSSH(ip, kullanici, sifre, is_silent=False):
    try:
        if is_silent == False:
            print_okgreen("Connecting SSH")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(ip, username=kullanici,password=sifre, timeout=3)
        stdin,stdout,stderr = ssh.exec_command("systemctl stop scadawatt")
        exit_status = stdout.channel.recv_exit_status()
        stdout.channel.set_combine_stderr(True)
        return ssh
    except Exception as ex:
        if is_silent == False:
            # bu alan debug için kullanılmaktadır
            print_okgreen(ip); 
            print_okgreen(kullanici);
            print_okgreen(sifre);
            # -------------
            print_fail("connectSSH : {0}".format(str(ex)))
        return False

ara = None
for arg in args:
    if arg[0:5] == "--mac":
        ara = arg[5:]
        print_okcyan("Elle girilen MAC adresi icin zorlanacak")
        print("importing openpyxl")
        import openpyxl
        dataframe = openpyxl.load_workbook("macs.xlsx", read_only=True)
        ws = dataframe.active
        ara = ara[0:2] + ":" + ara[2:4]

        found = False
        for row in ws.rows:
            if row[0].value == "5c:ad:a3:a7:" + ara:
                cvp = {}
                cvp["hata"] = False
                cvp["data"] = []
                temp = {}
                temp["swd_mac"] = row[0].value.replace(":", "-")
                temp["swd_ip_local"] = "scadawatt-" + ara.replace(":","") + ".local" #row[11].value
                temp["swd_ip_vpn"] = row[11].value
                temp["swd_test"] = 0
                cvp["data"].append(temp)
                found = True
                break

        if found == False:
            print_fail("Girilen MAC hatali veya bilinen listesinde yok !!!!")
            sys.exit(0)
        break

while bc.continueFlag:
    try:
        #bc.turnOn(bc.led_program)
        if ara == None:
            rs = requests.get("https://api.scadawatt.com/v2/scdTestDeviceInfo") # v2 olan local IP kontrolü yapar. v1 olan komple eski usül
            cvp = json.loads(rs.text)
        if(cvp["hata"] == False):
            #tamam istek doğru. En az 1 tane SCD cihazı bilgisi bize geldi
            for i in cvp["data"]:

                rsx = requests.post("https://api.scadawatt.com/v2/scdTestDeviceServiceEntry", data = json.dumps({"mac" : i["swd_mac"]}))
                cvpx = json.loads(rsx.text)

                if(rsx.status_code == 401):
                    # serviste durumu düzeltilmeye müsait cihaz var. Sormak lazım,
                    print_warning("!!!!! Bu cihaz ile ilgili servise girisi yapilmamis bir teknik servis formu mevcut.")
                    kullanici_cevap_guncelle = input("Formu guncelleyerek \"Servise Giriş Yaptı\" olarak guncellemek istiyor musunuz? : ")
                    if kullanici_cevap_guncelle.lower() in ["evet", "evt", "ev", "yes", "e", "y", "ivit", "yep", "olur", "güncelle", "guncelle", "yap", "ok", "okey", "oke"]:
                        rsx = requests.post("https://api.scadawatt.com/v2/scdTestDeviceServiceEntry", data = json.dumps({"mac" : i["swd_mac"], "onay" : 1}))
                        cvpx = json.loads(rsx.text)
                        if(rsx.status_code == 200):
                            print_okgreen("OK ... Servis formu guncellendi. Islemlere devam ediliyor.")
                        else:
                            print_fail("ERR : Form guncellenirken hata olustu. Lutfen elle WEB uzerinden kontrol edin!!")
                    else:
                        print_okcyan(["Pekala, formu guncellemiyorum.", "Tamam, siz bilirsiniz.", "Olur guncellemiyorum.", "O halde siz WEB panelinden guncelleyebilirsiniz.", "Form durumunu WEB panelden kontrol etmeyi unutmayin...", "Tamam, formu guncellemeden gectim.", "Tamam, guncellemeden devam ediyorum"][randint(0, 6)])

                bc.turnOff(2)
                bc.turnOff(3)
                bc.turnOff(4)
                bc.turnOff(5)
                bc.turnOff(6)
                bc.turnOff(7)
                bc.blinkThreadStart(bc.led_baglanti, 0.5, 0)  #ikinci aşama başlangıcı
                
                kontrol_1 = False
                kontrol_2 = False
                kontrol_3 = False
                kontrol_4 = False
                kontrol_5 = True
                otherDevices_success = True
                
                test_modbus = True
                test_serial = True
                test_test = True

                if "--force-test" in args:
                    print("--force-test parametresi uyarinca ZORLA TEST edilecektir.")
                    i["swd_test"] = 0
                if i["swd_test"] == "1":
                    print("[ " + i["swd_mac"] + " ] : Bu cihaz zaten daha once test edilmis. --force-test parametresi gondermediginiz icin haberlesme testi atlanacaktir.")
                    if "--no-modbus" not in args:
                        test_modbus = False
                    if "--no-serial" not in args:
                        test_serial = False
                    if "--no-test" not in args:
                        test_test = False


                sf = i["swd_mac"].split("-")[4] + i["swd_mac"].split("-")[5]
                ip = i["swd_ip_local"]
                kullanici = "root"
                sifre = "scd_"+sf.lower()
                port = 22
                print_okblue(str(i["swd_ip_local"]) + " icin baglanti saglayabiliriz")
                print_okblue("MAC Address : {0}".format(str(i["swd_mac"])))
                print_okblue("VPN Address : {0}".format(str(i["swd_ip_vpn"])))
                #gelen = os.system('sshpass -p "scd_7b7a" scp /root/deneme.py root@192.168.1.143:/root')
                #gelen = os.system('sshpass -p "'+sifre+'" scp /root/deneme.py root@' + i["swd_ip_local"]+':/root')
                #print(gelen)
                #if(gelen==0):
                komut = "python3 remoteTestAgent.py"
                try:
                    #ip = "192.168.1.166"
                    #kullanici = "root"
                    #sifre = "scd_71a3"
                    ssh = connectSSH(ip, kullanici, sifre)
                    
                    if ssh is False:
                        kontrol_1 = False
                        bc.blinkThreadStart(bc.led_baglanti, 0.1, 0)
                        print_fail("Connection failed for {0}@{1}:{2}".format(ip, kullanici, sifre))
                        time.sleep(5)
                    else:
                        kontrol_1 = True
                        bc.turnOn(bc.led_baglanti)

                        is_overlayed = overlay_control(ssh)
                                
                        if is_overlayed:
                            disable_overlay(ssh)
                            print_warning("Yazma koruması kapatıldı. Yeniden bağlantı bekleniyor...")
                            time.sleep(10)
                            for a in range(120):
                                ssh = connectSSH(ip, kullanici, sifre, True)
                                if ssh:
                                    print_okgreen("Bağlantı yeniden sağlandı")
                                    break
                                time.sleep(1)
                            
                        if ssh is False:
                            kontrol_1 = False
                            print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                            print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                            print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                            sys.exit(0)

                    if kontrol_1:    
                        if "--set-mac" in args:
                            bc.blinkThreadStart(bc.led_update, 0.5, 0) #update aşama başlangıcı
                            if controlClientFiles() == False:
                                kontrol_5 = False

                                #bc.blinkThreadStart(bc.led_program, 0.1, 0)
                                
                                print_fail(28 * "-" + " D i K K A T " + 29 * "-")
                                print_fail("| Client dosyalarinda hata oldugundan --set-mac islemi yapilmayacak! |")
                                print_fail("| Client dosyalarinda hata oldugundan --set-mac islemi yapilmayacak! |")
                                print_fail("| Client dosyalarinda hata oldugundan --set-mac islemi yapilmayacak! |")
                                print_fail(70 * "-")
                            else:
                                
                                is_overlayed = overlay_control(ssh)
                                
                                if is_overlayed:
                                    disable_overlay(ssh)
                                    print_warning("Yazma koruması kapatıldı. Yeniden bağlantı bekleniyor...")
                                    time.sleep(10)
                                    for a in range(120):
                                        ssh = connectSSH(ip, kullanici, sifre)
                                        if ssh:
                                            print_okgreen("Bağlantı yeniden sağlandı")
                                            break
                                        time.sleep(1)
                                    
                                if ssh is False:
                                    print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                                    print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                                    print_fail("| BAĞLANTI BEKLENMEDİK BİR ŞEKİLDE KOPTU |")
                                    sys.exit(0)

                                else:

                                    mac = getMacAddress(ssh)
                                    if mac is False:
                                        print_fail("Mac address cannot reading. Please try again later.")

                                    mac_s = mac.split(':')

                                    mac_degisecek = False
                                    if mac_s[0] == "5c" and mac_s[1] == "ad":
                                        #mac adresi Scadawatt için uygun
                                        for m in scd_test_mac_s:
                                            if m[0] == mac_s[4] and m[1] == mac_s[5]:
                                                #MAC adresi test veya ilk kurulumdaki cihazlar için tanımlanmış. Değiştirilmesi gerek
                                                mac_degisecek = True
                                                break
                                    else:
                                        mac_degisecek = True

                                    if mac_degisecek:
                                        print_okblue("!!!!!!!!!! MAC DEGISECEK !!!!!!!!!!")
                                        client_file = getNewMacAddressFromVpnClientFile()
                                        if client_file is not False:
                                            last4 = decodeClientFile(client_file)
                                            if last4 is not False:
                                                #last4 = "74be" #debug
                                                print_okblue(last4)
                                                setHostname(ssh, last4)
                                                setMacAddress(ssh, last4)
                                                sendVpnProfile(ssh, client_file)
                                                setPiPassword(ssh)
                                                setRootPassword(ssh, last4)

                                                # eğer SSH bağlantısı koparsa; sebebi Root Password değişimidir.
                                                #sifre = "scd_" + last4.lower()
                                                #ssh.close()
                                                #ssh = paramiko.SSHClient()
                                                #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                                #ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
                                                #ssh.connect(ip, username=kullanici,password=sifre)
                                            else:
                                                print_fail("VPN Client Profile broken. Please check file : {0}".format(client_file))
                                                kontrol_5 = False
                                        else:
                                            print_fail("Client File Not Found")
                                            kontrol_5 = False
                                        
                                    else:
                                        setHostname(ssh, sf)

                        else:
                            setDHCPCDconfig(sf)

                        
                        sftp=ssh.open_sftp()
                        sftp.put('/root/scd_tester/remoteTestAgent.py','/root/remoteTestAgent.py')
                        sftp.close()
                        print_okgreen("OK ... Test module sent.")
                        kontrol_1 = True
                except Exception as ex:
                    bc.blinkThreadStart(bc.led_baglanti, 0.1, 0)
                    print_fail("mainJob : " + str(ex))
                    print(traceback.format_exc())
                    #parola yanlışsa vs buraya düşüyor mu kontrol edelim.

                if(kontrol_1):
                    if "--no-update" not in args:
                        print_okcyan("Configuration starting")
                        bc.blinkThreadStart(bc.led_update, 0.5, 0) #update aşama başlangıcı
                        ret_update = connect.start(ssh, bc, i, "update")
                        if kontrol_5:
                            if ret_update[0] and ret_update[1] and ret_update[3] and ret_update[4] and ret_update[5]:
                                bc.turnOn(bc.led_update)
                            else:
                                bc.blinkThreadStart(bc.led_update, 0.1, 0) #update fail
                        else:
                            bc.blinkThreadStart(bc.led_update, 0.1, 0) #update fail

                    if "--no-upgrade" not in args:
                        print_okcyan("... SCD Version Upgrade Wizard Running ...")
                        bc.blinkThreadStart(bc.led_upgrade, 0.5, 0) #upgrade aşama başlangıcı
                        ret_update = connect.start(ssh, bc, i, "upgrade")
                        if ret_update[2]:
                            bc.turnOn(bc.led_upgrade)
                        else:
                            bc.blinkThreadStart(bc.led_upgrade, 0.1, 0) #upgrade fail
                        stdin,stdout,stderr = ssh.exec_command("systemctl stop scadawatt")
                        exit_status = stdout.channel.recv_exit_status()
                        stdout.channel.set_combine_stderr(True)
                        
                    if "--no-test" not in args and test_test:
                        os.system("systemctl start seri_oku.service")
                        print_okcyan("Serial test and Modbus test starting.")
                        bc.blinkThreadStart(bc.led_modbus, 0.5, 0)  #modbus aşama başlangıcı
                        bc.blinkThreadStart(bc.led_serial, 0.5, 0)  #serial test başlangıcı
                        bc.blinkThreadStart(bc.led_otherDevices, 0.5, 0)  #test başlangıcı
                        stdin,stdout,stderr = "", "", ""
                        try:
                            s1 = datetime.datetime.now()
                            stdin,stdout,stderr = ssh.exec_command(komut)
                            exit_status = stdout.channel.recv_exit_status()
                            stdout.channel.set_combine_stderr(True)
                            if exit_status == 0:
                                sonuc = stdout.readlines()
                                print_okblue("Modbus-Serial Test Süresi : " + str(datetime.datetime.now()-s1) + " sn")
                                time.sleep(2)
                                kontrol_2 = True
                        except:
                            print_fail("Bağlantıda hata var. İşlem verilen sürede bitmedi!")
                            bc.blinkThreadStart(bc.led_baglanti, 0.1, 0)
                            bc.blinkThreadStart(bc.led_otherDevices, 0.1, 0)
                            bc.blinkThreadStart(bc.led_modbus, 0.1, 0)
                            bc.blinkThreadStart(bc.led_serial, 0.1, 0)
                        if(kontrol_2):
                            otherDevices_success = True
                            for s in sonuc:
                                data = s.strip().split()
                                print_okblue(data)

                                if(data[0] == "m"):
                                    if(int(data[2]) >= int(data[1])*gecerlilik_modbus):
                                        kontrol_3 = True
                                        #print_okgreen("OK ... Modbus Test")
                                        bc.turnOn(bc.led_modbus)
                                    else:
                                        print("Err ... Modbus Test")
                                        if(int(data[2]) == -1):
                                            print_warning("Check : Raspberry and Arduino connection or Atmega328p software")
                                        bc.blinkThreadStart(bc.led_modbus, 0.1, 0)

                                elif(data[0] == "s"):
                                    if(int(data[2]) >= int(data[1])*gecerlilik_serial):
                                        bc.turnOn(bc.led_serial)
                                        kontrol_4 = True
                                        #print_okgreen("OK ... Serial Test")
                                    else:
                                        print_fail("Err ... Serial Test")
                                        bc.blinkThreadStart(bc.led_serial, 0.1, 0)

                                elif(data[0] == "em"):
                                    if(int(data[2]) == int(data[1])):
                                        print_okgreen("OK ... Energy Meter")
                                    else:
                                        print_fail("Err ... Energy Meter")
                                        otherDevices_success = False

                                elif(data[0] == "rtc"):
                                    if(int(data[2]) == int(data[1])):
                                        print_okgreen("OK ... RTC")
                                    else:
                                        print_fail("Err ... RTC")
                                        otherDevices_success = False

                                elif data[0] == "Atmega":
                                    atmegaVersion = data[4]
                                    if atmegaVersion == "okunmayacak":
                                        print_okgreen("Atmega versiyon kontrolu kapatılmıs, okunmayacak.")
                                    else:
                                        if atmegaVersion.isdigit() is False:
                                            atmegaVersion = 30
                                        if int(atmegaVersion) <= 40:
                                            print_fail("Atmega Version : {:.2f} \nAtmega Version KESINLIKLE yukseltilmeli. Test iptal edilecek.\nAtmega Version en az 4.1 olmalı.".format(int(atmegaVersion)/10))
                                            print_fail("Atmega Version : {:.2f} \nAtmega Version KESINLIKLE yukseltilmeli. Test iptal edilecek.\nAtmega Version en az 4.1 olmalı.".format(int(atmegaVersion)/10))
                                            print_fail("Atmega Version : {:.2f} \nAtmega Version KESINLIKLE yukseltilmeli. Test iptal edilecek.\nAtmega Version en az 4.1 olmalı.".format(int(atmegaVersion)/10))
                                            print_fail("Atmega Version : {:.2f} \nAtmega Version KESINLIKLE yukseltilmeli. Test iptal edilecek.\nAtmega Version en az 4.1 olmalı.".format(int(atmegaVersion)/10))
                                        else:
                                            print_okgreen("Atmega Version : {:.2f}".format(int(atmegaVersion)/10))

                                if otherDevices_success:
                                    bc.turnOn(bc.led_otherDevices)
                                else:
                                    bc.blinkThreadStart(bc.led_otherDevices, 0.1, 0)

                        kontrol_6 = False
                        komut = "python3 remoteTestAgent.py --only-input"
                        stdin,stdout,stderr = ssh.exec_command(komut)
                        exit_status = stdout.channel.recv_exit_status()
                        stdout.channel.set_combine_stderr(True)
                        inputVersion = None
                        if exit_status == 0:
                            inputVersion = stdout.readline().strip()
                            if inputVersion != "False":
                                print_okgreen("OK ... inputs")
                                print_okgreen("OK ... RS485")
                                kontrol_6 = True
                                if inputVersion == "182324":
                                    print_okgreen("PCB Version >= v3.05")
                                elif inputVersion == "161319":
                                    print_okblue("PCB Version < v3.05")
                                else:
                                    print_warning("PCB Version Unknown !")

                            else:
                                print_fail("ERR ... inputs (Bu sebeple RS485 hatali cikmis olabilir.)")
                                print_fail("ERR ... RS485 (Bu sebeple input hatali cikmis olabilir.)")



                        
                        if(kontrol_1 and kontrol_2 and kontrol_3 and kontrol_4 and kontrol_6):
                            #bc.turnOn(bc.led_success)
                            print_okblue("Serial and Modbus tests are OK. Writing database.")
                            requests.put("https://api.scadawatt.com/v2/swd_device_info", data = json.dumps({"swd_mac" : i["swd_mac"], "test" : "1", "inputVersion" : inputVersion, "atmegaVersion" : atmegaVersion}))
                        else:
                            print_fail("Haberlesme modulleri testi gecemedi")
                            if kontrol_1 is False:
                                print_fail("kontrol_1 is False")
                            if kontrol_2 is False:
                                print_fail("kontrol_2 is False")
                            if kontrol_3 is False:
                                print_fail("kontrol_3 is False")
                            if kontrol_4 is False:
                                print_fail("kontrol_4 is False")
                            if otherDevices_success is False:
                                print_fail("otherDevices_success is False")
                            if kontrol_6 is False:
                                print_fail("kontrol_6 is False")
                                                        #bc.blinkThreadStart(bc.led_success, 0.1, 0)

                    #os.system("systemctl stop seri_oku")
                        
                    stdin,stdout,stderr = ssh.exec_command("systemctl start scadawatt")
                    exit_status = stdout.channel.recv_exit_status()
                    stdout.channel.set_combine_stderr(True)


                    # her şey bitti. Overlay enable yapalım
                    if ret_update[2]:
                        enable_overlay(ssh)
                        print_warning("Yeniden baglanti bekleniyor...")
                        time.sleep(10)
                        for a in range(120):
                            ssh = connectSSH(ip, kullanici, sifre, True)
                            if ssh:
                                stdin,stdout,stderr = ssh.exec_command("systemctl restart scadawatt")
                                exit_status = stdout.channel.recv_exit_status()
                                stdout.channel.set_combine_stderr(True)
                                print_okgreen("Baglanti yeniden saglandi.")
                                break
                            time.sleep(1)
                        if ssh is False:
                            print_fail("| Yazma korumasi sonrasi cihaz yeniden baglanti kuramadi. Kontrol gerekli. |")
                            print_fail("| Yazma korumasi sonrasi cihaz yeniden baglanti kuramadi. Kontrol gerekli. |")
                            print_fail("| Yazma korumasi sonrasi cihaz yeniden baglanti kuramadi. Kontrol gerekli. |")

                    else:
                        print_warning(" >> Upgrade basarisiz oldugundan Overlay Korumasi etkinlestirilmeyecek.")
                        ssh.close()
                    
                    print("Yazilimin sunuculara bilgi gondermesi bekleniyor")
                    tekrar_dene = 0
                    is_tekrar_baglanti = False
                    while tekrar_dene < 30:
                        tekrar_dene += 1
                        rs = requests.get("https://api.scadawatt.com/v2/scdTestDeviceInfo") # v2 olan local IP kontrolü yapar. v1 olan komple eski usül
                        cvp = json.loads(rs.text)
                        if("404" not in cvp.keys()):
                            for c in cvp["data"]:
                                if i["swd_mac"].upper() == c["swd_mac"].upper():
                                    is_tekrar_baglanti = True
                        time.sleep(1)

                    if is_tekrar_baglanti:
                        print_okgreen("Cihaz yeniden baglanti kurdu. Kullanima hazir.")
                    else:
                        print_fail("| Her sey yapildi ancak yazilim calismiyor olabilir. Kontrol gerekli. |")

                    print_warning("\nTEST TAMAMLANDI")
                    print_warning("\nDevam etmek icin sagdaki butona basiniz.")
                    while bc.getButtonState(1):
                        pass
                        
                    for k, v in bc.threadParams.items():
                        bc.threadParams[k] = False

                    for t in bc.blinkThreadList.values():
                        t.join()
                    #else:
                    #   print("Dosya kopyalanamadi.")   
        else:
            bc.blinkThreadStart(bc.led_baglanti, 0.1, 0)
            if("404" in cvp.keys()):
                bc.blinkThreadStart(bc.led_baglanti, 0.1, 1)
                print("60 sn icinde guncellenen test cihazi yok")
                time.sleep(0.5)
                bc.blinkThreadStart(bc.led_baglanti, 0.5, 0)
                time.sleep(5)

    except Exception as ex:
        #bc.blinkThreadStart(bc.led_program, 0.1, 0)  #ikinci aşama başlangıcı
        print_fail(str(ex))
        print_fail(traceback.format_exc())
    
    time.sleep(5)
