#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:57:24 2022

@author: samuelwong
"""

from pipeline import Pipeline
from database import PropertyGuruDatabase

pipeline = Pipeline()

df = pipeline.run_pipeline()

pipeline.save_data('clean_data.csv')

db = PropertyGuruDatabase()

db.load_data_to_db()