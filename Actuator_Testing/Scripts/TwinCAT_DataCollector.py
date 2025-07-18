import os
import pathlib
import pyads
import csv
from sys import exit
import datetime
from datetime import datetime as dt
#from time import monotonic
import time
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
from scipy.fft import fft, fftfreq
from scipy.signal import detrend
import numpy as np

#--------------------------------------------------------------------------------------------------------------#

def save_image(filename):
    
    # PdfPages is a wrapper around pdf 
    # file so there is no clash and create
    # files with no error.
    p = PdfPages(filename)
      
    # get_fignums Return list of existing 
    # figure numbers
    fig_nums = plt.get_fignums()  
    figs = [plt.figure(n) for n in fig_nums]
      
    # iterating over the numbers in list
    for fig in figs: 
        
        # and saving the files
        fig.savefig(p, format='pdf') 
      
    # close the object
    p.close()  
    
#--------------------------------------------------------------------------------------------------------------#

# Try to establish connection to HPT Teststand at known NetID; If unable, print error to console and exit
AMSAddr = "5.91.191.48.1.1"
Port = 851
try:
    print("Connecting to TwinCAT...")
    plc = pyads.Connection(AMSAddr, Port)
    plc.open()
    print("Local address: " + str(plc.get_local_address()) + "\n")
    print("CONNECTED TO TWINCAT\n")

except:
    print("Could not connect to hardpoint teststand.\n Check that the NetID of the local machine is entered correctly.\n Now exiting.")
    exit()

# Try to establsih ADS Symbol Transaction at server cycle frequency; If unable, print error to console and exit
try:
    pyads.constants.ADSTRANS_SERVERCYCLE = 3
except:
    print("ERROR SETTING SYMBOL READ TO SERVER CYCLE MODE")
    
# Create list of variable names to be block read from the PLC. All variables inside another function MUST be in the VAR_OUT section of the TwinCAT program
var_list = [
            'MAIN.xAxisConverted_g',
            'MAIN.yAxisConverted_g',
            'MAIN.zAxisConverted_g',
            'MAIN.xAxisConverted_mps2',
            'MAIN.yAxisConverted_mps2',
            'MAIN.zAxisConverted_mps2',
            'MAIN.pyLoadBusy',
            'MAIN.pyReady',
            'MAIN.saForceSetting',
            'MAIN.saPwm1',
            'MAIN.sigGenFreq',
            ]

symbols = plc.read_list_by_name(var_list)

# Try to open folder at PATH location; If it doesnt exisit, create it. If unable, print error to console, print current
# PATH locations for troubleshooting, and exit 
try:
    if not os.path.isdir("\\Vibration_Data"):
        os.mkdir("\\Vibration_Data") 

except:
    print("ERROR IN FOLDER ACCESS")
    print("Current script directory: " + str(pathlib.Path(__file__).parent.resolve()))
    print("Current working directory: " + str(pathlib.Path().resolve()) )
    exit()
       
# Create new timestamped filename
startDate = datetime.date.today()
startTime = dt.now()
freq = symbols['MAIN.sigGenFreq']
fileNameTS = startDate.strftime("%Y%m%d") + "_" + startTime.strftime("%Hh%Mm") + "_Vibration_Test_" + str(float(f"{freq:.2f}")) + "hz" 
pathName = '\\Vibration_Data'
fullFileName = pathName + "\\" + fileNameTS + ".csv"

# Use monotonic time so time never has a negative value
t0 = time.monotonic()
#t0 = dt.now()

# Start CSV index at zero
index = 0

# Create new CSV file at previously created folder location with PLC_file name. Create all appropriate field names in for
# CSV dictionary sample collection.

plc.write_by_name("MAIN.pyReady", True)

