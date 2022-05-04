# Benchmarking reading performance of GOES16 ABI L1B data 

This repository aims at evaluating the performance of various approaches to read GOES16 data into xarray Datasets.
The following reading option are evaluated: 
- Local (Numpy vs. Dask) 
- Download with ffspec fs.get and os.remove (Numpy vs. Dask)
- HTTPS using io.bytesIO (Numpy vs. Dask)
- HTTPS using ffspec (Numpy vs. Dask)
- S3/GCS using ffspec (Numpy vs. Dask)
- S3/GCS using ffspec SimpleCache (Numpy vs. Dask)
- S3/GCS using ffspec BlockCache (Numpy vs. Dask)
- S3/GCS using kerchunk-reference file (Numpy vs. Dask)
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

# S3 Results 

Here we report the elapsed time in seconds with min/mean/max over > 10 tries.

`ReadFullDisc_C01` and `ReadQuarterDisc_C01` uses Dask chunks of (226 * 12, 226 * 12) corresponding to a total 16 and 4 Dask tasks respectively.
`ReadChunk_C01`uses Dask chunks of (226, 226) corresponding to 1 Dask task. 

Sorted by elapsed time (in seconds) when reading Full Disc

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|-----------------------------------|----------------------|-----------------------|-------------------|
| Local (Numpy)                     | 1.33/1.59/1.74       | 0.36/0.38/0.42        | 0.05/0.05/0.05    |
| Local (Dask)                      | 1.6/1.69/1.77        | 0.35/0.38/0.41        | 0.02/0.02/0.02    |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 3.17/3.54/3.75       | 2.17/2.31/2.41        | 1.85/1.98/2.12    |
| Download & Remove (Numpy)         | 3.14/3.56/4.65       | 2.06/2.2/2.38         | 1.77/1.88/2.06    |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 3.35/3.59/3.99       | 2.17/2.29/2.45        | 1.85/1.96/2.04    |
| Download & Remove (Dask)          | 3.28/3.73/5.29       | 2.1/2.21/2.3          | 1.76/1.89/1.95    |
| HTTPS + bytesIO (Dask)            | 4.38/4.58/4.82       | 3.17/3.32/3.48        | 2.83/2.98/3.13    |
| HTTPS + bytesIO (Numpy)           | 4.43/4.61/4.79       | 3.13/3.32/3.46        | 2.85/3.03/3.57    |
| S3 + FSSPEC (Dask)                | 13.21/14.56/17.08    | 3.71/3.91/4.11        | 1.16/1.22/1.28    |
| HTTPS + FSSPEC (Dask)             | 13.25/16.34/35.72    | 3.65/3.95/5.13        | 1.15/1.21/1.27    |
| S3 + FSSPEC (Numpy)               | 17.18/18.29/21.61    | 8.36/8.98/9.73        | 5.81/6.14/6.39    |
| HTTPS + FSSPEC (Numpy)            | 16.75/19.54/35.32    | 8.3/8.78/9.49         | 5.71/6.02/6.33    |
| Kerchunk (Dask)                   | 27.17/28.07/32.43    | 7.24/7.63/8.37        | 0.57/0.59/0.66    |
| Kerchunk (Numpy)                  | 28.91/29.83/30.89    | 7.96/8.17/8.38        | 1.18/1.21/1.3     |
| netCDF #mode=bytes (Dask)         | 272.03/276.12/285.54 | 79.44/81.5/83.46      | 17.31/17.93/18.83 |

