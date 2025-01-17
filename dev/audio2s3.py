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
import typing
from datetime import datetime
from minio import Minio
from minio.error import InvalidResponseError
from pydub import AudioSegment

from utils.params import Configuration
from utils.color_log import color
logging = color.setup(name=__name__, level=color.DEBUG)
CONFIG_PATH: str = os.path.join(os.getcwd(), "config")
cfg = Configuration(config_path=CONFIG_PATH)
config: dict = cfg.read_yaml(fname="default.yaml", verbose=True)

### Suppressing pyaudio error logs
from ctypes import *
# From alsa-lib Git 3fd4ab9be0db7c7430ebd258f2717a976381715d
# Define our error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
  pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler) # Set error handler

URL_POST_ENDPOINT: str = config["api"]["url_post_endpoint"]
MINIO_ENDPOINT: str = config["minio"]["endpoint"]
ACCESS_KEY: str = config["minio"]["access_key"]
SECRET_KEY: str = config["minio"]["secret_key"]
BUCKET_NAME: str = config["minio"]["bucket_name"]
MINIO_ENDPOINT_REDUNDANT: str = config["minio"]["endpoint_redundant"]
ACCESS_KEY_REDUNDANT: str = config["minio"]["access_key_redundant"]
SECRET_KEY_REDUNDANT: str = config["minio"]["secret_key_redundant"]
BUCKET_NAME_REDUNDANT: str = config["minio"]["bucket_name_redundant"]
MACHINE_PREFIX: str = config["device"]["prefix"]
MACHINE_ID: typing.List[int|str] = config["device"]["id"]
MACHINE_LOCATION: typing.Literal["XT", "HS", "DG"] = config["device"]["location"]
MIC_CHANNELS: int = config["mic"]["channels"]  # microphone channel
AUDIO_FRAMES_PER_BUFFER: int = config["audio"]["frames_per_buffer"]
AUDIO_SAMPLE_RATE: int = config["audio"]["sample_rate"]
AUDIO_RECORD_SECONDS: int = config["audio"]["record_seconds"]
AUDIO_USING_FLAC: bool = config["audio"]["using_flac"]
AUDIO_SAVE_FOLDER_PATH: bool = config["audio"]["save_folder_path"]
AUDIO_FORMAT: int = pyaudio.paInt16
AUDIO_FILE_FORMAT: typing.Literal[".wav", ".flac"] = ".flac" if AUDIO_USING_FLAC else ".wav"

def record_audio(duration: int, folder: str="."):
  py_audio = pyaudio.PyAudio()
  stream = None   # Init as None to check if pyaudio is function normally
  while stream is None:
    try:
      stream = py_audio.open(
        format=AUDIO_FORMAT, 
        channels=MIC_CHANNELS, 
        rate=AUDIO_SAMPLE_RATE, 
        input=True, 
        frames_per_buffer=AUDIO_FRAMES_PER_BUFFER
      )
    except Exception as err:
      logging.critical(f"{err} \nRetry the microphone after 2 seconds...")
      time.sleep(2)
      import sys
      os.execv(sys.executable, ['python'] + sys.argv)

  logging.debug(f"Handle the microphone successfully! [{stream}]")
  logging.info(f"Recording audio... [{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}, {duration=} s]")
  try:
    frames = []
    for i in range(0, int(AUDIO_SAMPLE_RATE / AUDIO_FRAMES_PER_BUFFER * duration)):
      data = stream.read(AUDIO_FRAMES_PER_BUFFER, exception_on_overflow=False)  # Prevent from overflow
      frames.append(data)
    logging.info("Finished recording.")

    stream.stop_stream()
    stream.close()
    py_audio.terminate()
  except Exception as e:
    logging.critical(f"Ignore and restart (5 seconds later)! {e}")
    time.sleep(5)
    import sys
    os.execv(sys.executable, ['python'] + sys.argv)

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
  
  with wave.open(audio_file, "wb") as wf:
    wf.setnchannels(MIC_CHANNELS)
    wf.setsampwidth(py_audio.get_sample_size(AUDIO_FORMAT))
    wf.setframerate(AUDIO_SAMPLE_RATE)
    wf.writeframes(b"".join(frames))

  if AUDIO_USING_FLAC:
    _song = AudioSegment.from_wav(audio_file)
    _song.export(audio_file, format="FLAC")

  upload_to_minio(audio_file)
  try:
    post_byrestful(filename)
  except Exception as e:
    logging.error(f"{e}")


