#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
from mfrc522 import SimpleMFRC522
from datetime import datetime
import requests
import json
import time

is_running = True
active_card = -1
base_url = "http://localhost:5005/Sonos/"
output_file_name = "jukeoutput.txt"
reader = SimpleMFRC522()

def sayText(text):
    query = "say/" + str(text) + "/12"
    makeRequest(query)

def logInformation(log_text):
    str_to_write = 'echo "' + str(log_text) + '" >> ' + output_file_name
    os.system(str_to_write)

def makeRequest(request):
    request_url = base_url + str(request)
    message = requests.get(request_url)
    result = message.json()
    if (not result.get("status") is None) and result["status"] == "error":
        logInformation('"Request of "' + str(request) + '" failed"')
    else:
        logInformation('"Request of "' + str(request) + '" successful"')
    return result

while is_running:
    id, text = reader.read_no_block()

    if active_card > -1:
        if id == None and active_card == 1:
            active_card = 0
        elif id == None and active_card == 0:
            active_card = -1
        if id != None:
            active_card = 1

    elif active_card == -1 and text != None:
        active_card = 1
        splitted = text.split(';')
        command = splitted[0]
        command = command.strip()

        if command.lower() == 'stop':
            logInformation('"STOPPING AT: ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' "')
            makeRequest("pause/")
            is_running = False

        elif command.lower() == "1":
            instructions = splitted[1]
            instructions = instructions.strip()
            if instructions == "togglenightmode":
                state = makeRequest("state/")
                if state["nightMode"] == "false":
                    sayText("Turning Night Mode Off")
                    makeRequest("nightmode/on/")
                elif state["nightMode"] == "true":
                    sayText("Turning Night Mode On")
                    makeRequest("nightmode/off")
                else:
                    sayText("Current state cannot be read")
                    print("Current state cannot be read")
                    logInformation("Retrieving current state failed")
            elif instructions == "togglespeechmode":
                state = makeRequest("state/")
                if not state["equalizer"]["speechEnhancement"]:
                    sayText("Enhanced Speech On")
                    makeRequest("speechenhancement/on")
                elif state["equalizer"]["speechEnhancement"]:
                    sayText("Enhanced Speech Off")
                    makeRequest("speechenhancement/off")
                else:
                    print("Current state cannot be read")
                    logInformation("Retrieving current state failed")
            elif instructions == "playpause" or instructions == "togglemute":
                makeRequest("playpause/")
            elif instructions == "shuffle":
                state = makeRequest("state/")
                if not state["playMode"]["shuffle"]:
                    sayText("Turning ON Shuffle")
                    logInformation("Turning ON Shuffle")
                    makeRequest("shuffle/on")
                elif state["playMode"]["shuffle"]:
                    sayText("Turning OFF Shuffle")
                    logInformation("Turning OFF Shuffle")
                    makeRequest("shuffle/off")
            else:
                sayText(str(instructions))
                print(base_url + str(instructions))
                makeRequest(str(instructions))

        elif command.lower() == "2":
            mediaName = splitted[2]
            mediaName = mediaName.strip()
            spotifyURI = splitted[1]
            spotifyURI = spotifyURI.strip()
            sayText("Playing " + mediaName + " from Spotify")
            logInformation('"Spotify URI: ' + str(spotifyURI) + ', requested at: ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' "')
            print(base_url + "spotify/now/" + str(spotifyURI))
            makeRequest("spotify/now/" + ("spotify:" + str(spotifyURI)))
            
    time.sleep(.5)
    text = None
    command = ''
    spotifyURI = ''

GPIO.cleanup()

