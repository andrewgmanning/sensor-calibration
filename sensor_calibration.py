# Andrew Manning, Sample Environments, Bragg Institute, November 2014
# andrewm@ansto.gov.au






###########################################
###########################################
###########################################
"""

SENSOR CALIBRATION PROGRAM STARTS HERE

"""
###########################################
###########################################
###########################################






import sys
import os
import optparse
import subprocess
import numpy as np
import random
import threading
import time
import serial
import numpy
import datetime
import time
import csv






def run():
    



    ###########################################
    """

    SETTING UP THE CONNECTION TO THE MERCURY

    """
    ###########################################

    print("\n**********************************************")
    print("*                                            *")   
    print("*             SENSOR CALIBRATION             *")
    print("*                                            *")
    print("**********************************************\n")

    now = datetime.datetime.now()
    print "\n\tDate and time is %s\n"% (now)
    timestring = "%s"%(now.strftime("%Y-%m-%d_%H_%M"))
    slash = os.path.normcase('/')

    serial_connection = serial.Serial()

    # default config - for LS 340 with PT100 sensor
    lakeshore = "340"                                           # serial (RJ11 -> RS232) port
    
    serial_connection.port = 0                                  # Port = COMS - 1, default is COMS = 1
    serial_connection.baudrate = 9600                           # RS232 is 9600 (LS 340), USB is 57600 (LS 336)
    serial_connection.bytesize = serial.EIGHTBITS               # 8None1
    serial_connection.parity = serial.PARITY_NONE
    serial_connection.stopbits = serial.STOPBITS_ONE
    serial_connection.timeout = 1                               # 1 s timeout
    serial_connection.writeTimeout = 1                          # 1 s timeout for write



    

    # Ask Lake Shore model (lakeshore) and connect to it via serial/USB
    dummy = False
    while dummy is False:
        print "Enter temperature controller model"
        TC_type = raw_input("Lake Shore [336] or [340], or Mercury [i]TC: ")
        dummy = TC_type == "336" or TC_type == "340" or TC_type == "i" or TC_type == "I"
        if dummy is True:
            break
        try:
            dummy is true
        except:
            print "-------> Try again, must be [336], [340] or [i]"

    commands = "LS"                         # Commands can be LS (Lake Shore) or M (Mercury)

    if TC_type == "336":
        serial_connection.baudrate = 57600
        serial_connection.bytesize = serial.SEVENBITS           # 7Odd1
        serial_connection.parity = serial.PARITY_ODD
        serial_connection.stopbits = serial.STOPBITS_ONE
        print "\n\tNOTE: Device must be set up for USB: Interface (6) > Enabled: USB\n"


    if TC_type == "i" or TC_type == "I":
        commands = "M" 
        serial_connection.baudrate = 115200
        serial_connection.bytesize = serial.EIGHTBITS               # 8None1
        serial_connection.parity = serial.PARITY_NONE
        serial_connection.stopbits = serial.STOPBITS_ONE
        print "\n\tNOTE: Device must be set up for USB: \n\tSettings>General>USB\n\tOn home page, press U in bottom left corner\n"


    COMS_num_imput = -1
    dummy = None
    while dummy is None:
        COMS_num_imput = raw_input("Enter COMS number for the serial connection: ")
        try:
            dummy = int(COMS_num_imput)
        except ValueError:
            print "-------> Try again, must be a number"

    COMS_num_imput = int(COMS_num_imput)
    
    serial_connection.port = COMS_num_imput - 1
    

    print("\n\t==============================================")
    print "\tConnecting to temperature controller via serial/USB\n"
    print "\tConnection parameters are COM%d, baud %d, databits per byte %d, \n\tparity %s, stopbit %d, read timeout %.2fs, write timeout %.2fs\n"%(serial_connection.port+1, serial_connection.baudrate, serial_connection.bytesize, serial_connection.parity, serial_connection.stopbits, serial_connection.timeout, serial_connection.writeTimeout)

    try:
        serial_connection.open()
    except e:
        print e
        raw_input("EXCEPTION THROWN - PRESS ENTER TO QUIT")
        return

    print "\n\tConnecting to %s. Connection state is "% (serial_connection.name) + str(serial_connection.isOpen())

    terminator = "\r\n"
    ## Figuring out correct terminator for iTC
    if commands == "M":
        dummy = None
        while dummy is None:
            try:
                serial_connection.write("*IDN?\r\n")
                reply = serial_connection.readline()
                serial_connection.write("*IDN?\r\n")
                reply = serial_connection.readline()
                reply_type = int(ord(reply[1]))
                terminator = "\r\n"
                print "\tTerminator is rn"
                dummy = True
                break 
            except:
                print "\tTerminator not rn"
            try:
                serial_connection.write("*IDN?\r")
                reply = serial_connection.readline()
                serial_connection.write("*IDN?\r")
                reply = serial_connection.readline()
                reply_type = int(ord(reply[1]))
                terminator = "\r"
                print "\tTerminator is r"
                dummy = True
                break 
            except:
                print "\tTerminator not r"
            try:
                serial_connection.write("*IDN?\n")
                reply = serial_connection.readline()
                serial_connection.write("*IDN?\n")
                reply = serial_connection.readline()
                reply_type = int(ord(reply[1]))
                terminator = "\n"
                print "\tTerminator is n"
                dummy = True
                break 
            except:
                print "\tTerminator not n"
            try:
                serial_connection.write("*IDN?\n\r")
                reply = serial_connection.readline()
                serial_connection.write("*IDN?\n\r")
                reply = serial_connection.readline()
                reply_type = int(ord(reply[1]))
                terminator = "\n\r"
                print "\tTerminator is nr"
                dummy = True
                break 
            except:
                print "\tTerminator not nr"

    serial_connection.write("*IDN?%s"% (terminator))
    reply = serial_connection.readline()
    if(reply==None) or reply == "":
        print "Serial connection failed"
        raw_input("Press enter to quit")
        return
    else:
        print "\tWinning! Connected to " + reply

    print("\t==============================================")

    # Lake Shore model 340 with thermocouple inputs can output some gibberish characters. Can use the reply message to identify which devices do this, to change the reading of their outputs accordingly


    start_index = 1             # where to start reading intype etc - TC likes 0, RTD likes 1
    gibberish = True
    reply_type = ord(reply[1])

    if (reply_type >= 65 and reply_type <= 90) or (reply_type >= 97 and reply_type <= 122):     # ord ranges for A-Z, a-z
        gibberish = False

    if gibberish == True:
        print "\n\n\tThis controller is outputting non-ASCII characters. \n\tBEWARE! Calibration may fail and need to be done manually.\n\n"
        start_index = 0

  





        
    # Ask sensor type (sensor) and load appropriate temperature calibration list as config .csv file

    num_sensors = 1         # Number of sensors to measure (not including pre-calibrated one)
    duration = 3600         # 1 hour
    sample_period = 60        # 1 sample per minute

    # Locations of the sensors - could be in DB1-8, MB on iTC, or ABCD on LS
    sensor_cal = "1"
    sensor1 = "2"
    sensor2 = "3"
    sensor3 = "4"

    sensor_type = "?"
    sensor_cal_serial = "?"
    sensor1_serial = "?"
    sensor2_serial = "?"
    sensor3_serial = "?"

    sensor_type = raw_input("\nEnter the type of sensor to calibrate: ")
    
    dummy = None
    while dummy is None:
        sensor_input = raw_input("Enter the number of sensors to test (not including pre-calibrated sensor): ")
        try:
            dummy = int(sensor_input)
        except ValueError:
            print "-------> Try again, must be a number"
    num_sensors = dummy

    dummy = False
    while dummy is False:
        print "\nEnter location of the calibrated sensor"
        sc_raw = raw_input("iTC - [M]B or DB[#], LS - [A/B/C/D]: ")
        sensor_cal_serial = raw_input("Enter the serial number for the calibrated sensor: ")
        dummy = sc_raw == "M" or sc_raw == "1" or sc_raw == "2" or sc_raw == "3" or sc_raw == "4" or sc_raw == "5" or sc_raw == "6" or sc_raw == "7" or sc_raw == "8" or sc_raw == "A" or sc_raw == "B" or sc_raw == "C" or sc_raw == "D" or sc_raw == "a" or sc_raw == "b" or sc_raw == "c" or sc_raw == "d"
        sensor_cal = sc_raw
        if sc_raw == "a" or sc_raw == "A":
            sensor_cal = "A"
        elif sc_raw == "b" or sc_raw == "B":
            sensor_cal = "B"
        elif sc_raw == "c" or sc_raw == "C":
            sensor_cal = "C"
        elif sc_raw == "d" or sc_raw == "D":
            sensor_cal = "D"
        if dummy is True:
            break
        try:
            dummy is true
        except:
            print "-------> Try again, must be [M], [1-8] or [A-D]" 

    dummy = False
    while dummy is False:
        print "Enter location of first sensor"
        s1_raw = raw_input("iTC - [M]B or DB[#], LS - [A/B/C/D]: ")
        sensor1_serial = raw_input("Enter the serial number for the first sensor: ")
        dummy = sc_raw == "M" or sc_raw == "1" or sc_raw == "2" or sc_raw == "3" or sc_raw == "4" or sc_raw == "5" or sc_raw == "6" or sc_raw == "7" or sc_raw == "8" or sc_raw == "A" or sc_raw == "B" or sc_raw == "C" or sc_raw == "D" or sc_raw == "a" or sc_raw == "b" or sc_raw == "c" or sc_raw == "d"
        sensor1 = s1_raw
        if s1_raw == "a" or s1_raw == "A":
            sensor1 = "A"
        elif s1_raw == "b" or s1_raw == "B":
            sensor1 = "B"
        elif s1_raw == "c" or s1_raw == "C":
            sensor1 = "C"
        elif s1_raw == "d" or s1_raw == "D":
            sensor1 = "D"
        if dummy is True:
            break
        try:
            dummy is true
        except:
            print "-------> Try again, must be [M], [1-8] or [A-D]" 


    if num_sensors > 1:
        dummy = False
        while dummy is False:
            print "Enter location of second sensor"
            s2_raw = raw_input("iTC - [M]B or DB[#], LS - [A/B/C/D]: ")
            sensor2_serial = raw_input("Enter the serial number for the second sensor: ")
            dummy = sc_raw == "M" or sc_raw == "1" or sc_raw == "2" or sc_raw == "3" or sc_raw == "4" or sc_raw == "5" or sc_raw == "6" or sc_raw == "7" or sc_raw == "8" or sc_raw == "A" or sc_raw == "B" or sc_raw == "C" or sc_raw == "D" or sc_raw == "a" or sc_raw == "b" or sc_raw == "c" or sc_raw == "d"
            sensor2 = s2_raw
            if s2_raw == "a" or s2_raw == "A":
                sensor2 = "A"
            elif s2_raw == "b" or s2_raw == "B":
                sensor2 = "B"
            elif s2_raw == "c" or s2_raw == "C":
                sensor2 = "C"
            elif s2_raw == "d" or s2_raw == "D":
                sensor2 = "D"
            if dummy is True:
                break
            try:
                dummy is true
            except:
                print "-------> Try again, must be [M], [1-8] or [A-D]" 
  

    if num_sensors > 2:
        dummy = False
        while dummy is False:
            print "Enter location of third sensor"
            s3_raw = raw_input("iTC - [M]B or DB[#], LS - [A/B/C/D]: ")
            sensor3_serial = raw_input("Enter the serial number for the third sensor: ")
            dummy = sc_raw == "M" or sc_raw == "1" or sc_raw == "2" or sc_raw == "3" or sc_raw == "4" or sc_raw == "5" or sc_raw == "6" or sc_raw == "7" or sc_raw == "8" or sc_raw == "A" or sc_raw == "B" or sc_raw == "C" or sc_raw == "D" or sc_raw == "a" or sc_raw == "b" or sc_raw == "c" or sc_raw == "d"
            sensor3 = s3_raw
            if s3_raw == "a" or s3_raw == "A":
                sensor3 = "A"
            elif s3_raw == "b" or s3_raw == "B":
                sensor3 = "B"
            elif s3_raw == "c" or s3_raw == "C":
                sensor3 = "C"
            elif s3_raw == "d" or s3_raw == "D":
                sensor3 = "D"
            if dummy is True:
                break
            try:
                dummy is true
            except:
                print "-------> Try again, must be [M], [1-8] or [A-D]" 


    dummy = None
    while dummy is None:
        dur_input = raw_input("\nEnter the duration of the test in minutes: ")
        try:
            dummy = int(dur_input)
        except ValueError:
            print "-------> Try again, must be a number"
    duration = dummy * 60

    dummy = None
    while dummy is None:
        sample_input = raw_input("Enter the period in seconds between samples: ")
        try:
            dummy = int(sample_input)
        except ValueError:
            print "-------> Try again, must be a number"
    sample_period = dummy

    number_measurements = duration/sample_period























    ###########################################
    """

    GETTING TEMPERATURE MEASUREMENTS

    """
    ###########################################
    
    print("\n==============================================\n")
    print("      To end measurement, press Ctrl + C\n")
    print("==============================================\n")

    temp_meas_vec_calib = np.zeros( (number_measurements+1, 1) )
    temp_meas_vec_1 = np.zeros( (number_measurements+1, 1) )
    temp_meas_vec_2 = np.zeros( (number_measurements+1, 1) )
    temp_meas_vec_3 = np.zeros( (number_measurements+1, 1) )

    volt_meas_vec_calib = np.zeros( (number_measurements+1, 1) )
    volt_meas_vec_1 = np.zeros( (number_measurements+1, 1) )
    volt_meas_vec_2 = np.zeros( (number_measurements+1, 1) )
    volt_meas_vec_3 = np.zeros( (number_measurements+1, 1) )

    res_meas_vec_calib = np.zeros( (number_measurements+1, 1) )
    res_meas_vec_1 = np.zeros( (number_measurements+1, 1) )
    res_meas_vec_2 = np.zeros( (number_measurements+1, 1) )
    res_meas_vec_3 = np.zeros( (number_measurements+1, 1) )
    
    quit_flag = 0

    temp_query_2_c = "A" # Will be unique to each channel
    temp_query_2_1 = "B"
    temp_query_2_2 = "C"
    temp_query_2_3 = "D"

    if commands == "LS":
        temp_query_2_c = sensor_cal
        temp_query_2_1 = sensor1
        temp_query_2_2 = sensor2
        temp_query_2_3 = sensor3

    if commands == "M":
        if sensor_cal == "M":
            temp_query_2_c = "MB1"
        if sensor1 == "M":
            temp_query_2_1 = "MB1"
        if sensor2 == "M":
            temp_query_2_2 = "MB1"
        if sensor3 == "M":
            temp_query_2_3 = "MB1"

        if sensor_cal == "1":
            temp_query_2_c = "DB1"
        if sensor1 == "1":
            temp_query_2_1 = "DB1"
        if sensor2 == "1":
            temp_query_2_2 = "DB1"
        if sensor3 == "1":
            temp_query_2_3 = "DB1"

        if sensor_cal == "2":
            temp_query_2_c = "DB2"
        if sensor1 == "2":
            temp_query_2_1 = "DB2"
        if sensor2 == "2":
            temp_query_2_2 = "DB2"
        if sensor3 == "2":
            temp_query_2_3 = "DB2"

        if sensor_cal == "3":
            temp_query_2_c = "DB3"
        if sensor1 == "3":
            temp_query_2_1 = "DB3"
        if sensor2 == "3":
            temp_query_2_2 = "DB3"
        if sensor3 == "3":
            temp_query_2_3 = "DB3"

        if sensor_cal == "4":
            temp_query_2_c = "DB4"
        if sensor1 == "4":
            temp_query_2_1 = "DB4"
        if sensor2 == "4":
            temp_query_2_2 = "DB4"
        if sensor3 == "4":
            temp_query_2_3 = "DB4"

        if sensor_cal == "5":
            temp_query_2_c = "DB5"
        if sensor1 == "5":
            temp_query_2_1 = "DB5"
        if sensor2 == "5":
            temp_query_2_2 = "DB5"
        if sensor3 == "5":
            temp_query_2_3 = "DB5"

        if sensor_cal == "6":
            temp_query_2_c = "DB6"
        if sensor1 == "6":
            temp_query_2_1 = "DB6"
        if sensor2 == "6":
            temp_query_2_2 = "DB6"
        if sensor3 == "6":
            temp_query_2_3 = "DB6"

        if sensor_cal == "7":
            temp_query_2_c = "DB7"
        if sensor1 == "7":
            temp_query_2_1 = "DB7"
        if sensor2 == "7":
            temp_query_2_2 = "DB7"
        if sensor3 == "7":
            temp_query_2_3 = "DB7"

        if sensor_cal == "8":
            temp_query_2_c = "DB8"
        if sensor1 == "8":
            temp_query_2_1 = "DB8"
        if sensor2 == "8":
            temp_query_2_2 = "DB8"
        if sensor3 == "8":
            temp_query_2_3 = "DB8"




        
    # Lake Shore - serial_connection.write("KRDG? A\r\n")
    temp_query_1 = "KRDG? "
    volt_query_1 = "SRDG? "
    temp_query_3 = ""
    volt_query_3 = ""
    res_query_1 = "READ:DEV:"
    res_query_3 = ".T1:TEMP:SIG:RES"

    read_mode_1 = "VOLT"
    read_mode_2 = "VOLT"
    read_mode_3 = "VOLT"
    read_mode_c = "VOLT"

    # Mercury - serial_connection.write("READ:DEV:DB8.T1:TEMP:SIG:TEMP\r\n")
    if commands == "M":
        temp_query_1 = "READ:DEV:"
        volt_query_1 = "READ:DEV:"
        temp_query_3 = ".T1:TEMP:SIG:TEMP"
        volt_query_3 = ".T1:TEMP:SIG:VOLT"

        # Figure out what kind of sensor is in each slot        
        serial_connection.write("READ:DEV:%s.T1:TEMP:TYPE\r\n"% (temp_query_2_c))
        reply = serial_connection.readline()
        if  reply[26:-1] == "PTC" or reply[26:-1] == "NTC":
            read_mode_c = "RES"
        serial_connection.write("READ:DEV:%s.T1:TEMP:TYPE\r\n"% (temp_query_2_1))
        reply = serial_connection.readline()
        if  reply[26:-1] == "PTC" or reply[26:-1] == "NTC":
            read_mode_1 = "RES"
        if num_sensors > 1:
            serial_connection.write("READ:DEV:%s.T1:TEMP:TYPE\r\n"% (temp_query_2_2))
            reply = serial_connection.readline()
            if  reply[26:-1] == "PTC" or reply[26:-1] == "NTC":
                read_mode_2 = "RES"
        if num_sensors > 2:
            serial_connection.write("READ:DEV:%s.T1:TEMP:TYPE\r\n"% (temp_query_2_3))
            reply = serial_connection.readline()
            if  reply[26:-1] == "PTC" or reply[26:-1] == "NTC":
                read_mode_3 = "RES"
                          
    # The measurement loop

    num_measured = 0
    raw_input("\n\nPress Enter to begin\n\n")
    for i in range(0,number_measurements):
        if commands == "LS":
            serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_c,temp_query_3,terminator))
            reply = serial_connection.readline()
            temp_meas_vec_calib[i,0] = float(reply[0:-2])
            serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_c,volt_query_3,terminator))
            reply = serial_connection.readline()
            volt_meas_vec_calib[i,0] = float(reply[0:-2])
        if commands == "M":
            serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_c,temp_query_3,terminator))
            reply = serial_connection.readline()
            temp_meas_vec_calib[i,0] = float(reply[30:-2])
            if read_mode_c == "VOLT":
                serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_c,volt_query_3,terminator))
                reply = serial_connection.readline()
                volt_meas_vec_calib[i,0] = float(reply[30:-3])
            elif read_mode_c == "RES":
                serial_connection.write("%s%s%s%s"% (res_query_1,temp_query_2_c,res_query_3,terminator))
                reply = serial_connection.readline()
                res_meas_vec_calib[i,0] = float(reply[29:-3])

        if commands == "LS":
            serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_1,temp_query_3,terminator))
            reply = serial_connection.readline()
            temp_meas_vec_1[i,0] = float(reply[0:-2])
            serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_1,volt_query_3,terminator))
            reply = serial_connection.readline()
            volt_meas_vec_1[i,0] = float(reply[0:-2])
        if commands == "M":
            serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_1,temp_query_3,terminator))
            reply = serial_connection.readline()
            temp_meas_vec_1[i,0] = float(reply[30:-2])
            if read_mode_1 == "VOLT":
                serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_1,volt_query_3,terminator))
                reply = serial_connection.readline()
                volt_meas_vec_1[i,0] = float(reply[30:-3])
            elif read_mode_1 == "RES":
                serial_connection.write("%s%s%s%s"% (res_query_1,temp_query_2_1,res_query_3,terminator))
                reply = serial_connection.readline()
                res_meas_vec_1[i,0] = float(reply[29:-3])

        if num_sensors > 1:
            if commands == "LS":
                serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_2,temp_query_3,terminator))
                reply = serial_connection.readline()
                temp_meas_vec_2[i,0] = float(reply[0:-2])
                serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_2,volt_query_3,terminator))
                reply = serial_connection.readline()
                volt_meas_vec_2[i,0] = float(reply[0:-2])
            if commands == "M":
                serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_2,temp_query_3,terminator))
                reply = serial_connection.readline()
                temp_meas_vec_2[i,0] = float(reply[30:-2])
                if read_mode_2 == "VOLT":
                    serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_2,volt_query_3,terminator))
                    reply = serial_connection.readline()
                    volt_meas_vec_2[i,0] = float(reply[30:-3])
                elif read_mode_2 == "RES":
                    serial_connection.write("%s%s%s%s"% (res_query_1,temp_query_2_2,res_query_3,terminator))
                    reply = serial_connection.readline()
                    res_meas_vec_2[i,0] = float(reply[29:-3])

        if num_sensors > 2:
            if commands == "LS":
                serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_3,temp_query_3,terminator))
                reply = serial_connection.readline()
                temp_meas_vec_3[i,0] = float(reply[0:-2])
                serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_3,volt_query_3,terminator))
                reply = serial_connection.readline()
                volt_meas_vec_3[i,0] = float(reply[0:-2])
            if commands == "M":
                serial_connection.write("%s%s%s%s"% (temp_query_1,temp_query_2_3,temp_query_3,terminator))
                reply = serial_connection.readline()
                temp_meas_vec_3[i,0] = float(reply[30:-2])
                if read_mode_3 == "VOLT":
                    serial_connection.write("%s%s%s%s"% (volt_query_1,temp_query_2_3,volt_query_3,terminator))
                    reply = serial_connection.readline()
                    volt_meas_vec_3[i,0] = float(reply[30:-3])
                elif read_mode_3 == "RES":
                    serial_connection.write("%s%s%s%s"% (res_query_1,temp_query_2_3,res_query_3,terminator))
                    reply = serial_connection.readline()
                    res_meas_vec_3[i,0] = float(reply[29:-3])

        if num_sensors == 1:
            print "Time = %d seconds, cal sensor = %.3f K, sensor 1 = %.3f K"% (i * sample_period,temp_meas_vec_calib[i,0],temp_meas_vec_1[i,0])
        if num_sensors == 2:
            print "Time = %d seconds, cal sensor = %.3f K, sensor 1 = %.3f K, sensor 2 = %.3f K"% (i * sample_period,temp_meas_vec_calib[i,0],temp_meas_vec_1[i,0],temp_meas_vec_2[i,0])
        if num_sensors == 3:
            print "Time = %d seconds, cal sensor = %.3f K, sensor 1 = %.3f K, sensor 2 = %.3f K, sensor 3 = %.3f K"% (i * sample_period,temp_meas_vec_calib[i,0],temp_meas_vec_1[i,0],temp_meas_vec_2[i,0],temp_meas_vec_3[i,0])

        # Allow user to quit calibration
        for sec in range(0,sample_period):
            try:
                time.sleep(1)
            except (KeyboardInterrupt,SystemExit):
                raw_input("\n\nSensor calibration terminated\n\n")
                quit_flag = 1
                break
            except:
                print "Something went wrong... Quitting"
                quit_flag = 1
                break

        num_measured = i
    
        if quit_flag == 1:
            break

        
    # Calculating data for calibration

    diff_1 = abs(temp_meas_vec_1[0:num_measured,0] - temp_meas_vec_calib[0:num_measured,0])
    max_1 = np.amax(diff_1)
    ave_1 = np.mean(diff_1)
    
    print "Maximum different for sensor 1 is %.3f, mean difference is %.3f" %(max_1,ave_1) 

    max_2 = 0
    ave_2 = 0
    max_3 = 0
    ave_3 = 0
    diff_2 = 0
    diff_3 = 0

    if num_sensors > 1:
        diff_2 = abs(temp_meas_vec_2[0:num_measured,0] - temp_meas_vec_calib[0:num_measured,0])
        max_2 = np.amax(diff_2)
        ave_2 = np.mean(diff_2)
        print "Maximum different for sensor 2 is %.3f, mean difference is %.3f" %(max_2,ave_2) 

    if num_sensors > 2:
        diff_3 = abs(temp_meas_vec_3[0:num_measured,0] - temp_meas_vec_calib[0:num_measured,0])
        max_3 = np.amax(diff_3)
        ave_3 = np.mean(diff_3)
        print "Maximum different for sensor 3 is %.3f, mean difference is %.3f" %(max_3,ave_3) 

        





    # Write out results

    filename = ".%ssensorCalLogs%s%s_output_summary.csv"% (slash, slash, timestring)
    f = open(filename,'w')
    f.write("Calibrated sensor is Cernox with serial %s\n"% (sensor_cal_serial))
    f.write("Sensor 1 is %s with serial %s\n"% (sensor_type,sensor1_serial))
    f.write("Maximum different for sensor 1 is %.3f, mean difference is %.3f K\n" %(max_1,ave_1))
    if num_sensors > 1:
        f.write("Sensor 2 is %s with serial %s\n"% (sensor_type,sensor2_serial))
        f.write("Maximum different for sensor 2 is %.3f, mean difference is %.3f K\n" %(max_2,ave_2))
    if num_sensors > 2:
        f.write("Sensor 3 is %s with serial %s\n"% (sensor_type,sensor3_serial))
        f.write("Maximum different for sensor 3 is %.3f, mean difference is %.3f K\n" %(max_3,ave_3))    
    f.close()


    
    filename = ".%ssensorCalLogs%s%s_output_A.csv"% (slash, slash, timestring)
    f = open(filename,'w')
    f.write("Sensor 1 type, %s\n"% (sensor_type))
    f.write("Sensor 1 serial, %s\n"% (sensor1_serial))
    f.write("Time (sec), Measured T (K), Difference T (K), Voltage (V)")
    if commands == "M":
        f.write(", Resistance (ohm)")
    f.write("\n")
    for n in range(0, num_measured):
        f.write("%d,%.3f,%.3f,%.5f"% (int(n * sample_period),float(temp_meas_vec_1[n,0]),float(diff_1[n]),float(volt_meas_vec_1[n,0])))
        if commands == "M":
            f.write(",%.5f"% (float(res_meas_vec_1[n,0])))
        f.write("\n")
    f.close()


    if num_sensors > 1:
        filename = ".%ssensorCalLogs%s%s_output_B.csv"% (slash, slash, timestring)
        f = open(filename,'w')
        f.write("Sensor 2 type, %s\n"% (sensor_type))
        f.write("Sensor 2 serial, %s\n"% (sensor2_serial))
        f.write("Time (sec), Measured T (K), Difference T (K), Voltage (V)")
        if commands == "M":
            f.write(", Resistance (ohm)")
        f.write("\n")
        for n in range(0, num_measured):
            f.write("%d,%.3f,%.3f,%.5f"% (int(n * sample_period),float(temp_meas_vec_2[n,0]),float(diff_2[n]),float(volt_meas_vec_2[n,0])))
            if commands == "M":
                f.write(",%.5f"% (float(res_meas_vec_2[n,0])))
            f.write("\n")
        f.close()

    if num_sensors > 2:
        filename = ".%ssensorCalLogs%s%s_output_C.csv"% (slash, slash, timestring)
        f = open(filename,'w')
        f.write("Sensor 3 type, %s\n"% (sensor_type))
        f.write("Sensor 3 serial, %s\n"% (sensor2_serial))
        f.write("Time (sec), Measured T (K), Difference T (K), Voltage (V)")
        if commands == "M":
            f.write(", Resistance (ohm)")
        f.write("\n")
        for n in range(0, num_measured):
            f.write("%d,%.3f,%.3f,%.5f"% (int(n * sample_period),float(temp_meas_vec_3[n,0]),float(diff_3[n]),float(volt_meas_vec_3[n,0])))
            if commands == "M":
                f.write(",%.5f"% (float(res_meas_vec_3[n,0])))
            f.write("\n")
        f.close()
    
    filename = ".%ssensorCalLogs%s%s_output_cal.csv"% (slash, slash, timestring)
    f = open(filename,'w')
    f.write("Calibrated sensor type, %s\n"% (sensor_type))
    f.write("Calibrated sensor serial, %s\n"% (sensor_cal_serial))
    f.write("Time (sec), Measured T (K), Voltage (V)")
    if commands == "M":
        f.write(", Resistance (ohm)")
    f.write("\n")
    for n in range(0, num_measured):
        f.write("%d,%.3f,%.5f"% (int(n * sample_period),float(temp_meas_vec_calib[n,0]),float(volt_meas_vec_calib[n,0])))
        if commands == "M":
            f.write(",%.5f"% (float(res_meas_vec_calib[n,0])))
        f.write("\n")
    f.close()
  
    raw_input("\n\n\nEnd of calibration. Outputs saved in dataLogs folder.\n\n\n")
        
    dummy = False
    while dummy is False:
        quitstring = raw_input("Press [Q] to quit: ")
        dummy = quitstring == "Q" or quitstring == "q"
        if dummy is True:
            return
        try:
            dummy is true
        except:
            print "-------> Press [Q] to quit: "


if __name__ == "__main__":

    run()
