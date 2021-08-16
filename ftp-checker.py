from datetime import datetime
from ftplib import FTP
import time
import os

ftp = FTP("63.33.239.182")

def connect():
    ftp.login("pi", "pi")
    ftp.cwd("files")
    ftp.set_pasv(False)

def getMs(dateTime):
    return datetime.strptime(dateTime,'%d.%m.%Y %H:%M:%S').timestamp() * 1000

def current():
    return round(time.time() * 1000)

def check():
    try:
        files = ftp.nlst()
        currentTime = current()
        
        for i in files:
            # print(i)
            modifiedTime = ftp.sendcmd('MDTM ' + i)[4:].strip()
            splitted = list(modifiedTime) #20210816121029
            dateString = splitted[6] + splitted[7]+ "." + splitted[4] + splitted[5] + "." +  splitted[0] + splitted[1] +  splitted[2] + splitted[3]+ " "+ splitted[8] + splitted[9]+ ":"+ splitted[10] + splitted[11]+ ":"+ splitted[12] + splitted[13]

            diff = currentTime - getMs(dateString) # 10805199 10877240.0
           
            if diff < 12890832:
                if not os.path.isfile('./' + i):
                    ftp.retrbinary("RETR " + i, open(i, 'wb').write)
                    print("İNDİRİLECEK DOSYA:")
                    print(i)
    except:
        connect()
        check()

while True:
    check()
    time.sleep(1)