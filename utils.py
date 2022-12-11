#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:29:53 2022

@author: samuelwong
"""

import pandas as pd
import numpy as np
import os


def set_cwd(working_dir: str = '/Users/samuelwong/Projects/PropertyGuru Analysis/PropertyGuruApp') -> str:

    cwd = os.getcwd()
    
    if os.getcwd() != working_dir:
        os.chdir(working_dir)
        cwd = os.getcwd()
    else:
        cwd = os.getcwd()
        
    return cwd

def save_data(df: pd.DataFrame, filename: str) -> None:
    """Save dataset into csv format

    Parameters
    ---------
    df: pd.DataFrame,
        The dataframe which contains the data to be saved.
    filename: str,
        The name of the csv file to be generated.
    Returns
    -------
    None
    """

    if filename[-4:] != '.csv':
        filename = filename.strp() + '.csv'
    else:
        pass

    try:
        df.to_csv(filename, index=False)
        print(f"File saved successfully as {filename}.")
    except Exception as e:
        print(e)

