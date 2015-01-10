#!/usr/bin/python
# -*- coding: utf-8 -*-

#from __future__ import print_function, division, absolute_import, unicode_literals

import RPi.GPIO as GPIO
import time
import sys
import os
import glob
import subprocess

from RPLCD import CharLCD, cleared, cursor
from RPLCD import Alignment, CursorMode, ShiftMode
from time import sleep, strftime
from datetime import datetime

GPIO.setwarnings(False)

# -----------------------------------------
# Temperature from dallas probe DS18B20 - Start
# -----------------------------------------

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = str(int(temp_string) / 1000)
        return temp_c

# ----------------------------------------
# Temperature from dallas probe DS18B20 - End
# ----------------------------------------

# ---------------------------------------
# CPU temperature as a rounded integer - Start                                 
# ---------------------------------------

def getCPUtemperature():
   res = os.popen('vcgencmd measure_temp').readline()
   res = float(res.replace("temp=","").replace("'C\n",""))
   res = int(round(res,0))
   res = str(res)
   return res

getCPUtemperature()

# --------------------------------------
# CPU temperature as a rounded integer - End
# --------------------------------------

# --------------
# MPD Info - Start
# --------------
def Get_MPC_info():
   subprocess_list = subprocess.check_output(('ps', '-A'))
   subprocess_list_mpd = subprocess_list.find("mpd")
   
   if subprocess_list_mpd == -1:
      mpd_info = " MPD not started!   "
      return mpd_info
   
   else:
      process = subprocess.Popen('mpc', shell=True, stdout=subprocess.PIPE)
      status = process.communicate()[0]
      statusLines = status.split('\n')
      #print statusLines
      
      # If MPC was not on "STOP"
      if len(statusLines) > 2:
      
            # Extract Volume (be sure that the mpc command return a value in volume (i.e not 'NA')
            mpc_vol= statusLines[2].replace("volume:","").replace(" ","").split('%')[0] + " %"
            #print "mpc vol = " + mpc_vol
            if len(str(mpc_vol)) == 3:
                mpc_vol = '0' + str(mpc_vol)
         
            timings_mpd = statusLines[1].split(' ')
            #print "timing mpd = " + str(len(timings_mpd))
            index_list = len(timings_mpd) -2
            #print "index = " + str(len(timings_mpd)-2)
            
            # Error handling
            if index_list <= 7:
            
               # Extract the song duration and the current duration played
               song_lengh = timings_mpd[index_list].split('/')[1]
               time_play = statusLines[1].split(' ')[index_list].split('/')[0]
               #print song_lengh
               #print time_play
               
               # Convert the durations in seconds
               song_lengh_sec=int(song_lengh.split(':')[0]) * 60 + int(song_lengh.split(':')[1])
               time_play_sec=int(time_play.split(':')[0]) * 60 + int(time_play.split(':')[1])

               # Calculate current song "countdown"
               count_down = int(song_lengh_sec) - int(time_play_sec)
         
               # Display the song count down (18 characters lengh)
               hours = count_down // 3600
               # Add a '0' if hours between 1-9
               if len(str(hours)) == 1:
                   hours = '0' + str(hours)
   
               minutes = int((count_down % 3600) // 60)
               # Add a '0' if minutes between 1-9
               if len(str(minutes)) == 1:
                  minutes = '0' + str(minutes)
       
               seconds = int(count_down % 60)
               # Add a '0' if seconds between 1-9
               if len(str(seconds)) == 1:
                   seconds = '0' + str(seconds)
       
               if count_down >= 3600:
                  count_down_display=  '{}:{}:{}'.format(hours, minutes, seconds)
                  if len(mpc_vol) > 4: # Volume equals 100%
                     spacer = "     "  # 5 spaces
                  else : 
                     spacer = "      " # 6 spaces
            
               else:
                  count_down_display =  '{}:{}'.format(minutes, seconds)
                  if len(mpc_vol) > 4: # Volume equals 100%
                     spacer = "        " # 8 spaces
                  else : 
                     spacer = "         " # 9 spaces
            
               mpd_info = " " + mpc_vol + spacer + count_down_display
               
            else:
               mpd_info = "                    " # 20 spaces
               
      else:
            mpd_info = " STOP         00:00 "  
      
      #print " mpd info = " + mpd_info
      return mpd_info
   
# -------------   
# MPD Info - End
# -------------

# -------------------
# Display section - Start
# -------------------

lcd = CharLCD()

# Define custom character (celcius degre sign)
degre_celcius= (0b00000, 0b00110, 0b00110, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000 );
lcd.create_char(0, degre_celcius)

lcd.clear()
   
while 1:
   # Row 1
   lcd.cursor_pos = (0, 0)
   lcd.write_string(" " + datetime.now().strftime('%a %d %b   %H:%M') + " ")
   # Row 2
   lcd.cursor_pos = (1, 0)
   lcd.write_string(" " + read_temp() + unichr(0) +"C" + "          " + getCPUtemperature() + unichr(0) +"C " )
   # Row 3
   lcd.cursor_pos = (3, 0)
   lcd.write_string(Get_MPC_info())
   #sleep(60)

# ------------------   
# Display section - End
# ------------------