with open(fullFileName, 'w', newline='', encoding='utf-8') as PLC_file:

    # Define the field names to be used for the CSV. THIS MUST MATCH THE .writerow() CALL!!!
    fieldnames = [
                  #'Index',
                  'Seconds',
                  'xAxisConverted_g',
                  'yAxisConverted_g',
                  'zAxisConverted_g',
                  'xAxisConverted_mps2',
                  'yAxisConverted_mps2',
                  'zAxisConverted_mps2',
                  'saForceSetting',
                  'saPwm1',
                 ]
    
    # Create new instance of CSV writer, write dictionary defined above
    PLC_writer = csv.DictWriter(PLC_file, fieldnames=fieldnames)

    # Write header to CSV file
    PLC_writer.writeheader()

    print("Found TwinCAT symbols list...\n")
        
    # Start collecting data
    print(r"Starting data collection, saving file " + fileNameTS + r".csv at C:\Actuator_Data")
    print("DO NOT CLOSE THE CMD PROMPT, USE THE COLLECT DATA BUTTON AGAIN ON GUI TO END DATA COLLECTION!\n")
    print("Graphs will be automatically created once button is clicked off.")
    
    # Loop for t seconds pulling data from both AttoCubes and all PLC symbols, writing a new line to CSV file on each loop
    while (symbols['MAIN.pyLoadBusy'] == True): #and (symbols['MAIN.fbGetPcruData.bReadError'] == False):
        
        # Grab all symbols defined in var_list; if more are desired to be recorded, all that is recquired is to add the
        # PLC symbol name into var_list and call by name
        symbols = plc.read_list_by_name(var_list)
      
        # Increment index number
        #index = index + 1
        #time.sleep(0.01)
        #t1 = dt.now()
        
        # Write a new row in the CSV based on the fieldnames defined above
        PLC_writer.writerow({
            #'Index' : index,
            'Seconds': time.monotonic() - t0,
            #'Seconds': t1 - t0,
            'x_AxisConverted_g' : symbols['MAIN.xAxisConverted_g'],
            'y_AxisConverted_g' : symbols['MAIN.yAxisConverted_g'],
            'z_AxisConverted_g' : symbols['MAIN.zAxisConverted_g'],
            'x_AxisConverted_mps2' : symbols['MAIN.xAxisConverted_mps2'],
            'y_AxisConverted_mps2' : symbols['MAIN.yAxisConverted_mps2'],
            'z_AxisConverted_mps2' : symbols['MAIN.zAxisConverted_mps2'],
            'saForceSetting' : symbols['MAIN.saForceSetting'],
            'saPwm1' : symbols['MAIN.saPwm1'],
            })

# Close PLC connection
plc.close()
#--------------------------------------------------------------------------------------------------------------#

df = pd.read_csv(fullFileName, usecols=fieldnames, encoding='utf-8')

# Set the figure size
plt.rcParams["figure.figsize"] = [14.00, 7.00]
plt.rcParams["figure.autolayout"] = True
plt.rcParams.update({'figure.max_open_warning': 0})
fullFileNamePDF = fullFileName[:-4] + ".pdf"

#--------------------------------------------------------------------------------------------------------------#
plt.figure()
plt.plot(df['Seconds'], df['x_AxisConverted_g'], label='X-Axis')
plt.plot(df['Seconds'], df['y_AxisConverted_g'], label='Y-Axis')
#plt.plot(df['Seconds'], df['z_AxisConverted_g'], label='Z-Axis')
plt.legend()
plt.title('Accelerometer Readings')
plt.xlabel('Time [s]')
plt.ylabel('Acceleration [G]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['x_AxisConverted_g'], color='blue', label='X-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [g]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('X-Axis Accelerometer Readings [g]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['y_AxisConverted_g'], color='blue', label='Y-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [g]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('Y-Axis Accelerometer Readings [g]')

#--------------------------------------------------------------------------------------------------------------#
'''
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['z_AxisConverted_g'], color='blue', label='Z-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [g]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('Z-Axis Accelerometer Readings [g]')
'''
#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['x_AxisConverted_mps2'], color='blue', label='X-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('X-Axis Accelerometer Readings [m/s^2]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['y_AxisConverted_mps2'], color='blue', label='Y-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('Y-Axis Accelerometer Readings [m/s^2]')

#--------------------------------------------------------------------------------------------------------------#
'''
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['z_AxisConverted_mps2'], color='blue', label='Z-Axis')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Seconds'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('Z-Axis Accelerometer Readings [m/s^2]')
'''
#--------------------------------------------------------------------------------------------------------------#

sample_rate = 1000  # samples per second
time = df["Seconds"].loc[df["Seconds"] > 10]
signal = df["x_AxisConverted_g"].loc[df["Seconds"] > 10]
signal_detrend = detrend(df["x_AxisConverted_g"].loc[df["Seconds"] > 10], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
ax1.plot(df["Seconds"].loc[df["Seconds"] > 10], signal_detrend)
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('X-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()

#--------------------------------------------------------------------------------------------------------------#

time = df["Seconds"].loc[df["Seconds"] > 10]
signal = df["y_AxisConverted_g"].loc[df["Seconds"] > 10]
signal_detrend = detrend(df["y_AxisConverted_g"].loc[df["Seconds"] > 10], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
ax1.plot(df["Seconds"].loc[df["Seconds"] > 10], signal_detrend)
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Y-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()

#--------------------------------------------------------------------------------------------------------------#
'''
time = df["Seconds"].loc[df["Seconds"] > 10]
signal = df["z_AxisConverted_g"].loc[df["Seconds"] > 10]
signal_detrend = detrend(df["z_AxisConverted_g"].loc[df["Seconds"] > 10], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
ax1.plot(df["Seconds"].loc[df["Seconds"] > 10], signal_detrend)
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Z-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()
'''

# Save to multi-page PDF
save_image(fullFileNamePDF)
exit("Done.")