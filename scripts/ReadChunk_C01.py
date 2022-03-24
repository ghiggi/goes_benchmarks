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
import datetime
import fsspec
import time
import appdirs
import requests
import fsspec.implementations.cached

# import netCDF4
# import h5netcdf
import numpy as np
import xarray as xr
from io import BytesIO

# Define directory where saving results
# base_dir = "/home/ghiggi/Projects/goes_benchmarks/"
# base_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_benchmarks/"
base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
results_dir = os.path.join(base_dir, "results")
data_dir = os.path.join(base_dir, "data")

# Define filepaths
fname = "OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
local_fpath = os.path.join(data_dir, fname)
reference_fpath = os.path.join(data_dir, fname + ".json")
tmp_fpath = os.path.join("/tmp", fname)

http_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"
nc_mode_fpath = "https://noaa-goes16.s3.amazonaws.com/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc#mode=bytes"
s3_fpath = "s3://noaa-goes16/ABI-L1b-RadF/2019/321/11/OR_ABI-L1b-RadF-M6C01_G16_s20193211130282_e20193211139590_c20193211140047.nc"

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
print(t_elapsed)

####------------------------------------------------
#### Local (dask)
t_i = time.time()
ds = xr.open_dataset(local_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Local (Dask)"] = t_elapsed
print(t_elapsed)

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
print(t_elapsed)

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
print(t_elapsed)

####------------------------------------------------
#### Kerchunk (Numpy)
t_i = time.time()
fs = fsspec.filesystem(
    "reference",
    fo=reference_fpath,
    remote_protocol="s3",
    remote_options={"anon": True},
    skip_instance_cache=True,
)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine="zarr", consolidated=False)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Kerchunk (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### Kerchunk (Dask)
t_i = time.time()
fs = fsspec.filesystem(
    "reference",
    fo=reference_fpath,
    remote_protocol="s3",
    remote_options={"anon": True},
    skip_instance_cache=True,
)
m = fs.get_mapper("")
ds = xr.open_dataset(m, engine="zarr", consolidated=False, chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Kerchunk (Dask)"] = t_elapsed
print(t_elapsed)

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
print(t_elapsed)

####------------------------------------------------
#### HTTPS + ffspec (Numpy)
t_i = time.time()
fs = fsspec.filesystem("https")
ds = xr.open_dataset(fs.open(http_fpath))
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["HTTPS + FSSPEC (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### HTTPS + ffspec (Dask)
t_i = time.time()
fs = fsspec.filesystem("https")
ds = xr.open_dataset(fs.open(http_fpath), chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["HTTPS + FSSPEC (Dask)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec (Numpy)
t_i = time.time()
fs = fsspec.filesystem("s3", anon=True)
ds = xr.open_dataset(fs.open(s3_fpath), engine="h5netcdf")
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec (Dask)
t_i = time.time()
fs = fsspec.filesystem("s3", anon=True)
ds = xr.open_dataset(fs.open(s3_fpath), engine="h5netcdf", chunks=chunks_dict)
apply_custom_fun(ds)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC (Dask)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec simplecache (Numpy)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-simple-cache-numpy")
storage_options = {"anon": True}
fs_s3 = fsspec.filesystem(protocol="s3", **storage_options)
fs_simple = fsspec.implementations.cached.SimpleCacheFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    check_files=False,
    expiry_times=60 * 2,  # to avoid cached file on next benchmark run,
    same_names=True,
)
with fs_simple.open(s3_fpath) as f:
    ds = xr.open_dataset(f, engine="h5netcdf")
    apply_custom_fun(ds)

del ds, f  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + SIMPLECACHE (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec simplecache (Dask)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-simple-cache-dask")
storage_options = {"anon": True}
fs_s3 = fsspec.filesystem(protocol="s3", **storage_options)
fs_simple = fsspec.implementations.cached.SimpleCacheFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    check_files=False,
    expiry_times=60 * 2,  # to avoid cached file on next benchmark run,
    same_names=True,
)
with fs_simple.open(s3_fpath) as f:
    ds = xr.open_dataset(f, engine="h5netcdf", chunks=chunks_dict)
    apply_custom_fun(ds)
del ds, f  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + SIMPLECACHE (Dask)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec blockcache (Numpy)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-block-cache-numpy")
storage_options = {"anon": True}
fs_s3 = fsspec.filesystem(protocol="s3", **storage_options)
fs_block = fsspec.implementations.cached.CachingFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    cache_check=600,
    check_files=False,
    expiry_times=60 * 2,  # to avoid cached file on next benchmark run
    same_names=False,
)
with fs_block.open(s3_fpath, block_size=2**20) as f:
    ds = xr.open_dataset(f, engine="h5netcdf")
    apply_custom_fun(ds)
del ds, f  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + BLOCKCACHE (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### S3 + fsspec blockcache (Dask)
t_i = time.time()
cachedir = appdirs.user_cache_dir("ABI-block-cache-dask")
storage_options = {"anon": True}
fs_s3 = fsspec.filesystem(protocol="s3", **storage_options)
fs_block = fsspec.implementations.cached.CachingFileSystem(
    fs=fs_s3,
    cache_storage=cachedir,
    cache_check=600,
    check_files=False,
    expiry_times=60 * 2,  # to avoid cached file on next benchmark run
    same_names=False,
)
with fs_block.open(s3_fpath, block_size=2**20) as f:
    ds = xr.open_dataset(f, engine="h5netcdf", chunks=chunks_dict)
    apply_custom_fun(ds)
del ds, f  # GOOD PRACTICE TO REMOVE, SINCE CONNECTION HAS BEEN CLOSED !
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["S3 + FSSPEC + BLOCKCACHE (Dask)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### Download & Remove (Numpy)
t_i = time.time()
fs = fsspec.filesystem("s3", anon=True)
fs.get(s3_fpath, tmp_fpath)
ds = xr.open_dataset(tmp_fpath)
apply_custom_fun(ds)
os.remove(tmp_fpath)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Download & Remove (Numpy)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### Download & Remove (Dask)
t_i = time.time()
fs = fsspec.filesystem("s3", anon=True)
fs.get(s3_fpath, tmp_fpath)
ds = xr.open_dataset(tmp_fpath, chunks=chunks_dict)
apply_custom_fun(ds)
os.remove(tmp_fpath)
t_f = time.time()

t_elapsed = round(t_f - t_i, 2)
result_dict["Download & Remove (Dask)"] = t_elapsed
print(t_elapsed)

####------------------------------------------------
#### Write JSON
with open(result_fpath, "w") as f:
    json.dump(result_dict, f, indent=4)
