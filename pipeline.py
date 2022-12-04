#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 21:23:28 2022

@author: samuelwong
"""

import pandas as pd
from preprocessing import cleaning_data, save_data, drop_missing_val, drop_duplicated_listings
from utils import set_cwd

class Pipeline():
    
    FILES = ['selangor_1-50_20221130.csv', 'selangor_51-100_20221130.csv', 'Full_dataset_asof_20221130.csv']
    
    def __init__(self):
        pass
    
    def __join_data(self, files: list = FILES) ->  pd.DataFrame:
        
        df = pd.DataFrame()
        
        for file in files:
            df1 = pd.read_csv(file)
            
            if 'Unnamed: 0' in df1.columns:
                df1.drop(columns = 'Unnamed: 0', inplace = True)
                
            df = pd.concat([df,df1], ignore_index=True)
        
        return df
    
    def run_pipeline(self) -> pd.DataFrame:
        
        self.cwd = set_cwd()
        
        print(self.cwd)
        
        self.df = self.__join_data()
        
        # drop duplicated listings
        self.df = drop_duplicated_listings(self.df)
    
        # data preprocessing
        self.df = cleaning_data(self.df)
    
        # Drop features with too many missing values
        self.df = drop_missing_val(self.df)
    
        return self.df
    
    def save_data(self, filename: str) -> None:
        
        save_data(self.df, filename)
        




