import subprocess
import os
import time


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

print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}.SCADAWATT TEST    \t\t\t\t-----\t\t\t\t    SCADAWATT TEST.{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.FAIL}..SCADAWATT TEST   \t\t\t\t-----\t\t\t\t   SCADAWATT TEST..{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.WARNING}...SCADAWATT TEST  \t\t\t\t-----\t\t\t\t  SCADAWATT TEST...{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.OKCYAN}....SCADAWATT TEST \t\t\t\t-----\t\t\t\t SCADAWATT TEST....{bcolors.ENDC}")
print(f"""{bcolors.BOLD}{bcolors.OKGREEN}
\t\t\t\t\t\t\t\t\t                                   $$\                                    $$\     $$\                
\t\t\t\t\t\t\t\t\t                                   $$ |                                   $$ |    $$ |           
\t\t\t\t\t\t\t\t\t $$$$$$$\  $$$$$$$\ $$$$$$\   $$$$$$$ | $$$$$$\  $$\  $$\  $$\  $$$$$$\ $$$$$$\ $$$$$$\       
\t\t\t\t\t\t\t\t\t$$  _____|$$  _____|\____$$\ $$  __$$ | \____$$\ $$ | $$ | $$ | \____$$\\_$$  _|\_$$  _|     
\t\t\t\t\t\t\t\t\t\$$$$$$\  $$ /      $$$$$$$ |$$ /  $$ | $$$$$$$ |$$ | $$ | $$ | $$$$$$$ | $$ |    $$ |       
\t\t\t\t\t\t\t\t\t \____$$\ $$ |     $$  __$$ |$$ |  $$ |$$  __$$ |$$ | $$ | $$ |$$  __$$ | $$ |$$\ $$ |$$\ 
\t\t\t\t\t\t\t\t\t$$$$$$$  |\$$$$$$$\\$$$$$$$ |\$$$$$$$ |\$$$$$$$ |\$$$$$\$$$$  |\$$$$$$$ | \$$$$  |\$$$$  |
\t\t\t\t\t\t\t\t\t\_______/  \_______|\_______| \_______| \_______| \_____\____/  \_______|  \____/  \____/                                                                                                                                        
{bcolors.ENDC}""")
# print(f"\t\t\t{bcolors.BOLD}{bcolors.OKGREEN}.....SCADAWATT TEST-SCADAWATT TEST.{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.OKCYAN}....SCADAWATT TEST \t\t\t\t-----\t\t\t\t SCADAWATT TEST....{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.WARNING}...SCADAWATT TEST  \t\t\t\t-----\t\t\t\t  SCADAWATT TEST...{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}{bcolors.FAIL}..SCADAWATT TEST   \t\t\t\t-----\t\t\t\t   SCADAWATT TEST..{bcolors.ENDC}")
print(f"\t\t\t\t\t\t\t\t\t{bcolors.BOLD}.SCADAWATT TEST    \t\t\t\t-----\t\t\t\t    SCADAWATT TEST.{bcolors.ENDC}")


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



mac = "7151"
last4 = mac

if len(mac) == 4:
    hedef_mac = "5c:ad:a3:a7:"
    hedef_mac += mac[0:2] + ":" + mac[2:4]
elif len(mac) == 17:
    hedef_mac = mac




def run_command(command):
    try:
        # Using os.popen which allows capturing output
        with os.popen(command) as proc:
            output = proc.read().strip()
        return output
    except Exception as e:
        print(f"Error executing command: {e}")
        return None

# def run_command(command, shell=False):
#     try:
#         if shell and isinstance(command, str):
#             command = command.split()
        
#         result = subprocess.run(
#             command, 
#             shell=shell, 
#             check=True, 
#             text=True, 
#             capture_output=True
#         )
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print(f"Error executing command: {e}")
#         print(f"Error output: {e.stderr}")
#         return None

def disable_overlay():
    print("Yazma koruması kapatıldı. Yeniden başlatılıyor...")
    run_command("raspi-config --disable-overlayfs && reboot")

