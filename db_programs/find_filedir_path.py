#プログラム概要：指定したディレクトリ内においてファイル群を持つディレクトリパスを全て格納したリストを出力する
#前提条件：ディレクトリの中身としてはディレクトリ群のみかファイル群のみ

#2019/11/15時点でディレクトリ内が空だった場合、無限ループエラー場発生するので改善予定

import os

#そのパスの直下がファイル群を持っているかどうか知らせる関数
#引数：判定したいディレクトリパス
#返り値：ファイル群のみが存在するとTrue、そうじゃないとFalse
def path_has_files(path):
    dc = 0
    fc = 0
    list_in_path = os.listdir(path)
    for dir_or_file in list_in_path:
        dir_or_file_path = os.path.join(path, dir_or_file)
        if os.path.isdir(dir_or_file_path):
            dc += 1
        else:
            fc += 1
    return fc > 0 and dc == 0

def search_files_path_list(start_dir):
    #まだ更新の余地があるパスを格納
    search_files_path = []
    #ファイル群までたどり着いたパスを格納
    searched_files_path = []

    #指定ディレクトリ内がファイル群か否か判定
    if path_has_files(start_dir):
        searched_files_path.append(start_dir)
        #これはこれで終了
    else:
        #中身がディレクトリ群だった場合にファイル群パスを探索
        start_dir_list = os.listdir(start_dir)
        for dir in start_dir_list:
            dir_path = os.path.join(start_dir, dir)
            search_files_path.append(dir_path)
        #search_files_pathの中身がある限りループする
        while search_files_path:
            #search_files_pathの中身を一個ずつみる
            for path in search_files_path:
                #pathの中身がファイル群だった場合にsearchから削除してsearchedに追加
                if path_has_files(path):
                    search_files_path.remove(path)
                    searched_files_path.append(path)
                #pathの中身がディレクトリ群だった場合にパスを更新して追加し、更新前のものは削除
                else:
                    #中身のディレクトリ一覧を取得
                    dir_list = os.listdir(path)
                    #一覧から一個ずつ出力
                    for down_dir in dir_list:
                        #更新用のディレクトリパスを作成
                        new_dir_path = os.path.join(path, down_dir)
                        search_files_path.append(new_dir_path)
                        search_files_path.remove(path)
    return searched_files_path

    