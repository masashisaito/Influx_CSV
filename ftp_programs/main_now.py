from ftp_get_write import *
from ftp_get_write_hpcs import hpcs_get
from configparser import ConfigParser
import os
import socket
from distutils.util import strtobool
import json
from plyer import notification


# Set TimeoutError default time
socket.setdefaulttimeout(5.0)

#[config.json informations]
pwd = os.path.normpath('%s/../config_file' % __file__) #実行中のスクリプトのファイル名を取得している
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)

# All server list
# server = config.sections() #利用できるセクションのリストを返す

def main_ftp():
  for svs in config_file:
    def notification_app():
      notification.notify(
        title = '%s: 現在データ取得'  % svs,
        message = 'エラーが発生しました、確認してください。'
      )
      return None
    try:
      switch = strtobool(config_file[svs]["switch"])
      host = config_file[svs]["host"]
      user = config_file[svs]["user"]
      passwd = config_file[svs]["passwd"]
      remote_file = config_file[svs]["remote_file"]
      local_file = config_file[svs]["local_file"]
      try:
        if svs == "HPCS":
          hpcs_get()
          continue
        print('\n[%s]' % svs)
        client = FTP_KIT(switch=switch, host=host, user=user, passwd=passwd, remote_file=remote_file, local_file=local_file)
        client.ftp_get()
      except error_perm:
        print('%s: %s 保存する対象のパスを確認してください。' % (host,remote_file))
        notification_app()
      except FileNotFoundError:
        print('%s: %s 保存するパスが間違っています。' % (host,local_file))
        notification_app()
      except socket.gaierror:
        print('%s: 接続出来ませんでした。' % host)
        notification_app()
      except socket.timeout:
        print('%s: タイムアウトでした。' % host)
        notification_app()
    except IndexError:
      print("[%s] 内で入力情報が欠損しています。" % svs)
      notification_app()

main_ftp()