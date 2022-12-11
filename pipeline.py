#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 21:23:28 2022

@author: samuelwong
"""

import pandas as pd
from preprocessing import preprocess_data, drop_duplicated_listings, drop_50p_cols, assign_primary_key
from utils import set_cwd, save_data


class RawDataPipeline:
    #
    FILES = ['selangor_1-50_20221130.csv', 'selangor_51-100_20221130.csv', 'Full_dataset_asof_20221130.csv']

    def __init__(self):
        pass

    def __join_data(self, files: list = FILES) -> pd.DataFrame:

        df = pd.DataFrame()

        for file in files:
            df1 = pd.read_csv(file)

            if 'Unnamed: 0' in df1.columns:
                df1.drop(columns='Unnamed: 0', inplace=True)

            df = pd.concat([df, df1], ignore_index=True)

        return df

    def run(self) -> pd.DataFrame:

        self.cwd = set_cwd()

        print(self.cwd)

        self.df = self.__join_data()

        # drop duplicated listings
        self.df = drop_duplicated_listings(self.df)

        # drop columns with missing values more than 50%
        self.df = drop_50p_cols(self.df)

        self.df  = assign_primary_key(self.df)

        return self.df

    def save_data(self, filename: str) -> None:

        save_data(self.df, filename)


class PreprocessedDataPipeline:

    def __init__(self):
        pass

    def __get_data(self) -> pd.DataFrame:

        raw_data_pipeline = RawDataPipeline()

        self.df = raw_data_pipeline.run()

        return self.df

    def run(self) -> pd.DataFrame:

        self.cwd = set_cwd()

        print(self.cwd)

        self.df = self.__get_data()

        # some simple cleaning before EDA
        self.df = preprocess_data(self.df)

        return self.df

    def save_data(self, filename: str) -> None:

        save_data(self.df, filename)

class CleanedDataPipeline:

    def __init__(self):
        pass

    def __get_data(self) -> pd.DataFrame:

        preprocessed_data_pipeline = PreprocessedDataPipeline()

        self.df = preprocessed_data_pipeline.run()

        return self.df

    def run(self) -> pd.DataFrame:

        self.cwd = set_cwd()

        print(self.cwd)

        self.df = self.__get_data()

        # some simple cleaning before EDA
        self.df = clean_data(self.df)

        return self.df

    def save_data(self, filename: str) -> None:

        save_data(self.df, filename)