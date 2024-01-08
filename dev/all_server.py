# V4 this sample by restful api trigger and store the result to pg, modify for mic-710aix
import os
from utils.params import Configuration
from utils.color_log import color
import silic
import pandas as pd
from minio import Minio
from flask import Flask, request, jsonify
import sqlalchemy as db
from datetime import datetime
import shutil
logging = color.setup(name=__name__, level=color.INFO)
CONFIG_PATH: str = os.path.join(os.getcwd(), "config")
cfg = Configuration(config_path=CONFIG_PATH)
config: dict = cfg.read_yaml(fname="default.yaml", verbose=True)


RESULT_BASE_PATH: str = os.path.join(os.getcwd(), "result_silic")
PG_CSV_FILE_PATH: str = RESULT_BASE_PATH + "/label/labels.csv"
PG_DATABASE_URL: str = config["pg"]["database_url"]
PG_SCHEMA_NAME: str = config["pg"]["schema_name"]
PG_TABLE_NAME: str = config["pg"]["table_name"]
PG_TARGETCLASSES_M: str = config["pg"]["targetclasses_m"]
SILIC_MODEL: str = config["silic"]["model"]
SILIC_STEP: int = config["silic"]["step"]
SILIC_CONF_THRES: float = config["silic"]["conf_thres"]
MINIO_ENDPOINT: str = config["minio"]["endpoint"]
ACCESS_KEY: str = config["minio"]["access_key"]
SECRET_KEY: str = config["minio"]["secret_key"]
BUCKET_NAME: str = config["minio"]["bucket_name"]

app = Flask(__name__)

@app.route("/silic", methods=["POST"])
def slic_browser():
  current_datetime: str = datetime.now().strftime("%Y-%m-%d")
  home_base_path = os.path.join(os.getcwd(), current_datetime)
  try:
    file_name = request.json["file_name"]
    download_path = os.path.join(home_base_path, file_name)
    print(f"file_path: {file_name}")
    print(f"download_path: {download_path}")

    ########## Use local record file ##########
    # folder = os.getcwd()
    # localfile_path = os.path.join(folder, current_datetime, file_name)
    # print(f"localfile_path: {localfile_path}")
    # shutil.copy(localfile_path, download_path)

    ########## Download the file from S3 ##########
    minio_client = Minio(   
      endpoint=MINIO_ENDPOINT, 
      access_key=ACCESS_KEY, 
      secret_key=SECRET_KEY, 
      secure=False
    )
    minio_client.fget_object(
      bucket_name=BUCKET_NAME,
      object_name=file_name, 
      file_path=download_path
      )

    # classed by silic
    os.makedirs(home_base_path, exist_ok=True)

    silic.browser(
      source=download_path,
      model=SILIC_MODEL,
      step=SILIC_STEP,
      targetclasses=PG_TARGETCLASSES_M,
      conf_thres=SILIC_CONF_THRES,
      zip=False,  # zip=false表示不產生zip檔
    )  

    # 调用函数删除特定类型的文件（例如删除路径'./samples3/'下的file）
    delete_specific_files(home_base_path, file_name)
    shutil.rmtree(os.path.join(RESULT_BASE_PATH, "audio"))
    shutil.rmtree(os.path.join(RESULT_BASE_PATH, "linear"))
    shutil.rmtree(os.path.join(RESULT_BASE_PATH, "rainbow"))

    upload_data_to_postgresql(
      csv_file_path=PG_CSV_FILE_PATH,
      database_url=PG_DATABASE_URL,
      schema_name=PG_SCHEMA_NAME,
      table_name=PG_TABLE_NAME,
      # if_exists="replace"
      if_exists="append"
    )
    return (
      jsonify({"message": "Successfully processed the file and restore to pg archive."}),
      200
      )

  except Exception as e:
    return jsonify({"error": str(e)}), 500


# delete the download file
def delete_specific_files(directory: str, file_extension: str):
  file_list = os.listdir(directory)
  # 删除特定类型的文件
  for file in file_list:
    if file.endswith(file_extension):
      file_path = os.path.join(directory, file)
      try:
        os.remove(file_path)
        print("Downloaded file removed successfully.")
      except Exception as e:
        print(f"Error! Please ensure {file_path} is closed. [log: {e}]")


# Store the result to pg
def upload_data_to_postgresql(
  csv_file_path: str,
  database_url: str,
  schema_name: str,
  table_name: str,
  if_exists: str="append"
):
  try:
    # 读取 labels.csv 文件
    df = pd.read_csv(csv_file_path)
    # 连接到 PostgreSQL 数据库
    engine = db.create_engine(database_url)
    inspector = db.inspect(engine)
    if schema_name not in inspector.get_schema_names():
      engine.execute(db.schema.CreateSchema(schema_name))
      # optional. set the default schema to the new schema:
      engine.dialect.default_schema_name = schema_name

    # 将数据上传至 PostgreSQL 数据库, 'replace'刪除取代現有資料, 'append'加入新的資料
    df.to_sql(
      name=table_name, 
      con=engine, 
      schema=schema_name, 
      if_exists=if_exists, 
      index=False
    )
    print("Store to PostgreSQL successfully!")
  except Exception as e:
    print(f"Error uploading data to PostgreSQL: {str(e)}")


if __name__ == "__main__":
  # file_name = 'recording_20230804_170020.mp3'    # get file name
  # file_path = file_name                          # get file path
  # download_path = "./samples3/"+file_name
  # folder = "/mnt/usb/audio_record_data/"  # 於/mnt/usb/目錄下

  # start the restful
  app.run(host="0.0.0.0", port=5000)