Sorted by elapsed time (in seconds) when reading 1/4 of Full Disc

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|-----------------------------------|----------------------|-----------------------|-------------------|
| Local (Numpy)                     | 1.33/1.59/1.74       | 0.36/0.38/0.42        | 0.05/0.05/0.05    |
| Local (Dask)                      | 1.6/1.69/1.77        | 0.35/0.38/0.41        | 0.02/0.02/0.02    |
| Download & Remove (Numpy)         | 3.14/3.56/4.65       | 2.06/2.2/2.38         | 1.77/1.88/2.06    |
| Download & Remove (Dask)          | 3.28/3.73/5.29       | 2.1/2.21/2.3          | 1.76/1.89/1.95    |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 3.35/3.59/3.99       | 2.17/2.29/2.45        | 1.85/1.96/2.04    |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 3.17/3.54/3.75       | 2.17/2.31/2.41        | 1.85/1.98/2.12    |
| HTTPS + bytesIO (Numpy)           | 4.43/4.61/4.79       | 3.13/3.32/3.46        | 2.85/3.03/3.57    |
| HTTPS + bytesIO (Dask)            | 4.38/4.58/4.82       | 3.17/3.32/3.48        | 2.83/2.98/3.13    |
| S3 + FSSPEC (Dask)                | 13.21/14.56/17.08    | 3.71/3.91/4.11        | 1.16/1.22/1.28    |
| HTTPS + FSSPEC (Dask)             | 13.25/16.34/35.72    | 3.65/3.95/5.13        | 1.15/1.21/1.27    |
| Kerchunk (Dask)                   | 27.17/28.07/32.43    | 7.24/7.63/8.37        | 0.57/0.59/0.66    |
| Kerchunk (Numpy)                  | 28.91/29.83/30.89    | 7.96/8.17/8.38        | 1.18/1.21/1.3     |
| HTTPS + FSSPEC (Numpy)            | 16.75/19.54/35.32    | 8.3/8.78/9.49         | 5.71/6.02/6.33    |
| S3 + FSSPEC (Numpy)               | 17.18/18.29/21.61    | 8.36/8.98/9.73        | 5.81/6.14/6.39    |
| netCDF #mode=bytes (Dask)         | 272.03/276.12/285.54 | 79.44/81.5/83.46      | 17.31/17.93/18.83 |

Sorted by elapsed time (in seconds) when reading a single chunk (226,226)

|                                   | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|-----------------------------------|----------------------|-----------------------|-------------------|
| Local (Dask)                      | 1.6/1.69/1.77        | 0.35/0.38/0.41        | 0.02/0.02/0.02    |
| Local (Numpy)                     | 1.33/1.59/1.74       | 0.36/0.38/0.42        | 0.05/0.05/0.05    |
| Kerchunk (Dask)                   | 27.17/28.07/32.43    | 7.24/7.63/8.37        | 0.57/0.59/0.66    |
| Kerchunk (Numpy)                  | 28.91/29.83/30.89    | 7.96/8.17/8.38        | 1.18/1.21/1.3     |
| HTTPS + FSSPEC (Dask)             | 13.25/16.34/35.72    | 3.65/3.95/5.13        | 1.15/1.21/1.27    |
| S3 + FSSPEC (Dask)                | 13.21/14.56/17.08    | 3.71/3.91/4.11        | 1.16/1.22/1.28    |
| Download & Remove (Numpy)         | 3.14/3.56/4.65       | 2.06/2.2/2.38         | 1.77/1.88/2.06    |
| Download & Remove (Dask)          | 3.28/3.73/5.29       | 2.1/2.21/2.3          | 1.76/1.89/1.95    |
| S3 + FSSPEC + SIMPLECACHE (Numpy) | 3.35/3.59/3.99       | 2.17/2.29/2.45        | 1.85/1.96/2.04    |
| S3 + FSSPEC + SIMPLECACHE (Dask)  | 3.17/3.54/3.75       | 2.17/2.31/2.41        | 1.85/1.98/2.12    |
| HTTPS + bytesIO (Dask)            | 4.38/4.58/4.82       | 3.17/3.32/3.48        | 2.83/2.98/3.13    |
| HTTPS + bytesIO (Numpy)           | 4.43/4.61/4.79       | 3.13/3.32/3.46        | 2.85/3.03/3.57    |
| HTTPS + FSSPEC (Numpy)            | 16.75/19.54/35.32    | 8.3/8.78/9.49         | 5.71/6.02/6.33    |
| S3 + FSSPEC (Numpy)               | 17.18/18.29/21.61    | 8.36/8.98/9.73        | 5.81/6.14/6.39    |
| netCDF #mode=bytes (Dask)         | 272.03/276.12/285.54 | 79.44/81.5/83.46      | 17.31/17.93/18.83 |


# GCS Results 

Here we report the elapsed time in seconds with min/mean/max over > 10 tries.

`ReadFullDisc_C01` and `ReadQuarterDisc_C01` uses Dask chunks of (226 * 12, 226 * 12) corresponding to a total 16 and 4 Dask tasks respectively.
`ReadChunk_C01`uses Dask chunks of (226, 226) corresponding to 1 Dask task. 

