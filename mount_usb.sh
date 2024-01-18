echo -e '#!/bin/sh\nsudo mkdir -p /media/silic\nsudo umount /dev/sda1\nsudo mount /dev/sda1 -t vfat -o rw,nosuid,nodev,sync,noatime,quiet,shortname=mixed,uid=1000,gid=1000,umask=077,iocharset=utf8 /media/silic\necho 'mount to /media/silic'\n' | sudo tee /etc/init.d/mount-usb > /dev/null
sudo chmod +x /etc/init.d/mount-usb
sudo update-rc.d mount-usb defaults



#!/bin/sh
sudo mkdir -p /media/silic
sudo umount /dev/sda1
sudo mount /dev/sda1 -t vfat -o rw,nosuid,nodev,sync,noatime,quiet,shortname=mixed,uid=1000,gid=1000,umask=077,iocharset=utf8 /media/silic
echo 'mount to /media/silic'



#!/bin/sh
cd ~/lobby/silic/; ~/.local/bin/poetry run python dev/audio2s3.py


### inside the crontab (RPi4):
# @reboot cd ~/lobby/silic/; poetry run python dev/audio2s3.py
@reboot /etc/init.d/mount-usb
# @reboot cd ~/lobby/silic/; /home/ntupi/.local/bin/poetry run python dev/audio2s3.py >/tmp/ppylog.log &>/tmp/troubleshooting.log
# @reboot (sleep 60 && cd ~/lobby/silic/ && /home/ntupi/.local/bin/poetry run python dev/audio2s3.py) >/tmp/ppylog.log 2>&1
@reboot (sleep 5 && cd ~/lobby/silic/ && ~/.local/bin/poetry run python dev/audio2s3.py) >/tmp/ppylog.log 2>&1
# */1 * * * * (sleep 5 && lsusb) >/tmp/ppylog.log 2>&1
# */1 * * * * (cd ~/lobby/silic/; /home/ntupi/.local/bin/poetry run python test.py) >/tmp/troubleshooting.log 2>&1

### inside the crontab (TX2):
@reboot (sleep 20 && cd ~/lobby/silic/ && ~/.local/bin/poetry run python dev/audio2s3.py) >/tmp/ppylog.log 2>&1
##### sudo crontab -e
@reboot (sleep 5 && /etc/init.d/mount-usb) >/tmp/mmount.log 2>&1
# @reboot (cd ~/lobby/silic/ && ~/.local/bin/poetry run python dev/audio2s3.py) >/tmp/ppylog.log 2>&1
# */1 * * * * (cd ~/lobby/silic/ && ~/.local/bin/poetry run python dev/audio2s3.py) >/tmp/ppylog.log 2>&1
# */1 * * * * (cd ~/lobby/silic/ && ~/.local/bin/poetry run python dev/test_pyaudio.py) >/tmp/ppylog.log 2>&1
