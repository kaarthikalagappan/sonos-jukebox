#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


def writeToTag(data):
    """ Function to write to the tag """

    reader = SimpleMFRC522()

    #Only 48 characters can be written using the mfrc522 library
    if len(data) > 48:
        print("""Can accept only string less than 48 characters, 
                but given data is > 48 chars, so writing only first 48 characters""")
    
    print("Place Tag to write")
    reader.write((str(data)[:48]))
    print("Successfully written")


def start():
    """ A method that manages writing to the RFID tag """

    flag = True

    """
    Grammar of the instruction embedded to the tags (jukebox uses this grammar)

    An instruction that starts with '1' means it is a system command (play, pause...)

    An instruction that starts with '2' means the following text is a Spotify URI and is followed
    by the media name (the media name will be announced when the tag is used)
    
    TODO: an instruction that starts with '3' means the following text is an Apply Music ID
    TODO: an instruction that starts with '4' means the following text is an Amazon Music ID
    """

    reader = SimpleMFRC522()

    while flag:
        flag = False
        userInput = input("1. System Command\n2. Spotify URI\n3. Read RFID Tag\n")

        if int(userInput) == 1:
            systemInput = input("\n1. play\n2. pause\n3. playpause\n4. mute/unmute\n5. next\n6. previous\n7. shuffle\n8. clearqueue\n9. toggle night mode\n10. toggle enhanced speech mode\n11. custom\n")

            if int(systemInput) == 1:
                writeToTag("1;play")
            elif int(systemInput) == 2:
                writeToTag("1;pause")
            elif int(systemInput) == 3:
                writeToTag("1;playpause")
            elif int(systemInput) == 4:
                writeToTag("1;togglemute")
            elif int(systemInput) == 5:
                writeToTag("1;next")     
            elif int(systemInput) == 6:            
                writeToTag("1;previous")           
            elif int(systemInput) == 7:           
                writeToTag("1;shuffle")     
            elif int(systemInput) == 8:
                writeToTag("1;clearqueue") 
            elif int(systemInput) == 9:
                writeToTag("1;togglenightmode")
            elif int(systemInput) == 10:
                writeToTag("1;togglespeechmode")
            elif int(systemInput) == 11:
                data = input("Custom command (max 48 characters): ")
                writeToTag("1;" + data)
            else:
                print("Invalid selection, please try again")
                flag = True
                continue

        elif int(userInput) == 2:
            URI = input("Enter the Spotify URI in the format given by Spotify ('spotify:{track/playlist/NO-ARTIST}:{ID}):'")
            mediaName = input("What is the name of the album, track, or playlist: ")

            writeToTag("2;" + URI[8:] + ";"+ mediaName)

            print("Successfully written")

        elif int(userInput) == 3:
            print("Place the card on top of the reader")
            id, text = reader.read()
            print(text)

        else:
            print("Invalid selection, please try again")
            flag = True
            continue
        
        userInput = input("""\n1. Write or read another tag\n2. Exit\n""")
        if int(userInput) == 1:
            flag = True   
        else:
            GPIO.cleanup()
            flag = False


if __name__ == '__main__':
    start()
