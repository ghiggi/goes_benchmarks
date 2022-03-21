# goes_io_benchmark

This repository aims at evaluating the performance of various approaches to read GOES16 data into xarray Datasets.

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

Chunks are compressed with zlib and a deflation level of 1. No shuffle applied to the arrays.
21 % of pixels in Full Disc arrays has `nan` radiances. 


