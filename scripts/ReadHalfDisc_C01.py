#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 15:12:48 2022

@author: ghiggi
"""
###################
### Benchmarks ####
###################
import os
import json 
import datetime
import fsspec
import time
import requests
# import netCDF4
# import h5netcdf
import xarray as xr
from io import BytesIO

# results_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_io_benchmark/results/"
# data_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_io_benchmark/data/"

# Define directory where saving results
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
results_dir = os.path.join(base_dir, "results")
data_dir = os.path.join(base_dir, "data")

# Define filepaths
local_fpath = os.path.join(data_dir, "OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc")
reference_fpath = os.path.join(data_dir, "OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc.json")

http_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
nc_mode_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc#mode=bytes"
s3_fpath = "s3://noaa-goes16/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"

# Define experiment name
exp_name = "ReadQuarterDisc_C01"

# -----------------------------------
# Define dask chunking
chunks_dict = {'Rad': (226 * 2, 226 * 2)}

# Define custom operation
def apply_custom_fun(ds):
    shape = ds['Rad'].shape
    half_da = ds['Rad'].isel(y=slice(0, int(shape[0]/2)), x=slice(0, int(shape[1]/2)))
    dummy = half_da.plot.imshow()
    return None


# Define filename where saving results
current_time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
result_fpath = os.path.join(results_dir, exp_name + "_" + current_time + ".json")

# Initialize dictionary
result_dict = {}

####--------------------------------------------------------------------------
#### Local (numpy)
t_i = time.time()
ds = xr.open_dataset(local_fpath)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['Local (Numpy)'] = t_elapsed
print(t_elapsed)  # 3.2 - 3.7 s

####------------------------------------------------
#### Local (dask)
t_i = time.time()
ds = xr.open_dataset(local_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['Local (Dask)'] = t_elapsed
print(t_elapsed)  # 4.45 s

####------------------------------------------------
#### HTTPS + bytesIO (numpy)
t_i = time.time()
resp = requests.get(http_fpath)
f_obj = BytesIO(resp.content)
ds = xr.open_dataset(f_obj)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['HTTPS + bytesIO (Numpy)'] = t_elapsed
print(t_elapsed)  # 7.0 - 7.4 s

####------------------------------------------------
#### HTTPS + bytesIO (dask)
t_i = time.time()
resp = requests.get(http_fpath)
f_obj = BytesIO(resp.content)
ds = xr.open_dataset(f_obj, chunks=chunks_dict)
# nc = netCDF4.Dataset('dummy_name', memory=resp.content)
# f_obj = xr.backends.NetCDF4DataStore(nc)
# ds = xr.open_dataset(f_obj)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['HTTPS + bytesIO (Numpy)'] = t_elapsed
print(t_elapsed)  # 7.7 - 7.8 s

####------------------------------------------------
#### Kerchunk (Numpy)
t_i = time.time()
fs = fsspec.filesystem("reference",
                       fo=reference_fpath,
                       remote_protocol="s3",
                       remote_options={"anon": True},
                       skip_instance_cache=True)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine='zarr', consolidated=False)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['Kerchunk (Numpy)'] = t_elapsed
print(t_elapsed)  # 12 s

####------------------------------------------------
#### Kerchunk (Dask)
t_i = time.time()
fs = fsspec.filesystem("reference",
                       fo=reference_fpath,
                       remote_protocol="s3",
                       remote_options={"anon": True},
                       skip_instance_cache=True)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine='zarr', consolidated=False, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['Kerchunk (Dask)'] = t_elapsed
print(t_elapsed)  # 36 s

####------------------------------------------------
#### nc mode byte  (dask)
t_i = time.time()
# nc = netCDF4.Dataset(nc_mode_fpath, mode="r")
# ds = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
ds = xr.open_dataset(nc_mode_fpath, chunks=chunks_dict)
ds['Rad'].plot.imshow()
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['netCDF #mode=bytes (Dask)'] = t_elapsed
print(t_elapsed)  # 286 s --> 4.7 minutes

####------------------------------------------------
#### HTTPS + ffspec (Numpy)   
t_i = time.time()
fs = fsspec.filesystem('https')
ds = xr.open_dataset(fs.open(http_fpath))
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['HTTPS + FSSPEC (Numpy)'] = t_elapsed
print(t_elapsed)  # 19-23 s

####------------------------------------------------
#### HTTPS + ffspec (Dask)
t_i = time.time()
fs = fsspec.filesystem('https')
ds = xr.open_dataset(fs.open(http_fpath), chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['HTTPS + FSSPEC (Dask)'] = t_elapsed
print(t_elapsed)  # 19-23 s

####------------------------------------------------
#### S3 + fsspec (Numpy)
t_i = time.time()
fs = fsspec.filesystem('s3', anon=True)
ds = xr.open_dataset(fs.open(s3_fpath), engine='h5netcdf')
apply_custom_fun(ds) 
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['S3 + FSSPEC (Numpy)'] = t_elapsed
print(t_elapsed)  # 21-23 s

####------------------------------------------------
#### S3 + fsspec (Dask)
t_i = time.time()
fs = fsspec.filesystem('s3', anon=True)
ds = xr.open_dataset(fs.open(s3_fpath), engine='h5netcdf', chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict['S3 + FSSPEC (Dask)'] = t_elapsed
print(t_elapsed)  # 21-23 s

####------------------------------------------------
#### Write JSON
with open(result_fpath, 'w') as f:
    json.dump(result_dict, f, indent=4)
