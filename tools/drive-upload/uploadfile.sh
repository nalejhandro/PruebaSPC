#!/bin/bash

ACCOUNT="XXXXXX@developer.gserviceaccount.com"
KEY_FILE_PATH="drive-upload.p12"
USER="user@gmail.com"

if [ $# -eq 0 ]
  then
    echo "No arguments supplied, provide filepath mimetype description parentfolder."

elif [ $# -ne 4 ]
  then
    echo "Not enough arguments supplied, provide filepath mimetype description parentfolder."

  else
    /opt/drive-upload/env/bin/python /opt/drive-upload/app/main.py $ACCOUNT $KEY_FILE_PATH $USER $1 $2 --desc $3 --parent $4 2>&1
fi
