import paramiko
import os
import requests
import json
from pathlib import Path
import sys
import RPi.GPIO as GPIO
import datetime
import time

def sshConnect(ip, username, password, port=22):
     try:
          ssh = paramiko.SSHClient()
          ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
          ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
          ssh.connect(ip, username=username,password=password)
          print("OK ... Connection success")
          return ssh
     except Exception as ex:
          print("Err ... Connection failed :", ex)
          return False


def copyCron(ssh, bc):
     try:
          ssh.exec_command("timedatectl set-ntp False")
          ssh.exec_command("timedatectl set-ntp True")
          sftp=ssh.open_sftp()
          sftp.put('/root/scd_tester/cron/tar.tar.gz', '/var/spool/cron/crontabs/tar.tar.gz')
          sftp.close()
          print("OK ... cron arsivi kopyalandi")
          komut = "cd /var/spool/cron/crontabs && tar -xvf tar.tar.gz && rm tar.tar.gz && service cron restart && systemctl restart cron"
          ssh.exec_command(komut)
          
          print("OK ... CronJobs")
          return True
     except Exception as ex:
          print("Err ... CronJobs :", ex)
          return False

def copyW5500ResetService(ssh):
     try:
          sftp=ssh.open_sftp()
          sftp.put('service/w5500_reset.service', '/etc/systemd/system/w5500_reset.service')
          sftp.put('service/w5500_reset.sh', '/w5500_reset.sh')
          sftp.close()
          komut = "chmod +x /w5500_reset.sh && systemctl daemon-reload && systemctl enable w5500_reset"
          ssh.exec_command(komut)
          print("OK ... copyW5500ResetService")
          return True
     except Exception as ex:
          print("Err ... copyW5500ResetService :", ex)
          return False
     
def copyRaspiConfigFile(ssh):
     try:
          sftp=ssh.open_sftp()
          sftp.put('service/raspi-config', '/usr/bin/raspi-config')
          sftp.close()
          print("OK ... copyRaspiConfigFile")
          return True
     except Exception as ex:
          print("Err ... copyRaspiConfigFile :", ex)
          return False
     
def copyHostsFile(ssh):
     try:
          sftp=ssh.open_sftp()
          sftp.put('service/hosts', '/etc/hosts')
          sftp.close()
          print("OK ... Hosts degistirildi")
          return True
     except Exception as ex:
          print("Err ... copyHostsFile :", ex)
          return False

def deleteAndDisableLogs(ssh):
     try:
          komut = "systemctl disable rsyslog && systemctl stop rsyslog && cd /var/log && rm *.1 -f && rm *.backup -f && rm *.log -f && rm *.gz -f  && rm /root/SCD_v1/log/*.log -f"
          stdin, stdout, stderr = ssh.exec_command(komut)
          exit_status = stdout.channel.recv_exit_status()
          stdout.channel.set_combine_stderr(True)
          if exit_status == 0:
               print("OK ... deleteAndDisableLogs")
               return True
          else:
               print("Err ... deleteAndDisableLogs")
               print("stdout : {0}\ncode : {1}".format(stdout.readlines(), exit_status))

               return False
     except Exception as ex:
          print("Err ... deleteAndDisableLogs :", ex)
          return False

retry = False
def upgradeSCD(ssh, version, bc, device):
     global retry
     try:
          bc.blinkThreadStart(bc.led_upgrade, 0.5, 0) #upgrade başlangıcı
          my_file = Path("/root/scd_tester/scdData/" + str(version) + "/" + str(version) + ".tar.gz")
          if my_file.is_file() is False:
               #tar.gz yok. Oluşturtalım
               komut = "cd /root/scd_tester/scdData/" + str(version) + " && tar -zcvf " + str(version) + ".tar.gz *"
               os.system(komut)
               print("Archive created")
          print("Archive uploading")
          #sıkıştırılmış hali var. Direk onu transfer edilim
          sftp=ssh.open_sftp()
          sftp.put("/root/scd_tester/scdData/" + str(version) + "/" + str(version) + ".tar.gz", '/root/SCD_v1/' + str(version) + '.tar.gz')
          print("Upload complated")
          sftp.close()
          print("Installation start . . .")
          komut = "rm -r /root/SCD_v1/log/*.log -f && rm -r exe.linux* -f && cd /root/SCD_v1 && mkdir log storage -p && tar -xvf " + str(version) + ".tar.gz && systemctl stop scadawatt && systemctl disable scadawatt && rm -r /lib/scadawatt* -f && rm /usr/bin/boxController -f && pip3 install pymodbustcp && python3 setup.py install && cd /root && mv /root/SCD_v1/build/exe.linux*/ /root/ && rm -r /root/SCD_v1/ -f && mv /root/exe.linux*/ /root/SCD_v1 && systemctl start scadawatt && systemctl enable scadawatt && exit"
          #if "swd_cpuModel" in device and device["swd_cpuModel"][4] == '7': #ARMv7 Processor rev 4 (v7l)
          #     print("ARMv7 detected")
          #     komut = "rm -r /root/SCD_v1/log/*.log -f && rm -r exe.linux-armv7l-3.7/ -f && cd /root/SCD_v1 && mkdir log storage -p && tar -xvf " + str(version) + ".tar.gz && systemctl stop scadawatt && systemctl disable scadawatt && rm -r /lib/scadawatt* -f && rm /usr/bin/boxController -f && python3 setup.py install && cd /root && mv /root/SCD_v1/build/exe.linux-armv7l-3.7/ /root/ && rm -r /root/SCD_v1/ -f && mv /root/exe.linux-armv7l-3.7/ /root/SCD_v1 && systemctl start scadawatt && systemctl enable scadawatt && exit"
          stdin, stdout, stderr = ssh.exec_command(komut)
          exit_status = stdout.channel.recv_exit_status()
          if exit_status == 0:
               bc.turnOn(bc.led_upgrade)
               print ("OK ... Upgrade complate :", str(version/100))
               return True
          else:
               if retry == False:
                    retry = True
                    print("Upgrade basarisiz oldu fakat yeniden denenecek. Cihaz 4 cekirdekli olabilir. Son kez birdaha deneniyor")
                    device["swd_cpuModel"] = "armv7"
                    return upgradeSCD(ssh, version, bc, device)
               else:
                    bc.blinkThreadStart(bc.led_upgrade, 0.1, 0) #cron update fail
                    print("Err ... Upgrade failed :", exit_status)
                    return False
     except Exception as ex:
          print(ex)
          print("connect.py 116 | device =", device)
          return False

def inputTest():
     GPIOList = [16,6,12,13,19,5]
     for g in GPIOList:
        GPIO.setup(g, GPIO.IN)
     while 1:
        print(datetime.datetime.now())
        for g in GPIOList:
            print(g, "=>", GPIO.input(g))
        print(10*"-")
        time.sleep(1)


def start(ssh, bc, device, which=None):

     target_version = 247
     ret = [None, None, None, None, None, None]
     if which is None or which == "update":
          ret[0] = (copyW5500ResetService(ssh))                 #0
          ret[1] = (copyCron(ssh, bc))                          #1
          ret[3] = (deleteAndDisableLogs(ssh))                  #3
          ret[4] = (copyRaspiConfigFile(ssh))                   #4
          ret[5] = (copyHostsFile(ssh))
     if which is None or which == "upgrade":
          ret[2] = (upgradeSCD(ssh, target_version, bc, device))        #2

     if which == "input":
          ret.append(inputTest())

     print("connect.py closing")

     return ret