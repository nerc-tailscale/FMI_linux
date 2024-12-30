# FMI_linux
Program to get weather data from FMI API. The task is executed every day at 23:00. A TMY file format is created and can be used for Radiance simulations.

Main.py file is run via bash (run_python_file.sh) with Crontan

Add the following command to Crontab

@reboot sleep 30 && /path/to/run_python_script.sh >> /path/to/log_file.log 2>&1
