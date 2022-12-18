#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 10:29:53 2022

@author: samuelwong
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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


def get_district(address: str) -> str:
    """Return the second last name in the address which usualy corresponds to the district name.

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

def check_metrics(model, X_train, X_valid, y_train, y_valid):
    mae_train = mean_absolute_error(y_train, model.predict(X_train))
    mae_valid = mean_absolute_error(y_train, model.predict(X_train))
    mse_train = mean_squared_error(y_train, model.predict(X_train))
    mse_valid = mean_squared_error(y_valid, model.predict(X_valid))
    rmse_train = np.sqrt(mean_squared_error(y_train, model.predict(X_train)))
    rmse_valid = np.sqrt(mean_squared_error(y_valid, model.predict(X_valid)))
    r2_train = r2_score(y_train, model.predict(X_train))
    r2_valid = r2_score(y_valid, model.predict(X_valid))
    print(f'MAE train score : {mae_train}')
    print(f'MAE train score : {mae_valid}')
    print(f'MSE train score : {mse_train}')
    print(f'MSE valid score : {mse_valid}')
    print(f'RMSE train score : {rmse_train}')
    print(f'RMSE valid score : {rmse_valid}')
    print(f'R2 train score : {r2_train}')
    print(f'R2 valid score : {r2_valid}')
    return [mae_train, mae_valid, mse_train, mse_valid, rmse_train, rmse_valid, r2_train, r2_valid]

def pivot_table_plot(row: str, col: str, value: str = 'price') -> None:
    table = df[[row,col,value]]
    result = pd.pivot_table(data=table, index = row,
                            columns=col, aggfunc='count',
                            fill_value=0)
    f, ax = plt.subplots(figsize=(14,10))
    sns.heatmap(result, annot=True, fmt="d", linewidths=.5, ax=ax, vmin=0, vmax=np.floor(result.max().max()/3), cmap = 'GnBu')
    plt.title(f'Pivot Table of {row} & {col} by count', fontsize = 18, fontweight = 'bold');