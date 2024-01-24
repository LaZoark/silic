import time
import sys, os
print(f"hello 1")
time.sleep(2)
os.execv(sys.executable, ['python'] + sys.argv)
