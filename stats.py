#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 12:39:33 2022

@author: ghiggi
"""
import os
import numpy as np
import xarray as xr
 

# Define directory where saving results
base_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_io_benchmark/"
 

# Define filepaths
fname = "OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
local_fpath = os.path.join(base_dir, "data", fname)


ds = xr.open_dataset(local_fpath, chunks=chunks_dict)
%timeit np.isnan(ds['Rad'].data).compute()

ds['Rad'].is_finite()

n_nan = np.count_nonzero(np.isnan(ds['Rad'].data))
n_nan/ds['Rad'].size*100 # 21 % is nan 
