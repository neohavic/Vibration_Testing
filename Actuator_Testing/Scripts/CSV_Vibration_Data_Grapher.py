"""
-Stand alone automatic graphing/PDF creator utility for combined TC and RTD data
-Uses the PySimpleGUI library for easy selection of files and filename creation
-Current version of tool only works for combination TC/RTD files, files must NOT have anything other
than data column names in header for tool to work
    -Other Python programs written for thermometry work may need some code changes to conform to standard
    data structure so all tools can function together (to-do)

Created on Fri Jul 30 11:08:27 2023

@author: aeverman
"""

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
#from numpy.fft import fft, fftfreq
from scipy.fft import fft, fftfreq
from scipy.signal import detrend
from sys import exit

#-----------------------------------------------------------------------------------------------#

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
    

#-----------------------------------------------------------------------------------------------#

#fullFileName = "C:\\Vibration_Data\\FFT\\20250319_Vibration_Test_10.0hz_12h06m.csv"
#fullFileName = "C:\\Vibration_Data\\FFT\\20250319_Vibration_Test_100.0hz_12h20m.csv"
#fullFileName = "C:\\Vibration_Data\\FFT\\20250403_11h02m_Vibration_Test_100.0hz.csv"
fullFileName = "C:\\Vibration_Data\\FFT\\Export 1_20250415_14h_42m_26s.csv"

fullFileNamePDF = fullFileName[:-4] + ".pdf"

'''
# Read a CSV file
fieldnames = [
              'Index',
              'Seconds',
              'x_AxisConverted_g',
              'y_AxisConverted_g',
              'z_AxisConverted_g',
              'x_AxisConverted_mps2',
              'y_AxisConverted_mps2',
              'z_AxisConverted_mps2',
              'saForceSetting',
              'saPwm1',
             ]
'''

fieldnames = [
              'Name',
              'saForceSpX',
              'saPwm1',
              'xAxisConverted_g',
              'xAxisConverted_mps2',
              'yAxisConverted_g',
              'yAxisConverted_mps2',
              'zAxisConverted_g',
              'zAxisConverted_mps2',
             ]

df = pd.read_csv(fullFileName, usecols=fieldnames, encoding='utf-8')

# Set the figure size
plt.rcParams["figure.figsize"] = [14.00, 7.00]
plt.rcParams["figure.autolayout"] = True
plt.rcParams.update({'figure.max_open_warning': 0})
fullFileNamePDF = fullFileName[:-4] + ".pdf"

#--------------------------------------------------------------------------------------------------------------#
plt.figure()
plt.plot(df['Name'], df['xAxisConverted_g'], label='X-Axis')
plt.plot(df['Name'], df['yAxisConverted_g'], label='Y-Axis')
#plt.plot(df['Seconds'], df['zAxisConverted_g'], label='Z-Axis')
plt.legend()
plt.title('Accelerometer Readings')
plt.xlabel('Time [ms]')
plt.ylabel('Acceleration [G]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Name'], df['xAxisConverted_g'], color='blue', label='X-Axis')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Acceleration [g]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
#ax2 = ax1.twinx()
#ax2.plot(df['Name'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
#ax2.set_ylabel('PWM Duty Cycle %', color='red')
#ax2.tick_params(axis='y', labelcolor='red')
plt.title('X-Axis Accelerometer Readings [g]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Name'], df['yAxisConverted_g'], color='blue', label='Y-Axis')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Acceleration [g]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
#ax2 = ax1.twinx()
#ax2.plot(df['Name'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
#ax2.set_ylabel('PWM Duty Cycle %', color='red')
#ax2.tick_params(axis='y', labelcolor='red')
plt.title('Y-Axis Accelerometer Readings [g]')

