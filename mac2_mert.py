import subprocess
import argparse
import sys


def check_is_rclocal_changed():
    isaret = "ip link set dev eth0 address"
    with open("/etc/rc.local", 'r', encoding='utf-8') as dosya:
        satirlar = dosya.readlines()
        for s in satirlar:
            if s.strip() == isaret:
                return True
        return False

def recreate_rclocal(mac):
    satirlar = []
    satirlar.append("#!/bin/sh -e\n")
    satirlar.append("#\n")
    satirlar.append("# Bu dosya ScadaWatt Sistem Yöneticisi tarafından oluşturulmuştur.\n")
    satirlar.append("#\n")
    satirlar.append("# Müdehale etmemeniz önerilir\n")
    satirlar.append("#\n")
    satirlar.append("ip link set dev eth0 down\n")
    satirlar.append("ip link set dev eth0 address {0}\n".format(mac))
    satirlar.append("ip link set dev eth0 up\n")
    satirlar.append("systemctl restart dhcpcd.service\n")
    satirlar.append("# Print the IP address\n")
    satirlar.append("_IP=$(hostname -I) || true\n")
    satirlar.append('if [ "$_IP" ]; then\n')
    satirlar.append('  printf "My IP address is %s\\n" "$_IP"\n')
    satirlar.append("fi\n")
    satirlar.append("exit 0\n")
    satirlar.append("")
    with open("/etc/rc.local", 'w', encoding='utf-8') as dosya:
        dosya.writelines(satirlar)
    return True


def change_rclocal(mac):
    if check_is_rclocal_changed() is False:
        eklenecek_satir = 0
        eklenecek_satir_bulundu = False
        with open("/etc/rc.local", 'r', encoding='utf-8') as dosya:
            satirlar = dosya.readlines()
            eklenecek_satir = 0
            for s in satirlar:
                if s.strip() == "# By default this script does nothing.":
                    #print("ilgili satir bulundu. Satir :", eklenecek_satir)
                    eklenecek_satir_bulundu = True
                    break
                eklenecek_satir += 1

            if eklenecek_satir_bulundu is False:
                eklenecek_satir = 0
                for s in satirlar:
                    #print("eklenecek satir bulunamadi. Son satir aranacak.")
                    if s.strip() == "exit 0":
                        #print("Son satir bulundu. Satir :", eklenecek_satir)
                        eklenecek_satir_bulundu = True
                        break
                    eklenecek_satir += 1

        if eklenecek_satir_bulundu:
            eklenecek_satir += 1
            satirlar.insert(eklenecek_satir, "systemctl restart dhcpcd.service" + '\n')
            satirlar.insert(eklenecek_satir, "ip link set dev eth0 up" + '\n')
            satirlar.insert(eklenecek_satir, "ip link set dev eth0 address " + mac + '\n')
            satirlar.insert(eklenecek_satir, "ip link set dev eth0 down" + '\n')

            with open("/etc/rc.local", 'w', encoding='utf-8') as dosya:
                dosya.writelines(satirlar)

            return True
        else:
            return False
    else:
        print("! rc.local zaten degistirilmis")
        return True
    
def disable_dhcpcd_service():
    prc1 = subprocess.run(["systemctl", "disable", "dhcpcd.service"], capture_output=True)
    answer = prc1.stdout.decode()
    code = prc1.returncode
    if code == 0:
        return True
    else:
        print("! disable_dhcpcd_service :", code, answer)
        return False

def check_is_staticIP():
    
    static_ip = None
    static_netmask = None
    static_gateway = None
    static_dns = ""

    isaret = "iface eth0 inet static"
    with open("/etc/network/interfaces", 'r', encoding='utf-8') as dosya:
        satirlar = dosya.readlines()
        for s in satirlar:
            s = s.strip()
            if s.startswith("address"):
                static_ip = s.split()[1]
            elif s.startswith("netmask"):
                static_netmask = s.split()[1]
            elif s.startswith("gateway"):
                static_gateway = s.split()[1]
            elif s.startswith("dns-nameservers"):
                static_dns += " " + s.split()[1]
        static_dns = static_dns.lstrip()
        
    return static_ip, static_netmask, static_gateway, static_dns
    
def clear_interfaces_file():
    son_olacak_satir = 0
    son_olacak_satir_bulundu = False
    isaret = "# Network interfaces"
    with open("/etc/network/interfaces", 'r', encoding='utf-8') as dosya:
        satirlar = dosya.readlines()
    for s in satirlar:
        if s.strip() == isaret:
            son_olacak_satir_bulundu = True
            break
        son_olacak_satir += 1

    if son_olacak_satir_bulundu:
        satirlar = satirlar[0:son_olacak_satir+1]

        with open("/etc/network/interfaces", 'w', encoding='utf-8') as dosya:
            dosya.writelines(satirlar)
        return True
    else:
        return False
    
