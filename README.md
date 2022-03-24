# Benchmarking reading performance of GOES16 ABI L1B data 

This repository aims at evaluating the performance of various approaches to read GOES16 data into xarray Datasets.
The following reading option are evaluated: 
- Local (Numpy vs. Dask) 
- Download with fs.get and os.remove (Numpy vs. Dask)
- HTTPS using io.bytesIO (Numpy vs. Dask)
- HTTPS using ffspec (Numpy vs. Dask)
- S3 using ffspec (Numpy vs. Dask)
- S3 using ffspec SimpleCache (Numpy vs. Dask)
- S3 using ffspec BlockCache (Numpy vs. Dask)
- S3 using kerchunk-reference file (Numpy vs. Dask)
- S3 download & remove (Numpy vs. Dask)
- netCDF4 mode=byte requests (Dask)

# Dataset characteristics

Some initial considerations on GOES16 datasets chunks:

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

Here we report the elapsed time in seconds with min/mean/max over > 10 tries.

`ReadFullDisc_C01` and `ReadQuarterDisc_C01` uses Dask chunks of (226 * 12, 226 * 12) corresponding to a total 16 and 4 Dask tasks respectively.
`ReadChunk_C01`uses Dask chunks of (226, 226) corresponding to 1 Dask task. 

Sorted by elapsed time (in seconds) when reading Full Disc

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01      |
|-----------------------------------|----------------------|-----------------------|--------------------|
| S3 + FSSPEC + BLOCKCACHE (Numpy)  | 1.29/1.43/1.65       | 0.42/0.44/0.47        | 0.13/0.14/0.14     |
| Local (Numpy)                     | 1.43/1.48/1.54       | 0.26/0.35/0.37        | 0.04/0.04/0.04     |
| Local (Dask)                      | 1.22/1.62/1.8        | 1.33/1.55/1.72        | 1.51/1.56/1.67     |
| S3 + FSSPEC + BLOCKCACHE (Dask)   | 1.3/1.63/1.76        | 1.64/1.69/1.74        | 1.6/1.67/1.83      |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 1.58/1.64/1.8        | 1.63/1.69/1.79        | 1.6/1.67/1.83      |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 1.59/1.66/1.78       | 0.43/0.44/0.47        | 0.14/0.14/0.15     |
| Download & Remove (Dask)          | 3.33/3.45/3.6        | 3.29/3.48/3.69        | 3.33/3.44/3.65     |
| Download & Remove (Numpy)         | 3.88/4.09/4.33       | 2.05/2.21/2.47        | 1.81/1.9/2.06      |
| HTTPS + bytesIO (Numpy)           | 4.3/4.53/4.67        | 3.12/3.2/3.41         | 2.84/2.99/3.26     |
| HTTPS + bytesIO (Dask)            | 4.19/5.88/17.94      | 4.24/4.52/4.7         | 4.3/4.49/4.71      |
| HTTPS + FSSPEC (Dask)             | 13.2/13.73/14.85     | 12.15/14.18/26.61     | 12.85/13.6/16.86   |
| S3 + FSSPEC (Dask)                | 13.45/14.69/21.88    | 12.42/13.06/13.51     | 12.77/13.51/14.38  |
| HTTPS + FSSPEC (Numpy)            | 17.1/17.47/18.4      | 8.51/9.07/10.46       | 6.14/6.33/6.6      |
| S3 + FSSPEC (Numpy)               | 16.64/18.08/23.91    | 8.56/8.96/9.49        | 6.0/6.22/6.49      |
| Kerchunk (Dask)                   | 26.64/27.36/29.14    | 6.82/7.35/8.07        | 0.6/0.62/0.66      |
| Kerchunk (Numpy)                  | 261.33/265.8/269.82  | 63.21/65.42/68.93     | 1.11/1.17/1.2      |
| netCDF #mode=bytes (Dask)         | 270.41/277.14/282.58 | 272.3/279.37/285.73   | 273.9/282.2/294.92 |

Sorted by elapsed time (in seconds) when reading 1/4 of Full Disc

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01      |
|-----------------------------------|----------------------|-----------------------|--------------------|
| Local (Numpy)                     | 1.43/1.48/1.54       | 0.26/0.35/0.37        | 0.04/0.04/0.04     |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 1.59/1.66/1.78       | 0.43/0.44/0.47        | 0.14/0.14/0.15     |
| S3 + FSSPEC + BLOCKCACHE (Numpy)  | 1.29/1.43/1.65       | 0.42/0.44/0.47        | 0.13/0.14/0.14     |
| Local (Dask)                      | 1.22/1.62/1.8        | 1.33/1.55/1.72        | 1.51/1.56/1.67     |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 1.58/1.64/1.8        | 1.63/1.69/1.79        | 1.6/1.67/1.83      |
| S3 + FSSPEC + BLOCKCACHE (Dask)   | 1.3/1.63/1.76        | 1.64/1.69/1.74        | 1.6/1.67/1.83      |
| Download & Remove (Numpy)         | 3.88/4.09/4.33       | 2.05/2.21/2.47        | 1.81/1.9/2.06      |
| HTTPS + bytesIO (Numpy)           | 4.3/4.53/4.67        | 3.12/3.2/3.41         | 2.84/2.99/3.26     |
| Download & Remove (Dask)          | 3.33/3.45/3.6        | 3.29/3.48/3.69        | 3.33/3.44/3.65     |
| HTTPS + bytesIO (Dask)            | 4.19/5.88/17.94      | 4.24/4.52/4.7         | 4.3/4.49/4.71      |
| Kerchunk (Dask)                   | 26.64/27.36/29.14    | 6.82/7.35/8.07        | 0.6/0.62/0.66      |
| S3 + FSSPEC (Numpy)               | 16.64/18.08/23.91    | 8.56/8.96/9.49        | 6.0/6.22/6.49      |
| HTTPS + FSSPEC (Numpy)            | 17.1/17.47/18.4      | 8.51/9.07/10.46       | 6.14/6.33/6.6      |
| S3 + FSSPEC (Dask)                | 13.45/14.69/21.88    | 12.42/13.06/13.51     | 12.77/13.51/14.38  |
| HTTPS + FSSPEC (Dask)             | 13.2/13.73/14.85     | 12.15/14.18/26.61     | 12.85/13.6/16.86   |
| Kerchunk (Numpy)                  | 261.33/265.8/269.82  | 63.21/65.42/68.93     | 1.11/1.17/1.2      |
| netCDF #mode=bytes (Dask)         | 270.41/277.14/282.58 | 272.3/279.37/285.73   | 273.9/282.2/294.92 |

