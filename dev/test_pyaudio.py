import pyaudio

pyaudio_instance = pyaudio.PyAudio()


print('\navailable devices:')

for i in range(pyaudio_instance.get_device_count()):
  dev = pyaudio_instance.get_device_info_by_index(i)
  name = dev['name'].encode('utf-8')
  print(f"[{i=}], {name}, \t\tmaxInputChannels={dev['maxInputChannels']}, maxOutputChannels={dev['maxOutputChannels']}")

print('\ndefault input & output device:')
print(f"default_input_device_info  = {pyaudio_instance.get_default_input_device_info()}")
print(f"default_output_device_info = {pyaudio_instance.get_default_output_device_info()}")


stream = pyaudio_instance.open(
    format=pyaudio.paInt16, 
    channels=1, 
    rate=44100, 
    input=True, 
    # input_device_index=3,
    frames_per_buffer=1024
  )