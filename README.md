# Benchmarking reading performance of GOES16 ABI L1B data 

This repository aims at evaluating the performance of various approaches to read GOES16 data into xarray Datasets.
The following reading option are evaluated: 
- Local (Numpy vs. Dask) 
- HTTPS + bytesIO (Numpy vs. Dask)
- kerchunk-reference file (Numpy vs. Dask)
- netCDF4 mode=byte requests (Dask)
- HTTPS via ffspec (Numpy vs. Dask)
- S3 via ffspec (Numpy vs. Dask)
- S3 Download & Remove (Numpy vs. Dask)

# Dataset characteristics

Some initial considerations on datasets chunks

| Sector    | CHUNK SHAPE | CHUNK MEMORY (float32) | CHUNK DISK (int16)    |
|-----------|-------------|------------------------|-----------------------|
| Full Disc | (226,226)   | 0.19 MB                | 99 KB (uncompressed)  |
| CONUS     | (250,250)   | 0.23 MB                | 122 KB (uncompressed) |
| Mesoscale | (250,250)   | 0.23 MB                | 122 KB (uncompressed) |

GOES16 Full Disc array: 

| Resolution  | ARRAY SHAPE    | ARRAY MEMORY (float32) | # CHUNKS |
|-------------|----------------|------------------------|----------|
| 500 m (C02) | (21696, 21696) | 1.75 GB                | 9216     |
| 1 km        | (10848,10848)  | 449 MB                 | 2304     |
| 2 km        | (5424, 5424)   | 112 MB                 | 576      |


GOES16 CONUS array:

| Resolution  | ARRAY SHAPE   | ARRAY MEMORY (float32) | # CHUNKS |
|-------------|---------------|------------------------|----------|
| 500 m (C02) | (6000, 10000) | 228 MB                 | 960      |
| 1 km        | (3000, 5000)  | 57 MB                  | 240      |
| 2 km        | (1500, 2500)  | 14 MB                  | 60       |

Chunks are compressed with zlib and a deflation level of 1. No bytes shuffle is applied to the arrays.
Full Disc arrays have 21 % of pixels of unvalid (nan) pixels. 

# Results 

# Notes on NetCDF4/HDF5, Zarr and Kerchunk 
  
### NetCDF4/HDF5 files
- Designed for filesytem use.  
- Suffer of performance issues when accessed from cloud object storage.
- Do not allow concurrent multi-threaded reads.
- Can be directly opened from s3 but performance is poor because:
  1. HDF5/NetCDF library executes many small reads.
  2. s3 storage has significantly higher latency than traditional file systems.

### Zarr
- was specifically designed to overcome NetCDF4/HDF5 issues.
- Metadata are stored in a single JSON object.
- Each chunk is a separate object.
- Enable unlimited file sizes and parallel writes/reads.
- Avoid HDF5/netCDF4 library issues with python concurrent multi-threaded reads.

### kerchunk
- Formerly known as `fsspec-reference-maker`.
- A kind of virtual file-system for `fsspec`.
- Enable to access the contents of binary files directly without the limitations of the package designed for that file type.
- It derive a single metadata JSON file describing all chunk locations of a NetCDF4/HDF5 file.
- It extract the internal references of a netCDF4/HDF5 file.
- It enable to perform efficient byte-range requests.
- The derived JSON metadata file can point directly to where the required data are, instead having to access all files to understand which are necessary.

async  
- It provide speed ups if:  
    1. Multiple chunks are being read at once 
       ---> The dask partition (chunk size) is larger than the file chunksize by some factor 
    2. The latency/overhead of each request is a significant fraction of the overall time.
- Lessens the overhead for smaller file chunks (so long as they are loaded concurrently, meaning a dask partition (chunk) containing many file chunks).
- Once the bandwidth limits are reached, as opposed to waiting, then async doesn’t help.
- When using kerchunk reference files, s3fs and gcsfs internally load the small chunks asynchronously inside each task.
- Should typically help when we encounter a dataset in object storage with lots of little disk chunks.
- Should typically help not so much when we read datasets with 100 MB disk chunks.

- One consequence of the async capability is that there is less of a performance penalty for using smaller Zarr chunks. You still want to use Dask chunks   of ~100MB for large compute jobs. But the underlying file chunks on disk can be smaller.

 
# TODO
- Identify best dask chunk granularity for retrievals 
- Assess request latency 

# References
The documentation listed here below has been used to design this benchmark and create the notes above.
- https://github.com/fsspec/kerchunk 
- https://medium.com/pangeo/fake-it-until-you-make-it-reading-goes-netcdf4-data-on-aws-s3-as-zarr-for-rapid-data-access-61e33f8fe685
- https://github.com/lsterzinger/fsspec-reference-maker-tutorial
- https://github.com/lsterzinger/cloud-optimized-satellite-data-tests
- https://github.com/lsterzinger/2022-esip-kerchunk-tutorial
- https://nbviewer.org/github/cgentemann/cloud_science/blob/master/zarr_meta/cloud_mur_v41_benchmark.ipynb
- https://medium.com/pangeo/cloud-performant-reading-of-netcdf4-hdf5-data-using-the-zarr-library-1a95c5c92314
- https://medium.com/pangeo/cloud-performant-netcdf4-hdf5-with-zarr-fsspec-and-intake-3d3a3e7cb935

 
