#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:29:53 2022

@author: samuelwong
"""

import pandas as pd
import numpy as np
import os


def set_cwd(working_dir: str = '/Users/samuelwong/Projects/PropertyGuru Analysis/Web Scraping/Working') -> str:

    cwd = os.getcwd()
    
    if os.getcwd() != working_dir:
        os.chdir(working_dir)
        cwd = os.getcwd()
    else:
        cwd = os.getcwd()
        
    return cwd