#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 17:12:50 2022

@author: ghiggi
"""
import os
import glob
import json
import tabulate
import numpy as np
import pandas as pd

results_dir = "/home/ghiggi/Projects/goes_benchmarks/results/"
# results_dir = "/home/ghiggi/Projects/0_Miscellaneous/goes_benchmarks/results/"

patterns = ["ReadFullDisc_C01", 
            "ReadQuarterDisc_C01",
            "ReadChunk_C01", 
]
global_dict = {}
global_dict_str = {}
global_dict_minmax_str = {}
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
    results_summary_min_max_str = {}
    for key in keys:
        values = [d.get(key, np.nan) for d in list_dicts]
        tmp_min = round(np.nanmin(values), 2)
        tmp_max = round(np.nanmax(values), 2)
        tmp_mean = round(np.nanmean(values), 2)
        tmp_std = round(np.nanstd(values), 2)
        results_summary[key] = tmp_mean
        results_summary_str[key] = str(tmp_mean) + ' +/- ' + str(2 * tmp_std)
        results_summary_min_max_str[key] = str(tmp_min) + "/" + str(tmp_mean) + "/" + str(tmp_max)
    # Attach summary to global dict
    global_dict[pattern] = results_summary
    global_dict_str[pattern] = results_summary_str
    global_dict_minmax_str[pattern] = results_summary_min_max_str
    
####------------------------------------------------
# Show summary statistics
df = pd.DataFrame(global_dict_str)
df = pd.DataFrame(global_dict_minmax_str)
print(df)

## ReadFullDisc_C01 
pattern = "ReadFullDisc_C01"
ordered_dict = {k: v for k, v in sorted(global_dict[pattern] .items(), key=lambda item: item[1])}
ordered_keys = list(ordered_dict.keys())
df.loc[ordered_keys]
print(tabulate.tabulate(df.loc[ordered_keys], headers="keys", tablefmt='github'))

## ReadChunk_C01 
pattern = "ReadChunk_C01"
ordered_dict = {k: v for k, v in sorted(global_dict[pattern] .items(), key=lambda item: item[1])}
ordered_keys = list(ordered_dict.keys())
df.loc[ordered_keys]
print(tabulate.tabulate(df.loc[ordered_keys], headers="keys", tablefmt='github'))

## ReadQuarterDisc_C01 
pattern = "ReadQuarterDisc_C01"
ordered_dict = {k: v for k, v in sorted(global_dict[pattern] .items(), key=lambda item: item[1])}
ordered_keys = list(ordered_dict.keys())
df.loc[ordered_keys]
print(tabulate.tabulate(df.loc[ordered_keys], headers="keys", tablefmt='github'))


