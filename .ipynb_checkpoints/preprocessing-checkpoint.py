#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 21:27:32 2022

@author: samuelwong
"""
import glob
import os
import pandas as pd
import numpy as np


def drop_50p_cols(df: pd.DataFrame) -> pd.DataFrame:
    # drop features with missing values more than 50%

    missing_val_pct = pd.Series(
        df.isna().sum() / df.shape[0] * 100,
        name='pct')

    cols_todrop = missing_val_pct.loc[missing_val_pct >= 50].index.tolist()

    for col in cols_todrop:

        if col in df.columns:

            df.drop(columns=col, inplace=True)

        else:
            pass

    return df


def drop_duplicated_listings(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df.duplicated(subset='url')]

    assert df.shape[0] == df['url'].nunique(), "There are still repeated listings in the dataset."

    df = df.drop_duplicates(subset = df.drop(columns = 'url').columns)

    return df


def assign_primary_key(df:pd.DataFrame) -> pd.DataFrame:
    # Can add a ID column as primary key for the table
    df['id'] = np.arange(1, df.shape[0] + 1)

    df = df[['id'] + [col for col in df.columns if col != 'id']]

    df = df.set_index('id')

    return df