def upload_to_minio(filepath: str):
  minio_client = Minio(
    endpoint=MINIO_ENDPOINT, 
    access_key=ACCESS_KEY, 
    secret_key=SECRET_KEY, 
    secure=False
  )
  selected_minio_bucket_name = BUCKET_NAME
  try:
    minio_client.list_buckets()
  except Exception as e:
    logging.warning(f"Unable to connect to the default MINIO endpoint.({MINIO_ENDPOINT = }) error: {e}")
    logging.info(f"Using the backup endpoint... ({MINIO_ENDPOINT_REDUNDANT = })")
    minio_client = Minio(
      endpoint=MINIO_ENDPOINT_REDUNDANT, 
      access_key=ACCESS_KEY_REDUNDANT, 
      secret_key=SECRET_KEY_REDUNDANT, 
      secure=False
    )
    selected_minio_bucket_name = BUCKET_NAME_REDUNDANT
  try:
    minio_client.list_buckets()
  except Exception as e:
    logging.error(f"Neither the default nor redundant endpoints were connected! Restart the script after 3 seconds...\n{e}")
    time.sleep(3)
    import sys
    os.execv(sys.executable, ['python'] + sys.argv)

  try:
    # 檢查bucket是否存在，如果不存在，則建立一個
    if not minio_client.bucket_exists(selected_minio_bucket_name):
      minio_client.make_bucket(selected_minio_bucket_name)
    with open(filepath, "rb") as file_data:
      file_stat = os.stat(filepath)
      object_name = os.path.basename(filepath)
      # https://stackoverflow.com/questions/55223401/minio-python-client-upload-bytes-directly
      minio_client.put_object(
        bucket_name=selected_minio_bucket_name, 
        object_name=object_name, 
        data=file_data, 
        length=file_stat.st_size,
        content_type="audio/flac" if AUDIO_USING_FLAC else "audio/wav"
      )
    logging.info(f"檔案 {filepath} 已成功上傳到 {selected_minio_bucket_name}/{object_name}")
  # except InvalidResponseError as err:
  except Exception as err:  # To catch all error (including `RequestTimeTooSkewed`)
    logging.error(f"Minio Error: {err}")


def post_byrestful(filename):
  url = URL_POST_ENDPOINT
  data = {"file_name": filename}
  response = requests.post(url, json=data)
  if response.status_code == 200:
    logging.info(f"POST successfully: {response.json()}")
  else:
    logging.warning(f"POST ERROR(res={response.status_code}): {response.json()}")


if __name__ == "__main__":
  # AUDIO_RECORD_SECONDS = 5
  # dtime = int(datetime.now().timestamp() * 1000)    # Milliseconds (1/1,000 second)
  # dtime = datetime.now().strftime("%Y%m%d_%H%M%S")  # 加上時間命名
  # folder = '/home/m/audio_record_data/'                              # 於/home/mic-710aix/目錄下
  # folder = "/mnt/usb/audio_record_data/"  # 於/mnt/usb/目錄下

  # for i in range(6000):
  #   # print(f'{dtime = }')
  #   # time.sleep(1)
  #   record_audio(AUDIO_RECORD_SECONDS)
  while 1:
    record_audio(AUDIO_RECORD_SECONDS, folder=AUDIO_SAVE_FOLDER_PATH)
