from pydub import AudioSegment

song = AudioSegment.from_wav("../sample/ZZG01_20210501_070000.wav")
song.export("wav2flac_demo.flac", format="FLAC")

song = AudioSegment.from_file("wav2flac_demo.flac", format="FLAC")
song.export("flac2wav_demo.wav", format="WAV")
