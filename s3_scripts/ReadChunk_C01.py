#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 18:00:41 2022

@author: ghiggi
"""
###################
### Benchmarks ####
###################
import os
import json
import shutil
import datetime
import fsspec
import time
import appdirs
import requests
# import netCDF4
# import h5netcdf
import numpy as np
import xarray as xr
from io import BytesIO
from fsspec.implementations.cached import CachingFileSystem, SimpleCacheFileSystem

# Define directory where saving results
# base_dir = "/home/ghiggi/Projects/goes_benchmarks/"
# base_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_benchmarks/"
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
reference_dir = os.path.join(base_dir, "s3_reference")
results_dir = os.path.join(base_dir, "s3_results")
data_dir = os.path.join(base_dir, "data")

# Define filepaths
fname = "OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
local_fpath = os.path.join(data_dir, fname)
reference_fpath = os.path.join(reference_dir, fname + ".json")
tmp_fpath = os.path.join("/tmp", fname)

http_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
nc_mode_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc#mode=bytes"
s3_fpath = "s3://noaa-goes16/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"

protocol = "s3"
storage_options = {"anon": True}
cache_expiry_times = 60 
block_size = 2**20

# Define experiment name
exp_name = "ReadChunk_C01"

# -----------------------------------
# Define dask chunking
chunks_dict = {"Rad": (226, 226)}

# Define custom operation
def apply_custom_fun(ds):
    dummy = np.asarray(ds["Rad"].isel(y=slice(0, 226), x=slice(0, 226)).data)
    return None

# Define filename where saving results
current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
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
result_dict["Local (Numpy)"] = t_elapsed
print(" - Local (Numpy)" + f": {t_elapsed} s") 

####------------------------------------------------
#### Local (dask)
t_i = time.time()
ds = xr.open_dataset(local_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Local (Dask)"] = t_elapsed
print(" - Local (Dask)" + f": {t_elapsed} s") 

####------------------------------------------------
#### HTTPS + bytesIO (numpy)
t_i = time.time()
resp = requests.get(http_fpath)
f_obj = BytesIO(resp.content)
ds = xr.open_dataset(f_obj)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["HTTPS + bytesIO (Numpy)"] = t_elapsed
print(" - HTTPS + bytesIO (Numpy)" + f": {t_elapsed} s") 

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
result_dict["HTTPS + bytesIO (Dask)"] = t_elapsed
print(" - HTTPS + bytesIO (Dask)" + f": {t_elapsed} s") 

####------------------------------------------------
#### Kerchunk (Numpy)
t_i = time.time()
fs = fsspec.filesystem(
    "reference",
    fo=reference_fpath,
    remote_protocol=protocol,
    remote_options=storage_options,
    skip_instance_cache=True,
)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine="zarr", consolidated=False)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Kerchunk (Numpy)"] = t_elapsed
print(" - Kerchunk (Numpy)" + f": {t_elapsed} s") 

####------------------------------------------------
#### Kerchunk (Dask)
t_i = time.time()
fs = fsspec.filesystem(
    "reference",
    fo=reference_fpath,
    remote_protocol=protocol,
    remote_options=storage_options,
    skip_instance_cache=True,
)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine="zarr", consolidated=False, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Kerchunk (Dask)"] = t_elapsed
print(" - Kerchunk (Dask)" + f": {t_elapsed} s") 

####------------------------------------------------
#### nc mode byte  (dask)
t_i = time.time()
# nc = netCDF4.Dataset(nc_mode_fpath, mode="r")
# ds = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
ds = xr.open_dataset(nc_mode_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["netCDF #mode=bytes (Dask)"] = t_elapsed
print(" - netCDF #mode=bytes (Dask)" + f": {t_elapsed} s") 

####------------------------------------------------
#### HTTPS + fsspec (Numpy)
t_i = time.time()
fs = fsspec.filesystem("https")
ds = xr.open_dataset(fs.open(http_fpath))
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["HTTPS + FSSPEC (Numpy)"] = t_elapsed
print(" - HTTPS + FSSPEC (Numpy)" + f": {t_elapsed} s") 

####------------------------------------------------
#### HTTPS + fsspec (Dask)
t_i = time.time()
fs = fsspec.filesystem("https")
ds = xr.open_dataset(fs.open(http_fpath), chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["HTTPS + FSSPEC (Dask)"] = t_elapsed
print(" - HTTPS + FSSPEC (Dask)" + f": {t_elapsed} s")  

####------------------------------------------------
#### S3 + fsspec (Numpy)
t_i = time.time()
fs = fsspec.filesystem(protocol, **storage_options)
ds = xr.open_dataset(fs.open(s3_fpath), engine="h5netcdf")
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC (Numpy)"] = t_elapsed
print(" - S3 + FSSPEC (Numpy)" + f": {t_elapsed} s")

####------------------------------------------------
#### S3 + fsspec (Dask)
t_i = time.time()
fs = fsspec.filesystem(protocol, **storage_options)
ds = xr.open_dataset(fs.open(s3_fpath), engine="h5netcdf", chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC (Dask)"] = t_elapsed
print(" - S3 + FSSPEC (Dask)" + f": {t_elapsed} s")

####------------------------------------------------
#### S3 + fsspec simplecache (Numpy)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-simple-cache-numpy")
fs_s3 = fsspec.filesystem(protocol=protocol, **storage_options)
fs_simple = SimpleCacheFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    expiry_time=cache_expiry_times,
    same_names=True,
)
with fs_simple.open(s3_fpath) as f:
    ds = xr.open_dataset(f, engine="h5netcdf")
    apply_custom_fun(ds)

del ds, f, fs_simple, fs_s3  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + SIMPLECACHE (Numpy)"] = t_elapsed
print(" - S3 + FSSPEC + SIMPLECACHE (Numpy)" + f": {t_elapsed} s")

shutil.rmtree(cachedir)
time.sleep(2) # to avoid problems ... 

####------------------------------------------------
#### S3 + fsspec simplecache (Dask)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-simple-cache-dask")
fs_s3 = fsspec.filesystem(protocol=protocol, **storage_options)
fs_simple = SimpleCacheFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    expiry_time=cache_expiry_times,
    same_names=True,
)
with fs_simple.open(s3_fpath) as f:
    ds = xr.open_dataset(f, engine="h5netcdf", chunks=chunks_dict)
    apply_custom_fun(ds)
del ds, f, fs_simple, fs_s3  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + SIMPLECACHE (Dask)"] = t_elapsed
print(" - S3 + FSSPEC + SIMPLECACHE (Dask)" + f": {t_elapsed} s")

shutil.rmtree(cachedir)
time.sleep(2) # to avoid problems ... 

####------------------------------------------------
#### S3 + fsspec blockcache (Numpy)
# t_i = time.time()
# cachedir = appdirs.user_cache_dir("ABI-block-cache-numpy")
# fs_s3 = fsspec.filesystem(protocol=protocol, **storage_options)
# fs_block = CachingFileSystem(
#     fs=fs_s3,
#     cache_storage=cachedir,
#     expiry_time=cache_expiry_times,
# )
# with fs_block.open(s3_fpath, block_size=block_size) as f:
#     ds = xr.open_dataset(f, engine="h5netcdf")
#     apply_custom_fun(ds)
# del ds, f, fs_block, fs_s3   # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !    
# t_f = time.time()

# t_elapsed = round(t_f - t_i, 2)
# result_dict["S3 + FSSPEC + BLOCKCACHE (Numpy)"] = t_elapsed
# print(" - S3 + FSSPEC + BLOCKCACHE (Numpy)" + f": {t_elapsed} s")

# shutil.rmtree(cachedir)
# time.sleep(2) # to avoid problems ... 

# ####------------------------------------------------
# #### S3 + fsspec blockcache (Dask)
# t_i = time.time()
# cachedir = appdirs.user_cache_dir("ABI-block-cache-dask")
# fs_s3 = fsspec.filesystem(protocol=protocol, **storage_options)
# fs_block = CachingFileSystem(
#     fs=fs_s3,
#     cache_storage=cachedir,
#     expiry_time=cache_expiry_times,
# )
# with fs_block.open(s3_fpath, block_size=block_size) as f:
#     ds = xr.open_dataset(f, engine="h5netcdf", chunks=chunks_dict)
#     apply_custom_fun(ds)
# del ds, f, fs_block, fs_s3  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
# t_f = time.time()

# t_elapsed = round(t_f - t_i, 2)
# result_dict["S3 + FSSPEC + BLOCKCACHE (Dask)"] = t_elapsed
# print(" - S3 + FSSPEC + BLOCKCACHE (Dask)" + f": {t_elapsed} s")

# shutil.rmtree(cachedir)
# time.sleep(2) # to avoid problems ... 

####------------------------------------------------
#### Download & Remove (Numpy)
t_i = time.time()
fs = fsspec.filesystem(protocol, **storage_options)
fs.get(s3_fpath, tmp_fpath)
ds = xr.open_dataset(tmp_fpath)
apply_custom_fun(ds)
os.remove(tmp_fpath)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Download & Remove (Numpy)"] = t_elapsed
print(" - Download & Remove (Numpy)" + f": {t_elapsed} s")

####------------------------------------------------
#### Download & Remove (Dask)
t_i = time.time()
fs = fsspec.filesystem(protocol, **storage_options)
fs.get(s3_fpath, tmp_fpath)
ds = xr.open_dataset(tmp_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
os.remove(tmp_fpath)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Download & Remove (Dask)"] = t_elapsed
print(" - Download & Remove (Dask)" + f": {t_elapsed} s")

####------------------------------------------------
#### Write JSON
with open(result_fpath, "w") as f:
    json.dump(result_dict, f, indent=4)
