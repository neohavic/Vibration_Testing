import os
import pathlib
import pyads
import csv
from sys import exit
import datetime
from datetime import datetime as dt
import time
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import detrend
import numpy as np
from scipy.fft import rfft, rfftfreq
import mplcursors

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

def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    normalized_arr = (arr - min_val) / (max_val - min_val)
    return normalized_arr

#-----------------------------------------------------------------------------------------------#
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
        
        # Write a new row in the CSV based on the fieldnames defined above
        PLC_writer.writerow({
            'Seconds': time.monotonic() - t0,
            'saForceSetting' : symbols['MAIN.saForceSetting'],
            'saPwm1' : symbols['MAIN.saPwm1'],
            'xAxisConverted_g' : symbols['MAIN.xAxisConverted_g'],
            'xAxisConverted_mps2' : symbols['MAIN.xAxisConverted_mps2'],
            'yAxisConverted_g' : symbols['MAIN.yAxisConverted_g'],
            'yAxisConverted_mps2' : symbols['MAIN.yAxisConverted_mps2'],
            'zAxisConverted_g' : symbols['MAIN.zAxisConverted_g'],
            'zAxisConverted_mps2' : symbols['MAIN.zAxisConverted_mps2'],
            })

# Close PLC connection
plc.close()
#--------------------------------------------------------------------------------------------------------------#

fullFileNamePDF = fullFileName[:-4] + ".pdf"

df = pd.read_csv(fullFileName, usecols=fieldnames, encoding='utf-8')
df.drop(list(range(0, 13281)), inplace=True)
df.drop(list(range(123278, 133300)), inplace=True)

# Set the figure size
plt.rcParams["figure.figsize"] = [14.00, 7.00]
plt.rcParams["figure.autolayout"] = True

#-----------------------------------------------------------------------------------------------#

# Sampling rate and time vector for FFT
sr = 1000  # Sampling rate in samples/Sec
T = 1/sr # Sample spacing

#-----------------------------------------------------------------------------------------------#

# Plot the signal used from the PWM signal sent to the valve
signal = df["saPwm1"]
time = df["Seconds"]
N = signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, signal)
# Add labels and title
plt.xlabel('Time [S]')
plt.ylabel('PWM %')

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)
# Annotate the maximum point
plt.annotate(
    f'Max: ({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),
    xytext=(max_x + 15, max_y),  # Adjust text position as needed
    arrowprops=dict(facecolor='red', arrowstyle='->'),
)
# Add labels and title
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')

#-----------------------------------------------------------------------------------------------#

# PLot the X-axis vibrational data and corresponding FFT
signal = df["xAxisConverted_mps2"]
time = df["Seconds"] # Only called once, no need to do it multiple times
N = signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, signal)
# Add labels and title
plt.xlabel('Time [S]')
plt.ylabel('Acceleration [m/s^2]')

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)

# Annotate the maximum point
plt.annotate(
    f'Max: ({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),
    xytext=(max_x + 15, max_y),  # Adjust text position as needed
    arrowprops=dict(facecolor='red', arrowstyle='->'),
)

# Add labels and title
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')

#-----------------------------------------------------------------------------------------------#

# PLot the Y-axis vibrational data and corresponding FFT
signal = df["yAxisConverted_mps2"]
N = signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, signal)
# Add labels and title
plt.xlabel('Time [S]')
plt.ylabel('Acceleration [m/s^2]')

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)

# Annotate the maximum point
plt.annotate(
    f'Max: ({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),
    xytext=(max_x + 15, max_y),  # Adjust text position as needed
    arrowprops=dict(facecolor='red', arrowstyle='->'),
)

# Add labels and title
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')

#-----------------------------------------------------------------------------------------------#
'''
# PLot the Z-axis vibrational data and corresponding FFT
signal = df["zAxisConverted_mps2"]
N = signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, signal)
#plt.xlim(13281, 123277)
# Add labels and title
plt.xlabel('Time [S]')
plt.ylabel('Acceleration [m/s^2'])

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)

# Annotate the maximum point
plt.annotate(
    f'Max: ({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),
    xytext=(max_x + 15, max_y),  # Adjust text position as needed
    arrowprops=dict(facecolor='red', arrowstyle='->'),
)

# Add labels and title
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')

# Create interactive graph
df2 = pd.DataFrame(zip(xf, yf), columns=['xf','yf'])
fig = px.line(df2, x="xf", y="yf", title='FFT Frequencies')

'''
#-----------------------------------------------------------------------------------------------#
fig.show()
mplcursors.cursor()
save_image(fullFileNamePDF)