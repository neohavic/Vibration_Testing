# -*- coding: utf-8 -*-
"""
Created on Tue May 20 13:06:56 2025

@author: aeverman
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 12:43:36 2025

@author: aeverman
"""

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
#from numpy.fft import fft, fftfreq
from scipy.fft import rfft, rfftfreq
from scipy.signal import detrend
import mplcursors
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy.signal.windows import hamming

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

def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    normalized_arr = (arr - min_val) / (max_val - min_val)
    return normalized_arr

#-----------------------------------------------------------------------------------------------#

def change_annotation_font_size(sel):
    sel.annotation.set_fontsize(25)
    
#-----------------------------------------------------------------------------------------------#

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

#fullFileName = "C:\\Vibration_Data\\FFT\\20250319_Vibration_Test_10.0hz_12h06m.csv"
#fullFileName = "C:\\Vibration_Data\\FFT\\20250319_Vibration_Test_100.0hz_12h20m.csv"
#fullFileName = "C:\\Vibration_Data\\FFT\\20250403_11h02m_Vibration_Test_100.0hz.csv"
#fullFileName = "C:\\Vibration_Data\\Scope_Project_1Hz.csv"
fullFileName = filename = askopenfilename(filetypes=[("Image files", "*.csv"), ("All Files", "*.*")])

fullFileNamePDF = fullFileName[:-4] + "_FFT_with_windowing_analysis.pdf"

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
#df.drop(list(range(0, 13281)), inplace=True)
#df.drop(list(range(123278, 133300)), inplace=True)

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
signal_mean = signal.mean()
signal = signal - signal_mean
time = df["Name"]
N = signal.size

# Apply Hamming window
window = np.hanning(len(signal))
windowed_signal = signal * window

# Compute the FFT
xf = rfftfreq(N, d=T)
yf = normalize_array(np.abs(rfft(signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, windowed_signal)
# Add labels and title
plt.xlabel('Time [mS]')
plt.ylabel('PWM %')
plt.title('Windowed PWM Signal')

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
plt.title('PWM Signal FFT')

#-----------------------------------------------------------------------------------------------#

# PLot the X-axis vibrational data and corresponding FFT
#signal = df["xAxisConverted_mps2"]
signal = detrend(df["xAxisConverted_g"], type='linear')
signal_mean = signal.mean()
signal = signal - signal_mean
time = df["Name"] # Only called once, no need to do it multiple times
# Apply Hamming window
window = np.hanning(len(signal))
windowed_signal = signal * window
N = windowed_signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(windowed_signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, windowed_signal)
# Add labels and title
plt.xlabel('Time [mS]')
plt.ylabel('Acceleration [m/s^2]')
plt.title('X-Axis Accelerometer Readings [m/s^2]')

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)
# %%
ax1.xaxis.set_ticks(np.arange(0, 500, 50))

# Annotate the maximum point
plt.annotate(
    f'Max: ({max_x:.2f}, {max_y:.2f})',
    xy=(max_x, max_y),
    xytext=(max_x + 15, max_y),  # Adjust text position as needed
    arrowprops=dict(facecolor='red', arrowstyle='->'),
)

# Add labels and title
plt.xlabel('Frequency [Hz]')
plt.ylabel('Normalized Magnitude')
plt.title('X-Axis Accelerometer FFT')

#-----------------------------------------------------------------------------------------------#

# PLot the Y-axis vibrational data and corresponding FFT
signal = df["yAxisConverted_mps2"]
signal_mean = signal.mean()
signal = signal - signal_mean
# Apply Hamming window
window = np.hanning(len(signal))
windowed_signal = signal * window
N = windowed_signal.size

# Compute the FFT
xf = rfftfreq(N, T)
yf = normalize_array(np.abs(rfft(windowed_signal)))

fig, ax1 = plt.subplots()
ax1.plot(time, windowed_signal)
# Add labels and title
plt.xlabel('Time [mS]')
plt.ylabel('Acceleration [m/s^2]')
plt.title('Y-Axis Accelerometer Readings [m/s^2]')

# Find the index of the maximum y-value
max_index = np.argmax(yf)
max_x = xf[max_index]
max_y = yf[max_index]

fig, ax1 = plt.subplots()
ax1.plot(xf, yf)
ax1.xaxis.set_ticks(np.arange(0, 500, 50))
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
plt.title('Y-Axis Accelerometer FFT')

#-----------------------------------------------------------------------------------------------#
'''
# PLot the Z-axis vibrational data and corresponding FFT
#signal = df["zAxisConverted_mps2"]
signal = detrend(df["zAxisConverted_g"], type='linear')
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
plt.title('Z-Axis Accelerometer Readings [m/s^2]')

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

cursor = mplcursors.cursor(hover=True)
cursor.connect("add", change_annotation_font_size)
plt.show()
save_image(fullFileNamePDF)