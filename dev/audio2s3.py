# V4 為新增POST API 功能, modify for mic-710aix
import os
import time
import pyaudio
import wave
import requests
from datetime import datetime
from minio import Minio
# from minio.error import ResponseError //"ResponseError" 沒有在使用了
from minio.error import InvalidResponseError
import typing

# MINIO_ENDPOINT: str = 'blobstore.education.wise-paas.com:8888'
# ACCESS_KEY: str = '836f6e5b71294a50989599f54a63f628'
# SECRET_KEY: str = 'xqDXwM57kYuA01ptpToWbtuj5SzSKAFzc'
# BUCKET_NAME: str = 'ntutony-demo'
# MINIO_ENDPOINT: str = "140.113.13.93:9010"
MINIO_ENDPOINT: str = "localhost:9010"
ACCESS_KEY: str = "admin"
SECRET_KEY: str = "987654321"
BUCKET_NAME: str = "silic-bucket"
MACHINE_ID: typing.List[int|str] = 99

AUDIO_FRAMES_PER_BUFFER: int = 1024
AUDIO_FORMAT: int = pyaudio.paInt16
AUDIO_FILE_FORMAT: str = ".wav"
MIC_CHANNELS: int = 1  # microphone channel
AUDIO_SAMPLE_RATE: int = 44100
AUDIO_RECORD_SECONDS: int = 60

def record_audio(duration: int, folder: str="."):
  py_audio = pyaudio.PyAudio()
  stream = py_audio.open(
    format=AUDIO_FORMAT, 
    channels=MIC_CHANNELS, 
    rate=AUDIO_SAMPLE_RATE, 
    input=True, 
    frames_per_buffer=AUDIO_FRAMES_PER_BUFFER
  )
  print("Recording audio...")
  frames = []
  for i in range(0, int(AUDIO_SAMPLE_RATE / AUDIO_FRAMES_PER_BUFFER * duration)):
    data = stream.read(AUDIO_FRAMES_PER_BUFFER)
    frames.append(data)
  print("Finished recording.")

  stream.stop_stream()
  stream.close()
  py_audio.terminate()

  # Create folder based on current date
  current_date = datetime.now().strftime("%Y-%m-%d")
  folder_path = os.path.join(folder, current_date)
  if not os.path.exists(folder_path):
    os.makedirs(folder_path)

  # Save audio file locally
  dtime = int(datetime.now().timestamp() * 1000)    # Milliseconds (1/1,000 second)
  filename = f"recording_M{MACHINE_ID}_" + str(dtime) + AUDIO_FILE_FORMAT
  audio_file = os.path.join(folder_path, filename)
  wf = wave.open(audio_file, "wb")
  wf.setnchannels(MIC_CHANNELS)
  wf.setsampwidth(py_audio.get_sample_size(AUDIO_FORMAT))
  wf.setframerate(AUDIO_SAMPLE_RATE)
  wf.writeframes(b"".join(frames))
  wf.close()

  # upload to minio
  upload_to_minio(audio_file)

  # POST API
  try:
    post_byrestful(filename)
  except Exception as e:
    print(f"[!!] {e}")


def upload_to_minio(filepath):
  minio_client = Minio(
    endpoint=MINIO_ENDPOINT, 
    access_key=ACCESS_KEY, 
    secret_key=SECRET_KEY, 
    secure=False
  )
  try:
    # 檢查bucket是否存在，如果不存在，則建立一個
    if not minio_client.bucket_exists(BUCKET_NAME):
      minio_client.make_bucket(BUCKET_NAME)
    with open(filepath, "rb") as file_data:
      file_stat = os.stat(filepath)
      object_name = os.path.basename(filepath)
      # https://stackoverflow.com/questions/55223401/minio-python-client-upload-bytes-directly
      minio_client.put_object(
        bucket_name=BUCKET_NAME, 
        object_name=object_name, 
        data=file_data, 
        length=file_stat.st_size,
        content_type='audio/wav'
      )
    print(f"檔案 {filepath} 已成功上傳到 {BUCKET_NAME}/{object_name}")
  except InvalidResponseError as err:
    print("Minio Error: ", err)


def post_byrestful(filename):
  url = "http://127.0.0.1:5000/silic"
  file_name = filename
  data = {"file_name": file_name}
  response = requests.post(url, json=data)

  if response.status_code == 200:
    print("POST success")
  else:
    print("An error occurred:", response.json())


if __name__ == "__main__":
  # AUDIO_RECORD_SECONDS = 5
  # dtime = int(datetime.now().timestamp() * 1000)    # Milliseconds (1/1,000 second)
  # dtime = datetime.now().strftime("%Y%m%d_%H%M%S")  # 加上時間命名
  # folder = '/home/m/audio_record_data/'                              # 於/home/mic-710aix/目錄下
  # folder = "/mnt/usb/audio_record_data/"  # 於/mnt/usb/目錄下

  for i in range(6000):
    # print(f'{dtime = }')
    # time.sleep(1)
    record_audio(AUDIO_RECORD_SECONDS)
