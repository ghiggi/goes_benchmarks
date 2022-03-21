#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:12:50 2022

@author: ghiggi
"""
import os
import glob
import json
import numpy as np
import pandas as pd

results_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_io_benchmark/results/"

patterns = ["ReadFullDisc_C01", "ReadQuarterDisc_C01", "ReadChunk_C01"]
global_dict = {}
global_dict_str = {}
for pattern in patterns:
    # Retrieve results for all profiling
    result_fpaths = glob.glob(os.path.join(results_dir, pattern + "_*.json"))
    list_dicts = []
    for fpath in result_fpaths:
        with open(fpath, 'r') as f:
            result_dict = json.load(f)
        list_dicts.append(result_dict)

    # Compute median and standard deviation
    keys = list(list_dicts[0])
    key = keys[0]
    results_summary = {}
    results_summary_str = {}
    for key in keys:
        values = [d[key] for d in list_dicts]
        results_summary[key] = round(np.mean(values), 2)
        results_summary_str[key] = str(round(np.mean(values), 2)) + ' +/- ' + str(2 * round(np.std(values), 2))
    # Attach summary to global dict
    global_dict[pattern] = results_summary
    global_dict_str[pattern] = results_summary_str

####------------------------------------------------
# Show summary statistics
df = pd.DataFrame(global_dict_str)
print(df)