def check_dhcpcdconfig_isalready_changed():
    # DHCPCD dosyasında zaten bir statik IP bulunuyor olabilir.
    # Bu durumda, ikinci defa çalıştırılmış olacak olmalı. Interfaces dosyası boş olduğundan
    # DHCPCD için otomatik IP konfigurasyonuna geçirmeye çalışır. Bu yüzden önce bir kontrol edelim
    
    static_ip = None
    static_subnet = None
    static_gateway = None
    static_dns = None

    with open("/etc/dhcpcd.conf", 'r', encoding='utf-8') as dosya:
        satirlar = dosya.readlines()

        temp_eth0_basladi = False
        
        for s in satirlar:
            s = s.strip()
            if s.startswith("interface eth0"):
                temp_eth0_basladi = True
            elif s.startswith("static ip_address") and temp_eth0_basladi:
                s = s.replace("=", " ")
                static_ip = s.split()[2]
            elif s.startswith("static routers") and temp_eth0_basladi:
                s = s.replace("=", " ")
                static_gateway = s.split()[2]
            elif s.startswith("static domain_name_servers") and temp_eth0_basladi:
                s = s.replace("=", " ")
                static_dns = s.split()[2]            
            else:
                temp_eth0_basladi = False

            if static_ip is not None and static_gateway is not None and static_subnet is not None and static_dns is not None:
                break

        if static_ip is not None:
            static_subnet = int(static_ip.split("/")[1])
            static_ip = static_ip.split("/")[0]
    
    return static_ip, static_subnet, static_gateway, static_dns


def recreate_dhcpcdconfig(mac, static_ip = None, static_subnet = None, static_gateway = None, static_dns = None):
    
    satirlar = []
    satirlar.append("hostname 'scadawatt-{0}'\n".format(mac.split(":")[4] + mac.split(":")[5]))
    satirlar.append("clientid '{0}'\n".format(mac))
    satirlar.append("persistent\n")
    satirlar.append("option rapid_commit\n")
    satirlar.append("option domain_name_servers, domain_name, domain_search, host_name\n")
    satirlar.append("option classless_static_routes\n")
    satirlar.append("option interface_mtu\n")
    satirlar.append("require dhcp_server_identifier\n")
    satirlar.append("slaac private\n")
    satirlar.append("interface eth0\n")

    
    if static_ip is not None and static_subnet is not None and static_gateway is not None and static_dns is not None:
        # static IP yapilandirmasi da eklenecek
        satirlar.append("\n")

        satirlar.append("static ip_address={0}/{1}\n".format(static_ip, static_subnet))
        satirlar.append("static routers={0}\n".format(static_gateway))
        satirlar.append("static domain_name_servers={0}\n".format(static_dns))
    else:
        # Dinamik IP - 10.241.241.x ağından talep et
        satirlar.append("inform 10.241.241.0/24\n")
        satirlar.append("ipv4only\n")


    with open("/etc/dhcpcd.conf", 'w', encoding='utf-8') as dosya:
        dosya.writelines(satirlar)
    return True

def daemon_reload():
    prc1 = subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
    answer = prc1.stdout.decode()
    code = prc1.returncode
    if code == 0:
        return True
    else:
        print("! daemon_reload :", code, answer)
        return False

def apply_mac_changes():
    prc1 = subprocess.run(["sh", "/etc/rc.local"], capture_output=True)
    answer = prc1.stdout.decode()
    code = prc1.returncode
    if code == 0:
        return True
    else:
        print("! apply_mac_changes :", code, answer)
        return False

parser = argparse.ArgumentParser(description='Bu uygulama bazı işler yapıyor.')
parser.add_argument('-m', '--mac', type=str, default=None, required=True, help="Atanacak MAC adresi")
parser.add_argument('-i', '--ip', type=str, default=None, required=False, help="Atanacak statik IP adresi")
parser.add_argument('-s', '--subnet', type=str, default=None, required=False, help="Atanacak statik subnet numarası")
parser.add_argument('-g', '--gateway', type=str, default=None, required=False, help="Atanacak statik gateway adresi")
parser.add_argument('-d', '--dns', type=str, default=None, required=False, help="Atanacak statik DNS adresi")
parser.add_argument('-r', '--dhcpreset', action='store_true', default=False, required=False, help="Ethernet arayüzünü DHCP yapar")

args = parser.parse_args()

hedef_mac = "aa:bb:cc:dd:ee:ff"
hedef_ip = None
hedef_subnet = None
hedef_gateway = None
hedef_dns = None

args.mac = args.mac.lower()
args.mac = args.mac.replace("-", ":")

if len(args.mac) == 17:
    hedef_mac = args.mac[12:]
elif len(args.mac) != 4:
    print("! MAC adresi hatali. Son haneyi bitişik gönderin veya TAM MAC adresini yazin")
    sys.exit(1)

if not args.dhcpreset:
    temp_ip_err_counter = 0
    if args.ip is None:
        temp_ip_err_counter += 1
    if args.subnet is None or args.subnet.isdigit() is False:
        temp_ip_err_counter += 1
        if args.subnet is not None:
            print("Hedef subnet sayi olarak girilmeli. Orn: 20,21,22,23,24 vb.")
    if args.gateway is None:
        temp_ip_err_counter += 1
    if args.dns is None:
        temp_ip_err_counter += 1

    if temp_ip_err_counter not in (0, 4):
        print("! Statik IP parametrelerinin hepsini gönderin veya hiç birini kullanmayın!")
        sys.exit(1)

    elif temp_ip_err_counter == 0:
        hedef_ip = args.ip
        hedef_subnet = int(args.subnet)
        hedef_gateway = args.gateway
        hedef_dns = args.dns
