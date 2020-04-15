#.csvファイルを変換して保存する:
#保存ディレクトリを作成する(自動)
#差分を抽出する
#hpcsに関しては.gzと分けて抽出する
#dcが形式が異なることも考慮したうえでのプログラムにする(空行を削除して上2行を削除する)
#メインでは基本的にパスさえ渡せばやってくれるようにしたい(願望)

import os
import csv
import sys
from tqdm import tqdm
import json
from pathlib import Path
import find_filedir_path


#hpcsディレクトリ内のcsvのみのリストを出力する
def class_splitext_csv(past_dir_path):
    file_list = os.listdir(past_dir_path)
    csv_file_list = []
    for file in file_list:
        base, ext = os.path.splitext(file)
        if ext == ".csv" or ext == ".CSV":
            csv_file_list.append(file)
    return csv_file_list

#差分ファイルの抽出
#引数は、ファイルリストとファイルパス
#返り値は差分のみのファイルリスト
def diff_hpcs(csv_file_list, enc_dir_path):
    enc_list = os.listdir(enc_dir_path)
    set_enclist = list(set(csv_file_list) - set(enc_list))
    if len(set_enclist) == 0:
        print('Don\'t need encoding!')
    return set_enclist

#alldir_mkdirを実行することでパス通りのディレクトリを自動で作成することができる
def notdir_find(dir_path):
    down_path = os.path.normpath('%s/../' %dir_path)
    dirname = os.path.basename(dir_path)
    return dirname, down_path

def alldir_mkdir(dir_path):
    dirname, down_path = notdir_find(dir_path)
    dir_list = ['%s' %dirname]
    if os.path.exists(down_path):
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            None
    else:
        while not os.path.exists(down_path):
            try:
                dirname, down_path = notdir_find(down_path)
                dir_list.append(dirname)
                os.mkdir(down_path)
            except FileNotFoundError:
                dirname, down_path = notdir_find(down_path)
                dir_list.append(dirname)
                # os.mkdir(down_path)
                continue
            except FileExistsError:
                break
        dir_list.reverse()
        for file in dir_list:
            try:
                down_path = os.path.join(down_path, file)
                os.mkdir(down_path)
            except FileExistsError:
                print('ディレクトリはすでに作成されています。')
    return None

#各サーバーから収集したcsvファイルを変換するプログラム
#csvの書き換え形式が異なるものが追加された場合、新たな条件分岐を作成する
#引数のpatternは、書き換え形式を番号付けしている。(現状は2まで存在)
def encode_csv_past(past_dir_path, enc_dir_path, charset, pattern):
    try:
        # ファイル群持ちパスリストの出力
        file_dir_list = find_filedir_path.search_files_path_list(past_dir_path)
        for path in file_dir_list:
            #ディレクトリの変わった部分だけの抽出
            new_dir_parts = path.replace(past_dir_path, "")
            #結合させて変換後保存パスとして作成
            new_enc_dir_path = enc_dir_path + new_dir_parts
            #予めディレクトリを作成しておく(ないと変換したファイルを保存するディレクトリが存在しないことになる)
            alldir_mkdir(new_enc_dir_path)
            #ディレクトリ内のcsvのみを抽出
            csv_file_list = class_splitext_csv(path)
            #差分の抽出(全てに対応している予定なのでdiff_hpcsから名前を変更する)
            diff_csv_file_list = tqdm(diff_hpcs(csv_file_list, new_enc_dir_path))
            #tqdmのdescriptionを設定
            diff_csv_file_list.set_description('Encoding [%s]' % path)
            # print("")
            for file in diff_csv_file_list:
                #csvまでの絶対パスを作成
                csv_file_path = os.path.join(path, file)
                with open(csv_file_path, 'r', newline='', encoding=charset) as r:
                    if pattern == 1:
                        content = csv.reader(r)
                        result = list(content)
                        for row in content:
                            result.append(row)
                        ch_result = []
                        for line in result:
                            if line != []:
                                ch_result.append(line)
                        del ch_result[:2]
                        enc_file_path = enc_dir_path + os.path.join(new_dir_parts, file)
                        with open(enc_file_path, 'w', newline='', encoding='UTF-8') as w:
                            writer = csv.writer(w)
                            writer.writerows(ch_result)
                    elif pattern == 2:
                        content = csv.reader(r)
                        result = list(content)
                        for row in content:
                            result.append(row)
                        enc_file_path = enc_dir_path + os.path.join(new_dir_parts, file)
                        with open(enc_file_path, 'w', newline='', encoding='UTF-8') as w:
                            writer = csv.writer(w)
                            writer.writerows(result)
                    else:
                        print("設定されていないパターンです。")
    except UnicodeDecodeError:
        print('\n文字コードエラーでエンコードできませんでした。')
    except :
            print('Unexpected error')
    return None

