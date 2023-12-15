# 引入所需的模組
import wave
import soundfile as sf
from minio import Minio
from minio.error import S3Error

# 定義要讀取和轉換的.wav檔案的路徑
wav_file = "/home/lazoark/lobby/silic/dev/TT01_20210401_060000.wav"
wav_file = "dev/wav2flac_demo.flac"

# 定義要轉換成的.flac檔案的路徑
flac_file = "output.flac"

# 定義要上傳到的S3的桶名和物件名
bucket_name = "silic-bucket"
object_name = "output.flac"

# 定義S3的連接資訊，包括端點、存取金鑰和密碼
s3_endpoint = "localhost:9010"
s3_access_key = "admin"
s3_secret_key = "987654321"

# 建立一個Minio客戶端物件
s3_client = Minio(
    s3_endpoint,
    access_key=s3_access_key,
    secret_key=s3_secret_key,
    secure=False
)

# 讀取.wav檔案，並獲取其聲道數、採樣率和數據
with wave.open(wav_file, "rb") as wav:
    n_channels = wav.getnchannels()
    sample_rate = wav.getframerate()
    data = wav.readframes(wav.getnframes())

# 轉換.wav檔案為.flac檔案，並保存到指定的路徑
sf.write(flac_file, data, sample_rate, subtype="PCM_16", format="FLAC")

# 上傳.flac檔案到S3的指定桶和物件
try:
    # 檢查桶是否存在，如果不存在，則建立一個
    if not s3_client.bucket_exists(bucket_name):
        s3_client.make_bucket(bucket_name)

    # 上傳.flac檔案，並指定內容類型為audio/flac
    s3_client.fput_object(
        bucket_name,
        object_name,
        flac_file,
        content_type="audio/flac"
    )

    # 打印上傳成功的訊息
    print(f"檔案 {flac_file} 已成功上傳到 {bucket_name}/{object_name}")

except S3Error as err:
    # 打印上傳失敗的錯誤訊息
    print(f"檔案上傳發生錯誤: {err}")