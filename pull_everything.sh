#!/bin/bash -x
HERE=$(pwd)
for DN in `find ${HERE}/ -maxdepth 1 -type d`
do
  if [ -d ${DN}/.git ]
  then
    cd ${DN}
    git pull
    sleep 3
  fi
done
cd ${HERE}