else:
    print("Statik adres yapilandirmasi varsa bile iptal edilecek, DHCP etkinlestirilecek.")
    hedef_ip = None
    hedef_subnet = None
    hedef_gateway = None
    hedef_dns = None

if len(args.mac) == 4:
    hedef_mac = "5c:ad:a3:a7:"
    hedef_mac += args.mac[0:2] + ":" + args.mac[2:4]
elif len(args.mac) == 17:
    hedef_mac = args.mac
else:
    print("! MAC parametresi hatalı kullanıldı. MAC adresinin son 4 hanesini bitişik yazın veya MAC adresini aralarında IKI NOKTA veya TIRNAK olacak şekilde tam olarak yazın.")
    sys.exit(0)

print("Uygulanacak MAC Adresi\t\t: {0}".format(hedef_mac))

if hedef_ip is None:

    islem_check_is_staticIP = check_is_staticIP()
    print("islem_check_is_staticIP\t\t:", islem_check_is_staticIP)
    if islem_check_is_staticIP[0] is not None:
        islem_check_is_staticIP = list(islem_check_is_staticIP)
        islem_check_is_staticIP[1] = sum(bin(int(x)).count('1') for x in islem_check_is_staticIP[1].split('.'))

    islem_check_dhcpcdconfig_isalready_changed = check_dhcpcdconfig_isalready_changed()
    print("islem_check_dhcpcd_changed\t:", islem_check_dhcpcdconfig_isalready_changed)
    temp_any_error = False
    if islem_check_dhcpcdconfig_isalready_changed[0] is not None and islem_check_is_staticIP[0] is not None:
        print("\nDHCPCD.conf dosyasinda statik IP mevcut. Iki dosyada da statik IP mevcut. Kontrol edilecek.\n")
        if islem_check_dhcpcdconfig_isalready_changed[0] != islem_check_is_staticIP[0]:
            print("DHCPCD.conf statik IP  !=  interfaces statik IP", islem_check_dhcpcdconfig_isalready_changed[0], islem_check_is_staticIP[0])
            temp_any_error = True
        if islem_check_dhcpcdconfig_isalready_changed[1] != islem_check_is_staticIP[1]:
            print("DHCPCD.conf subnet  !=  interfaces subnet", islem_check_dhcpcdconfig_isalready_changed[1], islem_check_is_staticIP[1])
            temp_any_error = True
        if islem_check_dhcpcdconfig_isalready_changed[2] != islem_check_is_staticIP[2]:
            print("DHCPCD.conf gateway  !=  interfaces gateway", islem_check_dhcpcdconfig_isalready_changed[2], islem_check_is_staticIP[2])
            temp_any_error = True

        if temp_any_error:
            print("! ! ! Interfaces dosyasindaki statik IP ayari ile DHCPCD dosyasindaki statik IP ayarlari tutarsiz. Yapilandirmaya devam edilmeyecek.")
            print("interfaces  :", islem_check_is_staticIP)
            print("dhcpcd.conf :", islem_check_dhcpcdconfig_isalready_changed)
            sys.exit(1)

    elif islem_check_dhcpcdconfig_isalready_changed[0] is not None and args.dhcpreset is False:
        # DHCPCD conf dosyasinda IP saklanıyor. resetleme de olmadığı için saklamaya devam edelim...
        print("DHCPCD.conf dosyasindaki IP ayarlari aynen korunacak.")
        islem_check_is_staticIP = islem_check_dhcpcdconfig_isalready_changed
        
    
else:
    islem_check_is_staticIP = [hedef_ip, hedef_subnet, hedef_gateway, hedef_dns]

islem_recreate_rclocal = recreate_rclocal(hedef_mac)
print("islem_recreate_rclocal\t\t:", islem_recreate_rclocal)

islem_clear_interfaces_file = clear_interfaces_file()
print("islem_clear_interfaces_file\t:", islem_clear_interfaces_file)

islem_recreate_dhcpcdconfig = recreate_dhcpcdconfig(hedef_mac, islem_check_is_staticIP[0], islem_check_is_staticIP[1], islem_check_is_staticIP[2], islem_check_is_staticIP[3])
print("islem_recreate_dhcpcdconfig\t:", islem_recreate_dhcpcdconfig)

islem_disable_dhcpcd_service = disable_dhcpcd_service()
print("islem_disable_dhcpcd_service\t:", islem_disable_dhcpcd_service)

islem_daemon_reload = daemon_reload()
print("islem_daemon_reload\t\t:", islem_daemon_reload)

islem_apply_mac_changes = apply_mac_changes()
print("islem_apply_mac_changes\t\t:", islem_apply_mac_changes)

print("\nBye..\n")