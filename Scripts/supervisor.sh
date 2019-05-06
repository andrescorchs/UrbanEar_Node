#!/bin/bash

cd /home/pi/Repositorio_main/

#PID=$(ps aux | grep -c [m]ain_test.py)

if [[ $(ps aux | grep -c main_test.py) -eq 1 ]]
then
	if [ -f config.yaml ]
	then
		/home/pi/berryconda3/envs/urbanear/bin/python3 main.py
	fi
fi


