#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 12:17:37 2022

@author: ghiggi
"""
import os 
import fsspec

# Define file 
s3_fpath = "s3://noaa-goes16/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"

# Download in the ./data directory
fname = os.path.basename(s3_fpath)  
current_dir = os.path.dirname(os.path.realpath(__file__))
dst_fpath = os.path.join(current_dir, "data", fname)
print(dst_fpath)
fs = fsspec.filesystem('s3', anon=True)
fs.get(s3_fpath, dst_fpath)
