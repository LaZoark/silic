"""
This script provides the following functions:
1. records sound from a (USB) microphone 
2. uploads it to s3 blub (using Minio)
3. pushes recorded audio file_name to URL_POST_ENDPOINT
"""
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

### Suppressing pyaudio error logs
from ctypes import *
# From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
# $ grep -rn snd_lib_error_handler_t
# include/error.h:59:typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *fmt, ...) /* __attribute__ ((format (printf, 5, 6))) */;
# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)

# MINIO_ENDPOINT: str = 'blobstore.education.wise-paas.com:8888'
# ACCESS_KEY: str = '836f6e5b71294a50989599f54a63f628'
# SECRET_KEY: str = 'xqDXwM57kYuA01ptpToWbtuj5SzSKAFzc'
# BUCKET_NAME: str = 'ntutony-demo'
# URL_POST_ENDPOINT: str = "http://127.0.0.1:5000/silic"
URL_POST_ENDPOINT: str = "http://ed716.duckdns.org:5000/silic"
MINIO_ENDPOINT: str = "140.113.13.93:9010"
# MINIO_ENDPOINT: str = "ed716.duckdns.org:8888"
# MINIO_ENDPOINT: str = "localhost:9010"
ACCESS_KEY: str = "admin"
SECRET_KEY: str = "987654321"
BUCKET_NAME: str = "silic-bucket"

MACHINE_PREFIX: str = "NTU"
MACHINE_ID: typing.List[int|str] = 2
MACHINE_LOCATION: typing.Literal["XT", "HS", "DG"] = "DG"
'''
NTU_XT1, XT2 (溪頭)
NTU_HS1 (和社)
NTU_DG (對高岳)
'''

AUDIO_FRAMES_PER_BUFFER: int = 1024
AUDIO_FORMAT: int = pyaudio.paInt16
AUDIO_FILE_FORMAT: str = ".wav"
MIC_CHANNELS: int = 1  # microphone channel
AUDIO_SAMPLE_RATE: int = 44100
# AUDIO_SAMPLE_RATE: int = 48000
AUDIO_RECORD_SECONDS: int = 300

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
  # dtime = int(datetime.now().timestamp() * 1000)    # Milliseconds (1/1,000 second)
  dtime = datetime.now().strftime("%Y%m%d_%H%M%S")
  filename = f"{MACHINE_PREFIX}_{MACHINE_LOCATION}{MACHINE_ID}_" + str(dtime) + AUDIO_FILE_FORMAT
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
  # url = "http://127.0.0.1:5000/silic"
  url = URL_POST_ENDPOINT
  data = {"file_name": filename}
  response = requests.post(url, json=data)
  if response.status_code == 200:
    print("POST success", response.json())
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