Sorted by elapsed time (in seconds) when reading Full Disc

|                                    | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|------------------------------------|----------------------|-----------------------|-------------------|
| Local (Numpy)                      | 1.32/1.38/1.54       | 0.36/0.37/0.38        | 0.05/0.05/0.05    |
| Local (Dask)                       | 1.52/1.64/1.76       | 0.36/0.38/0.4         | 0.02/0.02/0.02    |
| Download & Remove (Numpy)          | 2.12/2.22/2.32       | 0.94/0.95/0.96        | 0.64/0.64/0.65    |
| Download & Remove (Dask)           | 2.17/2.25/2.41       | 0.96/1.0/1.02         | 0.64/0.65/0.65    |
| GCS + FSSPEC + SIMPLECACHE (Numpy) | 2.23/2.32/2.41       | 1.03/1.05/1.08        | 0.73/0.75/0.86    |
| GCS + FSSPEC + SIMPLECACHE (Dask)  | 2.24/2.32/2.49       | 1.05/1.08/1.12        | 0.74/0.75/0.75    |
| HTTPS + bytesIO (Numpy)            | 2.3/2.45/3.03        | 1.01/1.1/1.13         | 0.79/0.81/0.83    |
| HTTPS + bytesIO (Dask)             | 2.29/2.45/2.75       | 1.13/1.15/1.17        | 0.81/0.81/0.82    |
| Kerchunk (Numpy)                   | 5.62/6.2/8.81        | 2.03/2.36/3.38        | 0.75/0.76/0.77    |
| GCS + FSSPEC (Dask)                | 7.92/8.1/8.36        | 2.5/2.52/2.57         | 1.04/1.06/1.11    |
| HTTPS + FSSPEC (Dask)              | 9.88/10.04/10.42     | 3.02/3.07/3.25        | 1.05/1.06/1.07    |
| GCS + FSSPEC (Numpy)               | 12.38/12.81/14.43    | 6.54/6.62/6.75        | 4.58/4.66/4.74    |
| HTTPS + FSSPEC (Numpy)             | 13.25/13.34/13.6     | 6.59/6.66/6.78        | 4.61/4.65/4.69    |
| Kerchunk (Dask)                    | 19.96/20.22/20.94    | 5.7/5.74/5.77         | 0.56/0.59/0.6     |
| netCDF #mode=bytes (Dask)          | 282.82/286.59/293.31 | 84.03/84.82/89.28     | 17.85/18.03/18.34 |

Sorted by elapsed time (in seconds) when reading 1/4 of Full Disc

|                                    | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|------------------------------------|----------------------|-----------------------|-------------------|
| Local (Numpy)                      | 1.32/1.38/1.54       | 0.36/0.37/0.38        | 0.05/0.05/0.05    |
| Local (Dask)                       | 1.52/1.64/1.76       | 0.36/0.38/0.4         | 0.02/0.02/0.02    |
| Download & Remove (Numpy)          | 2.12/2.22/2.32       | 0.94/0.95/0.96        | 0.64/0.64/0.65    |
| Download & Remove (Dask)           | 2.17/2.25/2.41       | 0.96/1.0/1.02         | 0.64/0.65/0.65    |
| GCS + FSSPEC + SIMPLECACHE (Numpy) | 2.23/2.32/2.41       | 1.03/1.05/1.08        | 0.73/0.75/0.86    |
| GCS + FSSPEC + SIMPLECACHE (Dask)  | 2.24/2.32/2.49       | 1.05/1.08/1.12        | 0.74/0.75/0.75    |
| HTTPS + bytesIO (Numpy)            | 2.3/2.45/3.03        | 1.01/1.1/1.13         | 0.79/0.81/0.83    |
| HTTPS + bytesIO (Dask)             | 2.29/2.45/2.75       | 1.13/1.15/1.17        | 0.81/0.81/0.82    |
| Kerchunk (Numpy)                   | 5.62/6.2/8.81        | 2.03/2.36/3.38        | 0.75/0.76/0.77    |
| GCS + FSSPEC (Dask)                | 7.92/8.1/8.36        | 2.5/2.52/2.57         | 1.04/1.06/1.11    |
| HTTPS + FSSPEC (Dask)              | 9.88/10.04/10.42     | 3.02/3.07/3.25        | 1.05/1.06/1.07    |
| Kerchunk (Dask)                    | 19.96/20.22/20.94    | 5.7/5.74/5.77         | 0.56/0.59/0.6     |
| GCS + FSSPEC (Numpy)               | 12.38/12.81/14.43    | 6.54/6.62/6.75        | 4.58/4.66/4.74    |
| HTTPS + FSSPEC (Numpy)             | 13.25/13.34/13.6     | 6.59/6.66/6.78        | 4.61/4.65/4.69    |
| netCDF #mode=bytes (Dask)          | 282.82/286.59/293.31 | 84.03/84.82/89.28     | 17.85/18.03/18.34 |

