#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 15:12:47 2022

@author: ghiggi
"""
import os
import subprocess
python_benchmark_fnames = ['ReadFullDisc_C01.py',
                           'ReadQuarterDisc_C01.py',
                           'ReadChunk_C01.py',
                          ]

current_dir = os.path.dirname(os.path.realpath(__file__))

# Run S3 benchmarks 
python_benchmark_fpaths = [os.path.join(current_dir, "s3_scripts", fname) for fname in python_benchmark_fnames]
n_repeat = 1 # 10
for python_fpath in python_benchmark_fpaths:
    print("Profiling : ", python_fpath)
    for i in range(0, n_repeat):
        print("Profiling number: ", i)
        cmd = 'python ' + python_fpath
        subprocess.run(cmd, shell=True)
        
# Run GCS benchmarks 
python_benchmark_fpaths = [os.path.join(current_dir, "gcs_scripts", fname) for fname in python_benchmark_fnames]
n_repeat = 1 # 10
for python_fpath in python_benchmark_fpaths:
    print("Profiling : ", python_fpath)
    for i in range(0, n_repeat):
        print("Profiling number: ", i)
        cmd = 'python ' + python_fpath
        subprocess.run(cmd, shell=True)