def set_password(last4):
    try:
        run_command('echo "root:scd_{0}" | chpasswd'.format(last4.lower()))
        run_command('echo "pi:Sc@d@w@++" | chpasswd')
        print_okgreen("OK ... Root Password Updated : scd_{0}".format(last4.lower()))
        print_okgreen("OK ... Pi Password Updated : Sc@d@w@++")
    except Exception as ex:
        print_fail("setRootPassword : {0}".format(str(ex)))
        print_fail("setPiPassword : {0}".format(str(ex)))
        return False


def set_hostname(last4):
    try:
        run_command("hostnamectl set-hostname scadawatt-" + last4.lower())
        print_okgreen("OK ... Device hostname updated : scadawatt-{0}".format(last4.lower()))
    except Exception as ex:
        print_fail("setHostname : {0}".format(str(ex)))
        return False

def set_mac_address(last4):
    try:
        file = ['# interfaces(5) file used by ifup(8) and ifdown(8)\n', '\n', '# Please note that this file is written to be used with dhcpcd\n', "# For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'\n", '\n', '# Include files from /etc/network/interfaces.d:\n', 'source-directory /etc/network/interfaces.d\n', '\n', '# Network interfaces\n', 'auto eth0\n', 'allow-hotplug eth0\n', 'iface eth0 inet dhcp\n']
        interfaces = open("/etc/network/interfaces", "w")
        for line in file:
            interfaces.write(line)
        interfaces.write("hwaddress ether 5c:ad:a3:a7:{0}:{1}\n".format(last4[0:2], last4[2:4]))
        interfaces.close()
        print_okgreen("OK ... setMacAddress : 5c:ad:a3:a7:{0}:{1}".format(last4[0:2], last4[2:4]))
        return True
    except Exception as ex:
        print_fail("setMacAddress : {0}".format(str(ex)))
        return False

# disableoverlay şuanki test cihazı için gerek yok zaten kapalı
# disable_overlay()

# set hostname (gerek yok zaten ayarlı)
# set_hostname(last4)

# set macaddress (gerek yok zaten ayarlı)
# set_mac_address(last4)

# set password gerek yok zaten ayarlı()
# set_password(last4)

# send vpn profile (vpn dosyası zaten içinde gerek yok)

# test kurulum dosyalarını sıkıştır (şuan gerek yok çünkü sıkıştırılmamış halini direkt kullanıyoruz)
# run_command("cd /root/test_kurulum && tar -zcvf /root/test_kurulum.tar.gz *")

# log dosyalarını ve exe.linux dosyalarını sil
# run_command("rm -r /root/SCD_v1/log/*.log -f")
# run_command("rm -r exe.linux* -f")

#log ve storage dosyalarını tekrar oluştur
run_command("cd /root/SCD_v1 && mkdir log storage -p")
print_success("OK ... log and storage created")

#sıkıştırılmış versiyon dosyasını çıkart (çıkartmamıza gerek yok çünkü elimizle zaten zipsiz halini atıyoruz)
# run_command("tar -xvf " + str(version) + ".tar.gz")

#service'i durdur
run_command("systemctl stop scadawatt")
run_command("systemctl disable scadawatt")
print_success("OK ... Scadawatt service stop and disable")

#eski dosyaları sil
run_command("rm -r /lib/scadawatt* -f")
run_command("rm /usr/bin/boxController -f")
print_success("OK ... old files removed")

#pymodbustcp kur
run_command("cd /root/test_kurulum/testversion && pip3 install pymodbustcp && python3 setup.py install")
print_success("OK ... pymodbustcp installation and setup.py started")

#yeni dosyaları kopyala
run_command("mv /root/test_kurulum/testversion/build/exe.linux*/ /root/")
print_success("OK ... new files moved to root")
# run_command("mv /root/SCD_v1/build/exe.linux*/ /root/")
run_command("rm -r /root/SCD_v1/ -f")
run_command("mv /root/exe.linux*/ /root/SCD_v1")
print_success("OK ... new files copied from root to SCD_v1")

#service'i başlat
run_command("systemctl start scadawatt")
run_command("systemctl enable scadawatt")
print_success("OK ... Scadawatt service started and enabled")


run_command("exit")
