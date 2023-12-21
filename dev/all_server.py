# V4 this sample by restful api trigger and store the result to pg, modify for mic-710aix
import pandas as pd
import silic
import os
from minio import Minio
from flask import Flask, request, jsonify
import sqlalchemy as db
from datetime import datetime
import shutil

RESULT_BASE_PATH: str = os.path.join(os.getcwd(), "result_silic")
PG_CSV_FILE_PATH: str = RESULT_BASE_PATH + "/label/labels.csv"
# PG_DATABASE_URL: str = "postgresql://188ae346-2065-47af-8df3-a14008cb7f29:ng7t27G4ciAwShQHNN72n0Lce@60.250.255.162:5432/silic-result"
# PG_DATABASE_URL: str = "postgresql://silic:silic@localhost:5432/silic"
PG_DATABASE_URL: str = "postgresql://silic:silic@140.113.13.93:5432/silic"
PG_SCHEMA_NAME: str = "silic"
PG_TABLE_NAME: str = "silic_labels_table"
PG_TARGETCLASSES_M: str = "1, 11, 12, 28, 29, 35, 40, 41, 72, 73, 76, 77, 78, 85, 86, 103, 105, 110, 126, 187, 199, 202, 235, 290, 307, 308, 313, 315, 316, 320, 330, 332, 333, 340, 341, 342, 344, 383, 419, 420, 459, 463, 465, 468, 553, 554, 555, 563, 565, 566"

SILIC_MODEL: str = "./exp29"
SILIC_STEP: int = 1000
SILIC_CONF_THRES: float = 0.5

# MINIO_ENDPOINT: str = 'blobstore.education.wise-paas.com:8888'
# ACCESS_KEY: str = '836f6e5b71294a50989599f54a63f628'
# SECRET_KEY: str = 'xqDXwM57kYuA01ptpToWbtuj5SzSKAFzc'
# BUCKET_NAME: str = 'ntutony-demo'
# MINIO_ENDPOINT: str = "localhost:9010"
MINIO_ENDPOINT: str = "140.113.13.93:9010"
ACCESS_KEY: str = "admin"
SECRET_KEY: str = "987654321"
BUCKET_NAME: str = "silic-bucket"

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
    os.makedirs(home_base_path, exist_ok=True)     # 确保下载目录存在

    silic.browser(
      source=download_path,
      model=SILIC_MODEL,
      step=SILIC_STEP,
      targetclasses=PG_TARGETCLASSES_M,
      conf_thres=SILIC_CONF_THRES,
      zip=False,  # zip=false表示不產生zip檔
    )  

    # 调用函数删除特定类型的文件（例如删除路径'./samples3/'下的file）
    # delete_specific_files(home_base_path, file_name)
    # shutil.rmtree(os.path.join(RESULT_BASE_PATH, "audio"))
    # shutil.rmtree(os.path.join(RESULT_BASE_PATH, "linear"))
    # shutil.rmtree(os.path.join(RESULT_BASE_PATH, "rainbow"))

    upload_data_to_postgresql(
      csv_file_path=PG_CSV_FILE_PATH,
      database_url=PG_DATABASE_URL,
      schema_name=PG_SCHEMA_NAME,
      table_name=PG_TABLE_NAME,
      if_exists="replace"
    )
    return (
      jsonify({"message": "Successfully processed the file and restore to pg archive."}),
      200
      )

  except Exception as e:
    return jsonify({"error": str(e)}), 500


# delete the download file
def delete_specific_files(directory: str, file_extension: str):
  # 获取路径下的所有文件和目录列表
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
  if_exists: str="replace"
):
  try:
    # 读取 labels.csv 文件
    df = pd.read_csv(csv_file_path)
    # 连接到 PostgreSQL 数据库
    engine = db.create_engine(database_url)
    # metadata = db.MetaData()
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
      # if_exists="append", 
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