#--------------------------------------------------------------------------------------------------------------#
'''
fig, ax1 = plt.subplots()
ax1.plot(df['Seconds'], df['zAxisConverted_g'], color='blue', label='Z-Axis')
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
ax1.plot(df['Name'], df['xAxisConverted_mps2'], color='blue', label='X-Axis')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
#ax2 = ax1.twinx()
#ax2.plot(df['Name'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
#ax2.set_ylabel('PWM Duty Cycle %', color='red')
#ax2.tick_params(axis='y', labelcolor='red')
plt.title('X-Axis Accelerometer Readings [m/s^2]')

#--------------------------------------------------------------------------------------------------------------#
fig, ax1 = plt.subplots()
ax1.plot(df['Name'], df['yAxisConverted_mps2'], color='blue', label='Y-Axis')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
#ax2 = ax1.twinx()
#ax2.plot(df['Name'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
#ax2.set_ylabel('PWM Duty Cycle %', color='red')
#ax2.tick_params(axis='y', labelcolor='red')
plt.title('Y-Axis Accelerometer Readings [m/s^2]')

#--------------------------------------------------------------------------------------------------------------#
'''
fig, ax1 = plt.subplots()
ax1.plot(df['Name'], df['zAxisConverted_mps2'], color='blue', label='Z-Axis')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Acceleration [m/s^2]', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax2 = ax1.twinx()
ax2.plot(df['Name'], df['saPwm1'], color='red', label='PWM Duty Cycle %')
ax2.set_ylabel('PWM Duty Cycle %', color='red')
ax2.tick_params(axis='y', labelcolor='red')
plt.title('Z-Axis Accelerometer Readings [m/s^2]')
'''
#--------------------------------------------------------------------------------------------------------------#

sample_rate = 1000  # samples per second
'''
time = df["Name"].loc[df["Name"] > 10000]
signal = df["xAxisConverted_g"].loc[df["Name"] > 10000]
signal_detrend = detrend(df["xAxisConverted_g"].loc[df["Name"] > 10000], type='linear')
'''

time = df["Name"]
signal = df["xAxisConverted_g"]
signal_detrend = detrend(df["xAxisConverted_g"], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
#ax1.plot(df["Name"].loc[df["Name"] > 10000], signal_detrend)
ax1.plot(df["Name"], signal_detrend)
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('X-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()

#--------------------------------------------------------------------------------------------------------------#
'''
time = df["Name"].loc[df["Name"] > 10000]
signal = df["yAxisConverted_g"].loc[df["Name"] > 10000]
signal_detrend = detrend(df["yAxisConverted_g"].loc[df["Name"] > 10000], type='linear')
'''
time = df["Name"]
signal = df["yAxisConverted_g"]
signal_detrend = detrend(df["yAxisConverted_g"], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
#ax1.plot(df["Name"].loc[df["Name"] > 10000], signal_detrend)
ax1.plot(df["Name"], signal_detrend)
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Y-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()

#--------------------------------------------------------------------------------------------------------------#
'''

#time = df["Name"].loc[df["Name"] > 10000].index[-1]
#signal = df["zAxisConverted_g"].loc[df["Name"] > 10000].index[-1]
#signal_detrend = detrend(df["zAxisConverted_g"].loc[df["Name"] > 10000].index[-1], type='linear')
time = df["Name"].loc[df["Name"]
signal = df["zAxisConverted_g"]
signal_detrend = detrend(df["zAxisConverted_g"], type='linear')

# Compute FFT
fft_signal = fft(signal_detrend)
frequencies = fftfreq(signal_detrend.size, d=1/sample_rate)

fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
#ax1.plot(df["Name"].loc[df["Name"] > 10000].index[-1], signal_detrend)
ax1.plot(df["Name"], signal_detrend)
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Z-Axis Acceleration [g]')
ax2.plot(frequencies[:signal_detrend.size//2], np.abs(fft_signal)[:signal_detrend.size//2])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
#plt.show()
'''

# Save to multi-page PDF
save_image(fullFileNamePDF)
exit("Done.")