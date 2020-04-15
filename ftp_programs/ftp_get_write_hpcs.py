from ftp_get_write import *
import configparser
from datetime import datetime
import time
import socket
import json
import os

# Set TimeoutError default time
socket.setdefaulttimeout(5.0)

# [JSON config informatino]
pwd = os.path.normpath('%s/../config_file' % __file__)
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)

# Function of FTP to HPCS
def hpcs_get():
  HPCS_host = config_file["HPCS"]["host"]
  HPCS_user = config_file["HPCS"]["user"]
  HPCS_passwd = config_file["HPCS"]["passwd"]
  HPCS_remote_file = datetime.now().strftime("%Y/%m/%d").replace("/", "-") + ".csv"
  HPCS_local_file = config_file["HPCS"]["local_file"]
  try:
    print('\n[HPCS]')
    HPCS_client = FTP_KIT(host=HPCS_host, user=HPCS_user, passwd=HPCS_passwd, remote_file=HPCS_remote_file, local_file=HPCS_local_file)
    HPCS_client.ftp_get()
  except error_perm:
    print('%s: %s 保存する対象のパスを確認してください。' % (HPCS_host, HPCS_remote_file))
  except FileNotFoundError:
    print('%s: %s 保存するパスが間違っています。' % (HPCS_host, HPCS_local_file))
  except socket.gaierror:
    print('%s: 接続出来ませんでした。' % HPCS_host)
  except socket.timeout:
    print('%s: タイムアウトでした。' % HPCS_host)
  except socket.gaierror:
    print('%s に接続出来ませんでした。' % HPCS_host)

if __name__ == "__main__":
    hpcs_get()