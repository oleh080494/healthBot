# December 2022 (c) Johannes Ellemose
# Saves data set from a connected arduino using Serial.print to a log-file.
#
# Based on Robin2's [https://forum.arduino.cc/u/Robin2] post on sending and
# receiving data between arduino and computer over the serial connection
# [https://forum.arduino.cc/t/demo-of-pc-arduino-comms-using-python/219184/5#msg1810764]
#
# the message to be sent from the Arduino starts with < and ends with >
# receiving a message from the Arduino involves waiting until the startMarker
# is detected and saving all subsequent bytes until the end marker is detected.
# This means that a log message can be split between multiple Serial.print on
# the arduino.

import pyrebase
import serial
import serial.tools.list_ports
from signal import signal, SIGINT
import time
import logging


# Hardcode the serial port to bypass the setup of the port, fx. if the same
# port is always used. Set 'arduinoPort = None' to use the assistant.
arduinoPort = "/dev/cu.usbmodem141101"  # Serial Port(USB)
# Hardcode the baud rate to bypass the setup if the same baud rate is always
# used. Set 'baudRate = None' to use the assistant.
baudRate = 115200

config = {"apiKey": "AIzaSyCBicsFBflpqY8fAibtXLVI4UYOUxqzigE",
          "authDomain": "healthbot-eade0.firebaseapp.com",
          "databaseURL": "https://healthbot-eade0-default-rtdb.europe-west1.firebasedatabase.app",
          # projectId: "healthbot-eade0",
          "storageBucket": "healthbot-eade0.appspot.com", }

firebase = pyrebase.initialize_app(config)
db = firebase.database()


# NOTE the user must ensure that the serial port and baudrate are correct when # the values are hardcoded.
# See the serial port connection and baud rate in the arduino IDE. Below
# are examples of serial ports for different operating systems:
# arduinoPort = "/dev/ttyS80"           # On Linux
# arduinoPort = "/dev/cu.usbmodem1410"  # On macOS
# arduinoPort = "COMM4"                 # On Windows

startMarker = 60  # startmarker '<'
endMarker = 62  # endmarker '>'

'''
Waits for the start marker '<' to be received over the serial connection.
All bytes received until the end marker '>' are stored and returned. 
'''


def readFromArduino():
    global startMarker, endMarker
    ck = ""
    x = "z"  # any value that is not an end- or startMarker
    byteCount = -1  # to allow for the fact that the last increment will be one too many
    # wait for the start character
    while ord(x) != startMarker:
        x = ser.read()
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker:
            ck = ck + x.decode("utf-8")  # change for Python3
            byteCount += 1
        x = ser.read()
    return (ck)


'''
Waits until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
it also ensures that any bytes left over from a previous message are discarded
'''


def waitForArduino():
    global startMarker, endMarker
    msg = ""
    while msg.find("Arduino is ready") == -1:

        while ser.inWaiting() == 0:
            pass
        msg = readFromArduino()
        print(msg)  # python3 requires parenthesis
        print()


'''
Guided setup of the serial connection and baudrate. Serial connections are detected automatically. If the description includes 'arduino' the serial port is suggested as the correct one, otherwise the user selects from a list. 
Baudrate defaults to 9600 unless the user writes a number when prompted. 
'''


def setup():
    global arduinoPort
    global baudRate
    global logfile
    ports = list(serial.tools.list_ports.comports())
    counter = 1
    for p in ports:
        if "arduino" in p.description:
            arduinoPort = p.device
    print("Serial ports found:")
    for p in ports:
        print("(", counter, ") ", p, sep="")
        counter += 1
    print()
    if arduinoPort != None:
        print("Arduino detected at", ports[arduinoPort])
    if arduinoPort == None:
        print("No arduino detected. Please type a port number from the list above:")
        while True:
            port_num = input()
            try:
                port_num = int(port_num)
                if port_num > len(ports):
                    print("Please select a port from the list")
                else:
                    print()
                    print("Selected port:", ports[port_num-1])
                    arduinoPort = ports[port_num-1].device
                    break
            except:
                print('The variable is not a number')
    print()
    if baudRate == None:
        print("Default baud rate is 9600.")
        print("Press enter to use the default, or specify the baud rate:")

        while True:
            baud_rate = input()
            if baud_rate == '':
                baudRate = 9600
                break
            try:
                baud_rate = int(baud_rate)
                baudRate = baud_rate
                break
            except:
                print('The variable is not a number')
    print("")
    print("Default log filename is 'data.log'")
    print("Press enter to use the default, or type new filename:")
    filename = input()
    if filename == '':
        logfile = "data.log"
    else:
        logfile = filename

    # Define the logging behaviour. Note that rerunning the program will not
    # overwrite existing log data as a safety measure
    logging.basicConfig(filename=logfile, format='%(asctime)s,%(message)s',
                        datefmt='%Y-%m-%d-%H-%M-%S', level=logging.DEBUG)


'''
Handler for keyboard interupts. 
'''


def handler(_signal_received, _frame):
    ser.close
    print()
    print("Logging stopped")
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, handler)

    dataRecvd = "<12,5>"
    print("Data Received: " + dataRecvd)
    dataRecvd = dataRecvd.replace("<", "")
    dataRecvd = dataRecvd.replace(">", "")
    data = dataRecvd.split(",")
    apples = int(data[0])
    carrots = int(data[1])
    # logging.info(dataRecvd)
    db.child("data").update({"apple": apples})
    db.child("data").update({"carrot": carrots})
    # setup()
"""
    ser = serial.Serial(arduinoPort, baudRate)
    print("Serial port " + arduinoPort +
          " opened with Baudrate " + str(baudRate))

    waitForArduino()

    while True:
        while ser.inWaiting() == 0:
            pass

        # dataRecvd = readFromArduino()
        dataRecvd = "<12,5>"
        print("Data Received: " + dataRecvd)
        dataRecvd = dataRecvd.replace("<", "")
        dataRecvd = dataRecvd.replace(">", "")
        data = dataRecvd.split(",")
        apples = int(data[0])
        carrots = int(data[1])
        # logging.info(dataRecvd)
        db.child("data").update({"apple" : apples})
        db.child("data").update({"carrot" : carrots})
"""
