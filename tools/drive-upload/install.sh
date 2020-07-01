#!/bin/bash

# Drive upload install script

# Make sure only root can run our script
if [[ $EUID -ne 0 ]];
  then
    echo "This script must be run as root" 1>&2
    exit 1
fi

apt-get install -y python3-virtualenv

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed python3-virtualenv"
  else
    echo "Unable to install python3-virtualenv please verify."
    exit 1
fi

apt-get install -y python3-dev

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed python3-dev"
  else
    echo "Unable to install python3-dev please verify."
    exit 1
fi

apt-get install -y libffi-dev

OUT=$?
if [ $OUT -eq 0 ];
  then
    echo "Installed libffi-dev"
  else
    echo "Unable to install libffi-dev please verify."
    exit 1
fi

echo "Creating dir drive-upload /opt"
mkdir -p /opt/drive-upload
echo "Copying files to /opt"
cp -a app /opt/drive-upload/app
cp uploadfile.sh /opt/drive-upload/
chmod +x /opt/drive-upload

echo "Creating environment"
cd /opt/drive-upload
virtualenv --python=/usr/bin/python3 env

echo "Installing requiremets"
/opt/drive-upload/env/bin/pip install -r /opt/drive-upload/app/requirements.txt

echo "Done"
