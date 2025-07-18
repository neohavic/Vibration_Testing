# -*- coding: utf-8 -*-
"""
Created on Wed May 14 16:30:58 2025

@author: aeverman
"""

from cx_Freeze import setup, Executable

setup(
    name="Manifold_Data_FFT_Viewer",
    version="1.0",
    description="View vibration and FFT Data from valve manifold",
    executables=[Executable("FFT_Sanity_Test.py")],
)

print("done")