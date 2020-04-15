#エンコードしたcsvをdbに保存する
#hpcsとその他は処理を別にする(文字コードとディレクトリ処理の関係より)
#インポートしたファイルを記録するcsvの作成、記録も行う
#メインでパスとmeasurementさえ渡せば自動で行ってくれるようにしたい(願望)
#ディレクトリの自動生成に関してはencodeのものを持ってくる

from influxdb import InfluxDBClient
import os
import csv
from tqdm import tqdm
from pathlib import Path
import encode_csv
import find_filedir_path

import json

def touch_import_list(measurement):
    import_list_dir_path = os.path.normpath('%s/../import_list/' %__file__)
    #リストを保管するディレクトリがなかったら
    if not os.path.exists(import_list_dir_path):
        encode_csv.alldir_mkdir(import_list_dir_path)
    if "import_file_list_%s.csv" % measurement not in os.listdir(import_list_dir_path):
        Path("%s/import_file_list_%s.csv" % (import_list_dir_path, measurement)).touch()
    return None


def diff_import_list(enc_dir_path, measurement):
    enc_file_list = os.listdir(enc_dir_path)
    import_list_file_path = os.path.normpath('%s/../import_list' %__file__)
    with open('%s/import_file_list_%s.csv' % (import_list_file_path, measurement), 'r') as r:
        imported_list = r.read().split()
        diff_import_enc_list = list(set(enc_file_list) - set(imported_list))
        diff_import_num = len(diff_import_enc_list)
    if diff_import_num == 0:
        print('\nDon\'t need importing!')
    return diff_import_enc_list, diff_import_num

