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
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split


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

    return df


def assign_primary_key(df:pd.DataFrame) -> pd.DataFrame:
    # Can add a ID column as primary key for the table
    df['id'] = np.arange(1, df.shape[0] + 1)

    df = df[['id'] + [col for col in df.columns if col != 'id']]

    df = df.set_index('id')

    return df

def drop_cols(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        try:
            df = df.drop(columns=col)
            assert col not in df.columns, f"{col} was not drop."
        except:
            print(f"{col} not in dataset.")

    return df

def get_district(address: str) -> str:
    """Return the second last name in the address which usually
        corresponds to the district name.

    Parameters
    --------
    address: str
        The address of the property or listing.

    Returns
    -------
    str
        The district name, if no district then the state will be returned.
    """
    words_ls = str(address).split(',')

    if len(words_ls) <= 1:
        return address.strip()
    else:
        return words_ls[-2].strip()

def swimming_pool(facilities: str) -> bool:
    if ('swimming pool' in facilities.lower()) | ('pool' in facilities.lower()):
        return True
    else:
        return False


def fitness(facilities: str) -> bool:
    if ('fitness' in facilities.lower()) | ('gym' in facilities.lower()):
        return True
    else:
        return False


def balcony(facilities: str) -> bool:
    if 'balcony' in facilities.lower():
        return True
    else:
        return False

def get_cols_with_na_morethan_2pct(df: pd.DataFrame) -> list:
    missing_prop = (df.isna().sum()) / df.shape[0] * 100
    target_cols = missing_prop[(missing_prop <= 2)].index.tolist()
    return target_cols

class RFImputer:

    def __init__(self, df:pd.DataFrame, col: str):
        self.col = col
        self.df = df

    def __separate_na_index(self):
        self.na_ind = (
            self.df[self.df[self.col].isna()] # find all rows where the target col has missing values
            .index # obtain the indices
            .tolist() # convert to list
        )

        # get all the indices where the target col does not contain missing values
        self.non_na_ind = [val for val in self.df.index.tolist() if val not in self.na_ind]

        assert len(self.na_ind) + len(self.non_na_ind) == self.df.shape[0]

    def run_model(self):

        self.__separate_na_index()

        # initialize a random forest classifer
        rf = RandomForestClassifier(random_state=42)

        cols_include = ['price', 'sqft', 'bedrooms', 'bathrooms', 'price_per_sqft',
                        'listing_tags', 'district', 'pool', 'fitness', 'balcony']

        # perform ordinal encoder
        enc = OrdinalEncoder()

        X = self.df.loc[:, cols_include].copy()
        cols_transform = X.select_dtypes('object').columns.tolist()

        X.loc[:, cols_transform] = enc.fit_transform(X[cols_transform])

        X_notna = X.loc[self.non_na_ind, :]
        y_notna = self.df.loc[self.non_na_ind, self.col]

        X_train, X_test, y_train, y_test = train_test_split(X_notna, y_notna, test_size=0.2, random_state=42)
        X_train, X_valid, y_train, y_valid = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
        rf.fit(X_train, y_train)

        X_na = self.df.loc[self.na_ind, cols_include].copy()

        X_na.loc[:, cols_transform] = enc.fit_transform(X_na[cols_transform])

        y_na = rf.predict(X_na)

        self.df.loc[self.na_ind, self.col] = y_na

        assert self.df[self.col].isna().sum() == 0

        return self.df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:

    cols_to_drop = ['name','listings_desc','listed_on',
                    'property_type','psf_det','facilities',
                    'property_title_type']

    # Price
    df['price'] = (
        df['price']
        .astype('str')
        .str.replace(',', '')
        .astype('float')
    )

    assert df['price'].dtype == 'float', "Feature 'price' is not float type."

    # Sqft
    df['sqft'] = (
        df['sqft']
        .astype('str')
        .str.replace(',', '')
        .str.replace('acre', '')
        .str.strip()
        .astype('float')
    )

    assert df['sqft'].dtype == 'float', "Feature 'sqft' is not float type."

    # Bedrooms
    map_dict = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
               '7': 7, '8': 8, '9': 9, '10': 10, 'Studio': 0,
               'studio': 0}

    df['bedrooms'] = df['bedrooms'].astype('str').map(map_dict)

    df['bedrooms'] = df['bedrooms'].astype('float')

    assert df['bedrooms'].dtype == 'float', "Feature 'bedrooms' is not float type."

    # bathrooms
    df['bathrooms'] = df['bathrooms'].astype('float')

    assert df['bathrooms'].dtype == 'float', "Feature 'bathrooms' is not float type."

    # price per sqft
    try:
        df['price_per_sqft'] = df['price_per_sqft'].astype('float')
    except:
        # means there is string in the values
        df['price_per_sqft'] = df['price_per_sqft'].astype('str').apply(lambda x: x.replace(',', ''))
        df['price_per_sqft'] = df['price_per_sqft'].astype('float')

    assert df['price_per_sqft'].dtype == 'float', "Feature 'price_per_sqft' is not float type."

    # state
    df['state'] = (
        df['address']
        .astype('str')
        .apply(lambda x: x.split(',')[-1])
    )

    # district
    df['district'] = (
        df['address']
        .astype('str')
        .apply(get_district)
    )

    # floor_size_det
    df['floor_size_det'] = (
        df['floor_size_det']
        .str.replace('sqft', '')
        .str.replace(',', '')
        .str.strip()
        .astype('float')
    )

    assert df['floor_size_det'].dtype == 'float', "Feature 'floor_size_det' is not float type."

    df['pool'] = df['facilities'].astype('str').apply(swimming_pool)

    df['fitness'] = df['facilities'].astype('str').apply(fitness)

    df['balcony'] = df['facilities'].astype('str').apply(balcony)

    # Missing values
    target_cols = get_cols_with_na_morethan_2pct(df)

    df = df.dropna(axis=0, how='any', subset=target_cols)

    # inpute finishing
    model = RFImputer(df, 'furnishing')
    df = model.run_model()

    # impute tenure
    df['tenure'].fillna(df['tenure'].mode().values[0], inplace=True)

    assert df['tenure'].isna().sum() == 0

    df = drop_cols(df, cols_to_drop)

    return df

