#プログラム機能：データ収集のおいて、FTPサーバで保存フォルダが新規作成され変更されていた場合に、自動的に収集パスと保存パスを変更する
#同時に新規保存ディレクトリを作成する
#2019年9月18日段階では本番運用テストは行っていません
#本番で使う際には設定ファイル等のパスは変更してくださいね、またバックアップも一応取りましょう

from ftplib import FTP
import os
import json
import time
from plyer import notification
import socket

socket.setdefaulttimeout(3.0)

#設定ファイルの取得
pwd = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='utf-8')
config_file = json.load(f)

#各サーバーについてのftp
def change_path():
    for i in config_file:

        def notification_app():
            notification.notify(
                title = '%s: パス変更'  % i,
                message = 'エラーが発生しました、確認してください。'
            )
            return None

        host = config_file[i]['host']
        user = config_file[i]['user']
        passwd = config_file[i]['passwd']
        remote_dir = config_file[i]['remote_dir']
        local_dir = config_file[i]['local_dir']

        try:
            if (i == "HPCS"):
                continue
            ftp_inf = FTP(host, user, passwd)
            #ftp側のパスの操作
            remote_path = os.path.normpath('%s/../' %remote_dir)
            re_remote_path = remote_path.replace('\\', '/') #パスをftpで使える形に変換する
            remote_list = ftp_inf.nlst(re_remote_path)[3:]
            #ローカル側のパスの操作
            local_path = config_file[i]['local_dir']
            re_local_path = os.path.normpath('%s/../' %local_path)
            local_list = [f.name for f in os.scandir(re_local_path)]
            #ftpとローカルの差分抽出
            diff_list = list(set(remote_list) - set(local_list)) #差分暫定
            #差分が存在した場合の処理を行う
            if diff_list == []:
                print("\n[%s]のディレクトリパスに変更はありません。" %i)
            else:
                print("\n[%sサーバー]に新規フォルダが作成されていたため、パスの書き換え、新規フォルダ作成を行います。" %i)
                #差分リストの文字列のみを抽出
                new_folder = diff_list[0]
                #新しいftpパスの作成
                new_remote_path0 = os.path.join(re_remote_path, new_folder)
                new_remote_path = new_remote_path0.replace('\\', '/')

                #新しいローカルパスの作成
                new_local_path0 = os.path.join(re_local_path, new_folder)
                new_local_path = new_local_path0.replace('\\', '/')

                #ディレクトリパスの書き換えを行う処理
                #ftpサーバーパスの書き換え
                with open(config_path, encoding='UTF-8') as f:
                    read_file = f.read()
                    re_remote = read_file.replace(remote_dir, new_remote_path + '/')
                with open(config_path, 'w', encoding='UTF-8') as f:
                    f.write(re_remote)

                #ローカルフォルダパスの書き換え
                with open(config_path, encoding='UTF-8') as f:
                    read_file = f.read()
                    re_local = read_file.replace(local_dir, new_local_path + '/')
                with open(config_path, 'w', encoding='UTF-8') as f:
                    f.write(re_local)

                #新規保存先となるローカルフォルダを作成する
                os.mkdir(new_local_path)

        except socket.timeout:
            print("\n[%sサーバー]にアクセスできませんでした。" %i)
            notification_app()
        except :
            print("\n%s: 予期せぬエラーが発生しました。" %i)
            notification_app()
    return None




# #ftpサーバーのディレクトリリストの表示
# remote_path3 = config_file['PSSP']['remote_dir']
# print(remote_path3)
# remote_list = server.nlst(remote_path)[3:]

# #ローカルディレクトリスト表示
# local_file = config_file['PSSP']['local_dir']
# local_list = [f.name for f in os.scandir(local_file)]

# #ディレクトリの差分抽出(ftp - local)
# diff_dir = list(set(remote_list) - set(local_list))

# #ftpのディレクトリパス指定(差分が存在したことがトリガーとなって処理されるようにしたい)

# middle_path ='/CF/LOGGING/LOG01/'
# for i in diff_dir:
#     diff_path = os.path.join(middle_path, i)

# #ディレクトリパスの書き換え(置換)を行う
# config = "C:/Users/b1635481/Desktop/config.json"

# # with open(config, encoding='UTF-8') as f:
# #     wfile = f.read() #読み込みファイルとして展開
# #     pssp ='F:/InfluxDB_csv_program/past_data/log_pssp/00000201'
# #     new_pssp = 'F:/InfluxDB_csv_program/past_data/log_pssp/00000101'

# #     data = wfile.replace(pssp, new_pssp)

# # with open(config, 'w', encoding='UTF-8') as f:
# #     f.write(data)


# remote_path1 = server.cwd(remote_path)
# remote = server.pwd()