class InfluxDB_CSV(InfluxDBClient):

    def import_csv_past(self, enc_dir_path, measurement, database, tags_name):
        try:
            #ファイル群を持っているディレクトリのリスト
            file_dir_list = find_filedir_path.search_files_path_list(enc_dir_path)
            #インポートリストの作成
            touch_import_list(measurement)
            for path in file_dir_list:
                diff_import_enc_list, diff_import_num = diff_import_list(path, measurement)
                diff_import_enc_list.sort()
                count = 1
                for file in diff_import_enc_list:
                    enc_file_path = os.path.join(path, file)
                    print('\nStart importing : [%s][%s/%s]' % (enc_file_path, count, diff_import_num))
                    with open(enc_file_path, 'r', newline='', encoding="UTF-8") as csv_file:
                        reader = csv.reader(csv_file)
                        reader = list(reader)
                        fields = reader[0]
                        #行数と列数
                        row_length = len(reader)
                        columun_length = len(fields)
                        #カラムを除いた範囲
                        rows = tqdm(range(1, row_length)) #後にtqdmを実装する
                        rows.set_description('Importing [%s]' % (file))
                    for row_num in rows:
                        value = reader[row_num]
                        # rows.set_description('Importing : %s' % file)
                        columun_list = {}
                        tags_list = {}
                        try:
                            for columun_num in range(1, columun_length):
                                if fields[columun_num] not in tags_name:
                                    #辞書型なので、n番目のフィールド名 = n番目の値
                                    # columun_list[fields[columun_num]] = value[columun_num] #1行スタートの行情報
                                    if value[columun_num] != "":
                                        columun_list[fields[columun_num]] = float(value[columun_num])
                                    else:
                                        columun_list[fields[columun_num]] = value[columun_num]
                                else:
                                    tags_list[fields[columun_num]] = value[columun_num]
                        except ValueError:
                            continue
                        import_array = [
                            {
                                "measurement":measurement,
                                "time":value[0].replace('/', '-').replace(' ', 'T').replace('.0', '+09:00'),
                                "fields":columun_list,
                                "tags":tags_list
                            }
                        ]
                        try:
                            self.write_points(import_array, database=database)
                        except:
                            None
                        # print(import_array)
                    #記録機能
                    current_directory_path = os.path.normpath('%s' %__file__)
                    with open('%s/../import_list/import_file_list_%s.csv' % (current_directory_path, measurement), 'a') as w:
                        w.write(file + '\n')
                    count += 1
        except IndexError:
            print('error')
        # except ValueError:
        #     None
        except :
            print('Unexpected error')
        return None

    def import_csv_current(self, enc_current_dir_path, measurement, database):
        try:
            enc_file = os.listdir(enc_current_dir_path)
            for file in enc_file:
                enc_file_path = os.path.join(enc_current_dir_path, file)
                print('\nStart importing : [%s]' % (enc_file_path))
                with open(enc_file_path, 'r', newline='', encoding='UTF-8') as csv_file:
                    reader = csv.reader(csv_file)
                    reader = list(reader)
                    fields = reader[0]
                    #行数と列数
                    row_length = len(reader)
                    columun_length = len(fields)
                    #カラムを除いた範囲
                    rows = tqdm(range(1, row_length)) #後にtqdmを実装する
                    rows.set_description('Importing [%s]' % file)
                
                for row_num in rows:
                    value = reader[row_num]
                    # rows.set_description('Importing : %s' % file)
                    columun_list = {}
                    for columun_num in range(1, columun_length):
                        #辞書型なので、n番目のフィールド名 = n番目の値
                        columun_list[fields[columun_num]] = value[columun_num] #1行スタートの行情報
                    import_array = [
                        {
                            "measurement":measurement,
                            "time":value[0].replace('/', '-').replace(' ', 'T').replace('.0', '+09:00'),
                            "fields":columun_list
                        }
                    ]
                    self.write_points(import_array, database=database)
        except IndexError:
            print('error')
        except :
            print('Unexpected error')
        return None

    # def import_now_other(self, enc_current_dir_path, measurement, database):
    #     enc_file = os.listdir(enc_current_dir_path)
    #     for file in enc_file:
    #         enc_file_path = os.path.join(enc_current_dir_path, file)
    #         print('\nStart importing : [%s]' % (enc_file_path))
    #         with open(enc_file_path, 'r', newline='', encoding='Shift-Jis') as csv_file:
    #             reader = csv.reader(csv_file)
    #             reader = list(reader)
    #             fields = reader[0]
    #             #行数と列数
    #             row_length = len(reader)
    #             columun_length = len(fields)
    #             #カラムを除いた範囲
    #             rows = tqdm(range(1, row_length)) #後にtqdmを実装する
    #             rows.set_description('Importing [%s]' % file)
            
    #         for row_num in rows:
    #             value = reader[row_num]
    #             # rows.set_description('Importing : %s' % file)
    #             columun_list = {}
    #             for columun_num in range(1, columun_length):
    #                 #辞書型なので、n番目のフィールド名 = n番目の値
    #                 columun_list[fields[columun_num]] = value[columun_num] #1行スタートの行情報
    #             import_array = [
    #                 {
    #                     "measurement":measurement,
    #                     "time":value[0].replace('/', '-').replace(' ', 'T').replace('.0', '+09:00'),
    #                     "fields":columun_list
    #                 }
    #             ]
    #             self.write_points(import_array, database=database)
    #     return None

    # def import_now_hpcs(self, enc_current_dir_path, measurement, database):
    #     enc_file = os.listdir(enc_current_dir_path)
    #     for file in enc_file:
    #         enc_file_path = os.path.join(enc_current_dir_path, file)
    #         print('\nStart importing : [%s]' % (enc_file_path))
    #         with open(enc_file_path, 'r', newline='', encoding='UTF-8') as csv_file:
    #             reader = csv.reader(csv_file)
    #             reader = list(reader)
    #             fields = reader[0]
    #             #行数と列数
    #             row_length = len(reader)
    #             columun_length = len(fields)
    #             #カラムを除いた範囲
    #             rows = tqdm(range(1, row_length)) #後にtqdmを実装する
    #             rows.set_description('Importing [%s]' % file)
            
    #         for row_num in rows:
    #             value = reader[row_num]
    #             # rows.set_description('Importing : %s' % file)
    #             columun_list = {}
    #             for columun_num in range(1, columun_length):
    #                 #辞書型なので、n番目のフィールド名 = n番目の値
    #                 columun_list[fields[columun_num]] = value[columun_num] #1行スタートの行情報
    #             import_array = [
    #                 {
    #                     "measurement":measurement,
    #                     "time":value[0].replace('/', '-').replace(' ', 'T').replace('.0', '+09:00'),
    #                     "fields":columun_list
    #                 }
    #             ]
    #             self.write_points(import_array, database=database)
    #     return None