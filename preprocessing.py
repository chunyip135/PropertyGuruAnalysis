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

def import_data(working_dir: str = '/Users/samuelwong/Projects/PropertyGuru Analysis/Web Scraping/Working')-> pd.DataFrame:
    '''Import data from different csv files and combine into 1 full dataset.
    
    Parameters
    ---------
    working_dir: str, optional
        working directory path name. By defaul, '~/Projects/PropertyGuru Analysis/Web Scraping'
        
    Returns
    -------
    pd.DataFrame
        The dataframe containing the full dataset.
    '''
    # check working directory
    if os.getcwd() != working_dir:
        os.chdir(working_dir)
        print(os.getcwd())
    else:
        print(os.getcwd())
        
    
    # find all the target csv files
    csv_pattern = 'selangor_*.csv'
    all_csv = glob.glob(csv_pattern)
    try:
        all_csv.remove('selangor_pg1-9.csv')
    except:
        pass
    
    # read the csv files and join into 1 dataframe
    df_full = pd.DataFrame({})
    n_obs = 0 # initialize counter
    
    for file in all_csv:
        df_tmp = pd.read_csv(file)
        n_obs += df_tmp.shape[0]
        
        if 'Unnamed: 0' in df_tmp.columns:
            df_tmp = df_tmp.drop(columns = 'Unnamed: 0')
        else:
            pass
        
        df_full = pd.concat([df_full, df_tmp])
    
    assert df_full.shape[0] == n_obs, 'The # of obs in the final dataset is not same as the total obs of all files.'
    
    return df_full


def save_data(df: pd.DataFrame, filename: str) -> None:
    '''Save dataset into csv format
    
    Parameters
    ---------
    df: pd.DataFrame, 
        The dataframe which contains the data to be saved.
    filename: str,
        The name of the csv file to be generated.
    Returns
    -------
    None
    '''
    
    if filename[-4:] != '.csv':
        filename = filename.strp() + '.csv'
    else:
        pass
    
    try:
        df.to_csv(filename, index=False)
        print(f"File saved successfully as {filename}.")
    except Exception as e:
        print(e)
        
def get_district(address: str) -> str:
    '''Return the second last name in the address which usualy corresponds to the district name.
        
    Parameters
    --------
    address: str
        The address of the property or listing.
            
    Returns
    -------
    str
        The district name, if no district then the state will be returned.
    '''
    words_ls= str(address).split(',')
        
    if len(words_ls) <= 1:
        return address.strip()
    else:
        return words_ls[-2].strip()

def landed_or_high_rise(tag: str) -> str:
    '''Classify the property as landed or high-rise based on the listing's tag.
        
    Parameters
    ---------
    tag: str
        The tag shown in the listing.
    
    Returns
    -------
    str
        'landed' or 'high-rise' property.
    '''
    landed_prop = ['house', 'bungalow', 'land', 'villa']
    high_rise_prop = ['apartment','apart','flat','penthouse','condominium','townhouse','condo', 'residence', 'studio', 'duplex']
    
    output = None
    # landed
    for cat in landed_prop:
        if cat in tag.lower():
            output = 'landed'
    
    for cat in high_rise_prop:
        if cat in tag.lower():
            output = 'high-rise'
    
    if output is None:
        output = 'Others'
            
    return output


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
        
def cleaning_data(df: pd.DataFrame) -> pd.DataFrame:
        
    # df_original = df.copy()
    
    df['price'] = (
        df['price']
        .astype('str')
        .str.replace(',','')
        .astype('float')
    )
    
    # convert the feature's datatype to float
    df['sqft'] = (
        df['sqft']
        .astype('str')
        .str.replace(',', '')
        .str.replace('acre', '')
        .str.strip()
        .astype('float')
    )
    
    df['bathrooms'] = df['bathrooms'].astype('float')
    
    # map the number of bedrooms to the correct value (int)
    map_dict = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'Studio': 0, 'studio': 0}
    
    
    df['bedrooms'] = df['bedrooms'].astype('str').map(map_dict)
    
    df['bedrooms'] = df['bedrooms'].astype('float')
    
    # address
    df['state'] = df['address'].astype('str')\
                    .apply(lambda x: x.split(',')[-1])
    
    # district
        
    df['district'] = df['address'].astype('str')\
                        .apply(get_district)
    
    # landed vs condo
    df['listing_tags'] = df['listing_tags'].astype('str')
    
    df['landed_vs_high_rise'] = df['listing_tags']\
                                    .apply(landed_or_high_rise)\
                                    .astype('str')
    
    # type of property: terraced house, condo, service residence, aprtment, duplex, villa, townhouse, bungalow, others
    
    # swimming pool & gym
            
    df['pool'] = df['facilities'].astype('str').apply(swimming_pool)
        
    df['fitness'] = df['facilities'].astype('str').apply(fitness)
    
    facilities_ls = []
    for i, row in df.iterrows():
        tmp_var = str(row['facilities']).split(',')
        tmp_var = [a.strip().lower() for a in tmp_var]
        for faci in tmp_var:
            if faci not in facilities_ls:
                facilities_ls.append(faci)
        
    df['balcony'] = df['facilities'].astype('str').apply(balcony)
    
    # take the log transformation of the price column to reduce the range 
    df['log_price'] = np.log(df['price'])
    
    df['id'] = np.arange(1, df.shape[0] + 1)
    
    df = df[ ['id'] + [ col for col in df.columns if col != 'id' ] ]
    
    return df


def drop_missing_val(df: pd.DataFrame) -> pd.DataFrame:
    
    # if price then remove the row
    # if sqft then impute the average mean of the same bedrooms or bathroom
    # drop features with missing values more than 50%
    # drio all the features with missing values more than 50%
    missing_val_pct = pd.Series(
        df.isna().sum() / df.shape[0] * 100, 
        name = 'pct')
    
    cols_todrop = missing_val_pct.loc[missing_val_pct >= 50].index.tolist()
    
    cols_todrop += ['psf_det','floor_size_det','url',
                    'property_title_type','property_type', 
                    'listings_desc', 'facilities', 'name',
                    'address','listed_on', 'listing_title','price_per_sqft']
    
    for col in cols_todrop:
        
        if col in df.columns:
            
            df.drop(columns=col, inplace = True)
        
        else:
            pass
    
    return df

def drop_duplicated_listings(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df[~df.duplicated(subset = 'url')]
    
    assert df.shape[0] == df['url'].nunique(), "There are still repeated listings in the dataset."
    
    return df









