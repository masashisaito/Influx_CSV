import os
import smtplib
from email.mime.text import MIMEText
import json
from pathlib import Path
import time
import error_mail

def send_error_email(from_addr, to_addrs, server_domain, server_port, subject, message, Error_server_list):

    error_server = str(Error_server_list).replace("'", "")

    error_message = '%s' %(error_server) + message

    msg = MIMEText(error_message, 'plain')
    msg['Subject'] = subject
    server = smtplib.SMTP(server_domain, server_port)

    if Error_server_list != []:
        #logファイルの有無の確認
        log_path = os.path.normpath('%s/../time_logs.txt' %__file__)
        if os.path.exists(log_path):
            #logファイルが存在する場合の処理
            now_time = time.time()
            with open(log_path, 'r', newline='', encoding='UTF-8') as r:
                last_time = r.readlines()[-1]
            total_time = now_time - float(last_time)
            #エラーが発生して8時間が経過していた場合にメールを送信する
            if total_time >= 28800:
                server.send_message(msg, from_addr, to_addrs)
                with open(log_path, 'a', newline='', encoding='UTF-8') as w:
                    now_time_str = str(now_time)
                    w.write(now_time_str + '\r\n')
            else:
                None
        else:
            #logファイルが存在しなかった場合の処理
            Path(log_path).touch()
            server.send_message(msg, from_addr, to_addrs)

            now_time = time.time()
            with open(log_path, 'w', newline='', encoding='UTF-8') as w:
                now_time_str = str(now_time)
                w.write(now_time_str + '\r\n')
    else:
        #エラーリストが空だった場合なので特になし
        None
    return None