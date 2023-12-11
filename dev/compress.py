# 引入所需的模組
import wave
import soundfile as sf

# 定義一個函數，用於將.wav檔案轉換成.flac檔案
def wav_to_flac(wav_file, flac_file):
    # 讀取.wav檔案，並獲取其聲道數、採樣率和數據
    with wave.open(wav_file, "rb") as wav:
        n_channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        data = wav.readframes(wav.getnframes())

    # 轉換.wav檔案為.flac檔案，並保存到指定的路徑
    sf.write(flac_file, data, sample_rate, subtype="PCM_16", format="FLAC")

# 測試函數
# 定義要讀取和轉換的.wav檔案的路徑
# wav_file = "/home/lazoark/lobby/silic/dev/ZZG01_20210501_070000.wav"
wav_file = "/home/lazoark/lobby/silic/dev/test.wav"

# 定義要轉換成的.flac檔案的路徑
flac_file = "output.flac"

# 調用函數，將.wav檔案轉換成.flac檔案
wav_to_flac(wav_file, flac_file)

# 打印轉換成功的訊息
print(f"檔案 {wav_file} 已成功轉換成 {flac_file}")