# def encode_now_other(current_dir_path, enc_current_dir_path):
#     alldir_mkdir(enc_current_dir_path)
#     current_dir_list = os.listdir(current_dir_path)
#     for file in current_dir_list:
#         current_file_path = os.path.join(current_dir_path, file)
#         enc_current_file_path = os.path.join(enc_current_dir_path, file)
#         if not os.path.exists(enc_current_file_path):
#             Path(enc_current_file_path).touch()
#         # if os.path.getsize(current_file_path) == os.path.getsize(enc_current_file_path):
#         #     print('Don\'t need encoding!')
#         # else:
#         with open(current_file_path, 'r', encoding='shift-jis') as current:
#             reader = csv.reader(current)
#             result = list(reader)
#             for i in reader:
#                 result.append(i)
#             del result[:2]
#         with open(enc_current_file_path, 'w', newline='', encoding='shift-jis') as enc_current:
#             writer = csv.writer(enc_current)
#             writer.writerows(result)
#     return None

# def encode_now_hpcs(current_dir_path, enc_current_dir_path):
#     alldir_mkdir(enc_current_dir_path)
#     current_dir_list = os.listdir(current_dir_path)
#     for file in current_dir_list:
#         current_file_path = os.path.join(current_dir_path, file)
#         enc_current_file_path = os.path.join(enc_current_dir_path, file)
#         if not os.path.exists(enc_current_file_path):
#             Path(enc_current_file_path).touch()
#         # if os.path.getsize(current_file_path) == os.path.getsize(enc_current_file_path):
#         #     print('Don\'t need encoding!')
#         # else:
#         with open(current_file_path, 'r', encoding='UTF-8') as current:
#             reader = csv.reader(current)
#             result = list(reader)
#             for i in reader:
#                 result.append(i)
#             # del result[:2]
#         with open(enc_current_file_path, 'w', newline='', encoding='UTF-8') as enc_current:
#             writer = csv.writer(enc_current)
#             writer.writerows(result)
#     return None

def encode_csv_current(current_dir_path, enc_current_dir_path, charset, pattern):
    #この部分は後程つくります
    alldir_mkdir(enc_current_dir_path)
    current_dir_list = os.listdir(current_dir_path)
    for file in current_dir_list:
        current_file_path = os.path.join(current_dir_path, file)
        enc_current_file_path = os.path.join(enc_current_dir_path, file)
        if not os.path.exists(enc_current_file_path):
            Path(enc_current_file_path).touch()
        with open(current_file_path, 'r', newline='', encoding=charset) as current:
            if pattern == 1:
                reader = csv.reader(current)
                result = list(reader)
                for i in reader:
                    result.append(i)
                del result[:2]
                with open(enc_current_file_path, 'w', newline='', encoding='UTF-8') as enc_current:
                    writer = csv.writer(enc_current)
                    writer.writerows(result)
            elif pattern == 2:
                reader = csv.reader(current)
                result = list(reader)
                for i in reader:
                    result.append(i)
                with open(enc_current_file_path, 'w', newline='', encoding='UTF-8') as enc_current:
                    writer = csv.writer(enc_current)
                    writer.writerows(result)
            else:
                print("設定されていないパターンです。")
    return None