#プログラム機能：FTPサーバーに保存されている昨日までのデータをサーバーごとに一括収集するプログラム

import os
import socket
from ftplib import FTP
from distutils.util import strtobool
import time
import json
from plyer import notification
import ftp_ch_config
import error_mail

#モジュールのタイムアウト設定
socket.setdefaulttimeout(5.0)

#ストップウォッチ
def stopwatch(func):
  def wrapper(*args, **kwargs):
    print('処理を開始します。')
    start = time.time()
    func(*args, **kwargs)
    total_time = time.time() - start
    print('処理を終了しました。トータルタイムは:{0}'.format(total_time)+"[sec]です。")
  return wrapper

#外部にある設定ファイル情報の読み込み
pwd = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)

#パスを変更するプログラムを外部から読みだし、実行
ftp_ch_config.change_path()

#サーバー名を保存するエラーリスト
Error_server_list = []

#メインのプログラム
for i in config_file:

    #エラーが発生した際の通知処理
    def notification_app():
      notification.notify(
        title = '%s: 過去データ取得'  % i,
        message = 'エラーが発生しました、確認してください。'
      )
      return None

    switch = strtobool(config_file[i]["switch"])
    host = config_file[i]["host"]
    user = config_file[i]["user"]
    passwd = config_file[i]["passwd"]
    remote_dir = config_file[i]["remote_dir"]
    local_dir = config_file[i]["local_dir"]

    try:

        if switch == 0:
            print('%s がFalseになっています。' % host)
            break

        print ('\n[%s]' %i)

        inf = FTP(host, user, passwd)

        #HPCS以外のFTPサーバーとローカルの差分を抽出
        def diff_local_remote(inf, remote_dir, local_dir):
            local_list = [f.name for f in os.scandir(local_dir)]
            remote_list = inf.nlst(remote_dir)[3:]
            diff_file_list =set(remote_list) - set(local_list)
            return list(diff_file_list)
        
        #HPCSのFTPサーバーとローカルの差分を抽出
        def diff_local_remote_hpcs(inf, remote_dir, local_dir):
            local_list = [f.name for f in os.scandir(local_dir)]
            remote_list = inf.nlst(remote_dir)
            diff_file_list =set(remote_list) - set(local_list)
            return list(diff_file_list)
        @stopwatch
        def ftp_past_get_write(inf, remote_dir, local_dir):
            for i in diff_local_remote(inf, remote_dir, local_dir):
                get_time = time.time()
                with open(local_dir + i, 'wb') as f:
                    inf.retrbinary('RETR %s' % '{0}'.format(remote_dir + i), f.write)
                    print(i + "done")
                print('処理時間は%s [sec]\n' % (time.time() - get_time))
            return None
        @stopwatch
        def ftp_past_get_write_hpcs(inf, remote_dir, local_dir):
            for i in diff_local_remote_hpcs(inf, remote_dir, local_dir):
                get_time = time.time()
                with open(local_dir + i, 'wb') as f:
                    inf.retrbinary('RETR %s' % '{0}'.format(remote_dir + i), f.write)
                    print(i + "done")
                print('処理時間は%s [sec]\n' % (time.time() - get_time))
            return None

        if i == "HPCS":
            ftp_past_get_write_hpcs(inf, remote_dir, local_dir)
        else:
            ftp_past_get_write(inf, remote_dir, local_dir)
    except socket.timeout:
        print("タイムアウト：[%s]サーバーにアクセスできませんでした" %i)
        Error_server_list.append(i)
        notification_app()
    except:
        print("想定外のエラーが発生しました。")
        Error_server_list.append(i)
        notification_app()

#エラーメール送信用の設定ファイル読み込み
pwd = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd, 'error_mail.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)

#設定ファイル情報の抽出
from_addr = config_file['SMTP']['from_addr']
to_addrs = config_file['SMTP']['to_addrs']
server_domain = config_file['SMTP']['server_domain']
server_port = config_file['SMTP']['server_port']
message = config_file['SMTP']['message']
subject = config_file['SMTP']['subject']

error_mail.send_error_email(from_addr, to_addrs, server_domain, server_port, subject, message, Error_server_list)