import pyaudio
print(f"[DEBUG warn] --------------------------- 0 -------------------------------")

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

pyaudio_instance = pyaudio.PyAudio()


print('\nAvailable devices:')

for i in range(pyaudio_instance.get_device_count()):
  dev = pyaudio_instance.get_device_info_by_index(i)
  name = dev['name'].encode('utf-8')
  print(f"[{i=}], {name}, \t\tmaxInputChannels={dev['maxInputChannels']}, maxOutputChannels={dev['maxOutputChannels']}")

print('\ndefault input & output device:')
try:
  print(f"[DEBUG warn] --------------------------- 1 -------------------------------")
  print(f"default_input_device_info  = {pyaudio_instance.get_default_input_device_info()}")
  print(f"[DEBUG warn] --------------------------- 2 -------------------------------")
  print(f"default_output_device_info = {pyaudio_instance.get_default_output_device_info()}")
  print(f"[DEBUG warn] --------------------------- 3 -------------------------------")
except Exception as e:
  print(f"[DEBUG warn] --------------------------- 4 -------------------------------")
  print(f"{e}")
  print(f"[DEBUG warn] --------------------------- 5 -------------------------------")

stream = pyaudio_instance.open(
    format=pyaudio.paInt16, 
    channels=1, 
    rate=44100, 
    input=True, 
    # input_device_index=0,
    frames_per_buffer=1024
  )

print("Success!")