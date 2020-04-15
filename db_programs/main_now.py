import import_csv
import encode_csv
import os
from configparser import ConfigParser
import json
import csv

pwd0 = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd0, 'influxdb_config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file_influx = json.load(f)

host = config_file_influx['InfluxDB']['host']
port = config_file_influx['InfluxDB']['port']
username = config_file_influx['InfluxDB']['username']
password = config_file_influx['InfluxDB']['password']
database = config_file_influx['InfluxDB']['database']

client = import_csv.InfluxDB_CSV(
  host = host,
  port = port,
  username = username,
  password = password,
   # If you don't have a database yet you need to create a new database
  # database = database
)

# Path list
pwd = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)


for i in config_file:
    current_dir_path = config_file[i]["current_dir_path"]
    enc_current_dir_path = config_file[i]["enc_current_dir_path"]
    measurement = config_file[i]["measurement"]
    charset = config_file[i]["charset"]
    pattern = config_file[i]["pattern"]

    encode_csv.encode_csv_current(current_dir_path, enc_current_dir_path, charset, pattern)
    client.import_csv_current(enc_current_dir_path, measurement, database)
