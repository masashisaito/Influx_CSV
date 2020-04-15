from ftplib import FTP, error_perm
import socket
import time

# 処理時間計測のためのデコレータ
def stopwatch(func):
  def wrapper(*args, **kwargs):
    print('処理を開始します。')
    start = time.time()
    func(*args, **kwargs)
    total_time = time.time() - start
    print('処理を終了しました。トータルタイムは:{0}'.format(total_time)+"[sec]です。")
  return wrapper

@stopwatch
# ftpしてファイルを取得する関数
def ftp_get(host, filename):
  with open('./logging_now/hpcs.csv', 'wb') as f:
    print('getting %s' % filename)
    host.retrbinary('RETR %s' % filename, f.write)
    print("hpcs.csv done")


class FTP_KIT(FTP):
  def __init__(self, host=None, switch=True, user=None, passwd=None, remote_file=None, local_file=None):
    # super関数は2系3系, 違う
    super().__init__(host, user, passwd)
    self.switch = switch
    self.remote_file = remote_file
    self.local_file = local_file
  def ftp_get(self):
    try:
      if self.switch == 0:
        print('%s がFalseになっています。' % self.host)
      else:
        with open(self.local_file, 'wb') as f:
          self.retrbinary('RETR %s' % self.remote_file, f.write)
          print('%s done' % self.remote_file)
          print('Getting Success!!')
    except socket.gaierror:
      return print('%s に接続出来ませんでした。' % self.host)

if __name__ == "__main__":
  client = FTP_KIT(
    switch=True,
    host='bb-dl.ihc-in.kanazawa-it.ac.jp',
    user=' ',
    passwd=' ',
    remote_file='LOGGING/LOG01/LOG01.CSV',
    local_file='logging_now/biomus.csv'
    )
  client.ftp_get()


# For Example...
# filename = '2019-02-01.csv'
# hpcs = FTP(host="172.24.7.233", user='hpcs01', passwd='15507')

# ftp_get(hpcs, filename)