echo -e '#!/bin/sh\nsudo mkdir -p /media/silic\nsudo umount /dev/sda1\nsudo mount /dev/sda1 -t vfat -o rw,nosuid,nodev,sync,noatime,quiet,shortname=mixed,uid=1000,gid=1000,umask=077,iocharset=utf8 /media/silic\necho 'mount to /media/silic'\n' | sudo tee /etc/init.d/mount-usb > /dev/null
sudo chmod +x /etc/init.d/mount-usb
update-rc.d mount-usb defaults



#!/bin/sh
sudo mkdir -p /media/silic
sudo umount /dev/sda1
sudo mount /dev/sda1 -t vfat -o rw,nosuid,nodev,sync,noatime,quiet,shortname=mixed,uid=1000,gid=1000,umask=077,iocharset=utf8 /media/silic
echo 'mount to /media/silic'



#!/bin/sh
cd ~/lobby/silic/; ~/.local/bin/poetry run python dev/audio2s3.py
