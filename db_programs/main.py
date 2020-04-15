import os
import json
import encode_csv
import import_csv

pwd0 = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd0, 'influxdb_config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file_influx = json.load(f)

database = config_file_influx['InfluxDB']['database']

client = import_csv.InfluxDB_CSV(
  host = config_file_influx['InfluxDB']['host'],
  port = config_file_influx['InfluxDB']['port'],
  username = config_file_influx['InfluxDB']['username'],
  password = config_file_influx['InfluxDB']['password']
   # If you don't have a database yet you need to create a new database
  # database = config_file_influx['InfluxDB']['database']
)

pwd = os.path.normpath('%s/../config_file' %__file__)
config_path = os.path.join(pwd, 'config.json')
f = open(config_path, 'r', encoding='UTF-8')
config_file = json.load(f)

for server in config_file:
    past_dir_path = config_file[server]['past_dir_path']
    enc_dir_path = config_file[server]['enc_dir_path']
    measurement = config_file[server]['measurement']
    charset = config_file[server]['charset']
    pattern = config_file[server]["pattern"]
    tags_name = config_file[server]["tags_name"]
    
    encode_csv.encode_csv_past(past_dir_path, enc_dir_path, charset, pattern)
    client.import_csv_past(enc_dir_path, measurement, database, tags_name)