Sorted by elapsed time (in seconds) when reading a single chunk (226,226)

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01      |
|-----------------------------------|----------------------|-----------------------|--------------------|
| Local (Numpy)                     | 1.43/1.48/1.54       | 0.26/0.35/0.37        | 0.04/0.04/0.04     |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 1.59/1.66/1.78       | 0.43/0.44/0.47        | 0.14/0.14/0.15     |
| S3 + FSSPEC + BLOCKCACHE (Numpy)  | 1.29/1.43/1.65       | 0.42/0.44/0.47        | 0.13/0.14/0.14     |
| Kerchunk (Dask)                   | 26.64/27.36/29.14    | 6.82/7.35/8.07        | 0.6/0.62/0.66      |
| Kerchunk (Numpy)                  | 261.33/265.8/269.82  | 63.21/65.42/68.93     | 1.11/1.17/1.2      |
| Local (Dask)                      | 1.22/1.62/1.8        | 1.33/1.55/1.72        | 1.51/1.56/1.67     |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 1.58/1.64/1.8        | 1.63/1.69/1.79        | 1.6/1.67/1.83      |
| S3 + FSSPEC + BLOCKCACHE (Dask)   | 1.3/1.63/1.76        | 1.64/1.69/1.74        | 1.6/1.67/1.83      |
| Download & Remove (Numpy)         | 3.88/4.09/4.33       | 2.05/2.21/2.47        | 1.81/1.9/2.06      |
| HTTPS + bytesIO (Numpy)           | 4.3/4.53/4.67        | 3.12/3.2/3.41         | 2.84/2.99/3.26     |
| Download & Remove (Dask)          | 3.33/3.45/3.6        | 3.29/3.48/3.69        | 3.33/3.44/3.65     |
| HTTPS + bytesIO (Dask)            | 4.19/5.88/17.94      | 4.24/4.52/4.7         | 4.3/4.49/4.71      |
| S3 + FSSPEC (Numpy)               | 16.64/18.08/23.91    | 8.56/8.96/9.49        | 6.0/6.22/6.49      |
| HTTPS + FSSPEC (Numpy)            | 17.1/17.47/18.4      | 8.51/9.07/10.46       | 6.14/6.33/6.6      |
| S3 + FSSPEC (Dask)                | 13.45/14.69/21.88    | 12.42/13.06/13.51     | 12.77/13.51/14.38  |
| HTTPS + FSSPEC (Dask)             | 13.2/13.73/14.85     | 12.15/14.18/26.61     | 12.85/13.6/16.86   |
| netCDF #mode=bytes (Dask)         | 270.41/277.14/282.58 | 272.3/279.37/285.73   | 273.9/282.2/294.92 |

# Notes on NetCDF4/HDF5, Zarr and Kerchunk 
  
### NetCDF4/HDF5 files
- Designed for filesytem use.  
- Suffer of performance issues when accessed from cloud object storage.
- Do not allow concurrent multi-threaded reads.
- Can be directly opened from s3 but performance is poor because:
  1. HDF5/NetCDF library executes many small reads.
  2. s3 storage has significantly higher latency than traditional file systems.

### Zarr
- Was specifically designed to overcome NetCDF4/HDF5 issues.
- Metadata are stored in a single JSON object.
- Each chunk is a separate object.
- Enables unlimited file sizes and parallel writes/reads.
- Avoids HDF5/netCDF4 library issues with python concurrent multi-threaded reads.

### kerchunk
- Formerly known as `fsspec-reference-maker`.
- A kind of virtual file-system for `fsspec`.
- Enable to access the contents of binary files directly without the limitations of the package designed for that file type.
- It derives a single metadata JSON file describing all chunk locations of a NetCDF4/HDF5 file.
- It extracts the internal references of a netCDF4/HDF5 file.
- It enables to perform efficient byte-range requests.
- The derived JSON metadata file can point directly to where the required data are, instead having to access all files to understand which are necessary.

async  
- It provides speed ups if:  
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

 