Sorted by elapsed time (in seconds) when reading a single chunk (226,226)

|                                    | ReadFullDisc_C01     | ReadQuarterDisc_C01   | ReadChunk_C01     |
|------------------------------------|----------------------|-----------------------|-------------------|
| Local (Dask)                       | 1.52/1.64/1.76       | 0.36/0.38/0.4         | 0.02/0.02/0.02    |
| Local (Numpy)                      | 1.32/1.38/1.54       | 0.36/0.37/0.38        | 0.05/0.05/0.05    |
| Kerchunk (Dask)                    | 19.96/20.22/20.94    | 5.7/5.74/5.77         | 0.56/0.59/0.6     |
| Download & Remove (Numpy)          | 2.12/2.22/2.32       | 0.94/0.95/0.96        | 0.64/0.64/0.65    |
| Download & Remove (Dask)           | 2.17/2.25/2.41       | 0.96/1.0/1.02         | 0.64/0.65/0.65    |
| GCS + FSSPEC + SIMPLECACHE (Numpy) | 2.23/2.32/2.41       | 1.03/1.05/1.08        | 0.73/0.75/0.86    |
| GCS + FSSPEC + SIMPLECACHE (Dask)  | 2.24/2.32/2.49       | 1.05/1.08/1.12        | 0.74/0.75/0.75    |
| Kerchunk (Numpy)                   | 5.62/6.2/8.81        | 2.03/2.36/3.38        | 0.75/0.76/0.77    |
| HTTPS + bytesIO (Numpy)            | 2.3/2.45/3.03        | 1.01/1.1/1.13         | 0.79/0.81/0.83    |
| HTTPS + bytesIO (Dask)             | 2.29/2.45/2.75       | 1.13/1.15/1.17        | 0.81/0.81/0.82    |
| HTTPS + FSSPEC (Dask)              | 9.88/10.04/10.42     | 3.02/3.07/3.25        | 1.05/1.06/1.07    |
| GCS + FSSPEC (Dask)                | 7.92/8.1/8.36        | 2.5/2.52/2.57         | 1.04/1.06/1.11    |
| HTTPS + FSSPEC (Numpy)             | 13.25/13.34/13.6     | 6.59/6.66/6.78        | 4.61/4.65/4.69    |
| GCS + FSSPEC (Numpy)               | 12.38/12.81/14.43    | 6.54/6.62/6.75        | 4.58/4.66/4.74    |
| netCDF #mode=bytes (Dask)          | 282.82/286.59/293.31 | 84.03/84.82/89.28     | 17.85/18.03/18.34 |

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

# References
The documentation listed here below has been used to design this benchmark and create the notes above.
- https://github.com/pytroll/satpy/pull/1321
- https://github.com/fsspec/kerchunk 
- https://medium.com/pangeo/fake-it-until-you-make-it-reading-goes-netcdf4-data-on-aws-s3-as-zarr-for-rapid-data-access-61e33f8fe685
- https://github.com/lsterzinger/fsspec-reference-maker-tutorial
- https://github.com/lsterzinger/cloud-optimized-satellite-data-tests
- https://github.com/lsterzinger/2022-esip-kerchunk-tutorial
- https://nbviewer.org/github/cgentemann/cloud_science/blob/master/zarr_meta/cloud_mur_v41_benchmark.ipynb
- https://medium.com/pangeo/cloud-performant-reading-of-netcdf4-hdf5-data-using-the-zarr-library-1a95c5c92314
- https://medium.com/pangeo/cloud-performant-netcdf4-hdf5-with-zarr-fsspec-and-intake-3d3a3e7cb935

 
