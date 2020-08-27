#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
from mfrc522 import SimpleMFRC522
from datetime import datetime
import requests
import json
import time
import config


sonos_url = config.SONOS_URL
output_file_name = config.LOG_FILE
log = config.LOG


def sayText(text):
    """ Function to make the voice assistant announce a string """

    query = "say/" + str(text) + "/12"
    makeRequest(query)


def logInformation(log_text):
    """ Logging the actions (set LOG to false in config.py if you don't want to log the actions) """

    if log:
        str_to_write = 'echo "' + str(log_text) + '" >> ' + output_file_name
        os.system(str_to_write)


def makeRequest(request, actionMessage=None):
    """ Make a request to the sonos http API and log it (if enabled in config.py) """

    if actionMessage is not None:
        sayText(str(actionMessage))
        logInformation(str(actionMessage))
    request_url = sonos_url + str(request)
    message = requests.get(request_url)
    result = message.json()
    # check if sonos http API successfully executed the request and log it
    if (not result.get("status") is None) and result["status"] == "error":
        logInformation('"Request of "' + str(request) + '" failed"')
    else:
        logInformation('"Request of "' + str(request) + '" successful"')
    return result


def start():
    """ The function that continuously runs the code to read RFID tags and execute the action embedded in the tag """

    reader = SimpleMFRC522()
    is_running = True #flag to keep it running forever
    active_card = -1 #a three step flag to ensure that the same card isn't read twice accidentally

    while is_running:
        # read the card
        id, text = reader.read_no_block()

        # if a card is left on the reader, we don't want to read it more than once,
        # so we check if the reader reads an empty card, and if so we accept the
        # next read. But the reader retains the card information for one more read iterations
        # even after the card is not within range, so we check if the third continous reading 
        # is also empty, and if so we confirm that no card has been in contact with 
        # the reader and can will parse the next card reading
        if active_card > -1:
            if id == None and active_card == 1:
                active_card = 0
            elif id == None and active_card == 0:
                active_card = -1
            if id != None:
                active_card = 1
        
        # active_card == -1 means that no card was in contact with the reader in the previous
        # reading, thus we won't be reading the same card again
        elif active_card == -1 and text != None:
            active_card = 1 #set active_card to 1 to indicate we read a card

            #see the grammar in rfidOperations.py to understand how tags are written
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

                # toggle night mode
                if instructions == "togglenightmode":
                    state = makeRequest("state/")
                    if state["nightMode"] == "false":
                        makeRequest("nightmode/on/", "Turning Night Mode Off")
                    elif state["nightMode"] == "true":
                        makeRequest("nightmode/off", "Turning Night Mode On")
                    else:
                        sayText("Current state cannot be read")
                        logInformation("Retrieving current state failed")
                
                # toggle enhanced speech mode
                elif instructions == "togglespeechmode":
                    state = makeRequest("state/")
                    if not state["equalizer"]["speechEnhancement"]:
                        makeRequest("speechenhancement/on", "Enhanced Speech On")
                    elif state["equalizer"]["speechEnhancement"]:
                        makeRequest("speechenhancement/off", "Enhanced Speech Off")
                    else:
                        logInformation("Retrieving current state failed")

                # toggle play/pause/
                elif instructions == "playpause":
                    makeRequest("playpause/")
                
                # toggle mute
                elif instructions == "togglemute":
                    makeRequest("toggleMute/")

                # toggle shuffle
                elif instructions == "shuffle":
                    state = makeRequest("state/")
                    if not state["playMode"]["shuffle"]:
                        makeRequest("shuffle/on", "Turning ON Shuffle")
                    elif state["playMode"]["shuffle"]:
                        makeRequest("shuffle/off", "Turning OFF Shuffle")

                # commands that don't depend on current state of the player       
                else:
                    makeRequest(str(instructions), str(instructions))

            # play from spotify
            elif command.lower() == "2":
                mediaName = splitted[2]
                mediaName = mediaName.strip()
                spotifyURI = splitted[1]
                spotifyURI = spotifyURI.strip()
                logInformation('"Spotify URI: ' + str(spotifyURI) + ', requested at: ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' "')
                makeRequest("spotify/now/" + ("spotify:" + str(spotifyURI)), "Playing " + mediaName + " from Spotify")
                
        time.sleep(.5)
        text = None
        command = ''
        spotifyURI = ''

    # clean up the GPIO information
    GPIO.cleanup()


if __name__ == '__main__':
    start()

