#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 11:00:31 2022

@author: samuelwong
"""

import bitdotio
from dotenv import load_dotenv
import os


class PropertyGuruDatabase():

    def __init__(self):
        pass

    def __load_credentials(self):
        """Read credentials from environment file (.env)"""

        load_dotenv()

        self.__api_key = os.getenv("BITDOTIO_API_KEY")
        self.__db_name = os.getenv("BITDOTIO_DATABASE")
        self.__postgres_url = os.getenv('BITDOTIO_URL')

    def load_preprocessed_data_to_db(self):
        """Read and load preprosessed dataset into bit.io from csv file"""

        self.__load_credentials()

        b = bitdotio.bitdotio(self.__api_key)

        # Create table, if it does not already exist
        create_cleaned_old_table_sql = """
            CREATE TABLE IF NOT EXISTS clean_data (
            id integer PRIMARY KEY,
            price numeric,
            sqft numeric,
            bedrooms numeric,
            bathrooms numeric,
            listing_tags text,
            furnishing text,
            tenure text,
            state text,
            district text,
            landed_vs_high_rise text,
            pool text,
            fitness text,
            balcony text,   
            log_price numeric
        );
        """

        # For preprocessed data
        create_preprocessed_table_sql = """
            CREATE TABLE IF NOT EXISTS preprocessed_data (
            id integer PRIMARY KEY,
            price numeric,
            listing_title text,
            sqft numeric,
            bedrooms numeric,
            bathrooms numeric,
            address text,
            price_per_sqft numeric,
            listing_tags text,
            furnishing text,
            tenure text,
            floor_size_det numeric,
            url text,
            state text,
            district text,
            pool text,
            fitness text,
            balcony text 
        );
        """

        delete_table_sql = """DELETE FROM preprocessed_data;"""

        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_preprocessed_table_sql)

        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_table_sql)

        # Copy csv from a local file
        copy_table_sql = """
            COPY preprocessed_data FROM stdin WITH CSV HEADER DELIMITER as ',';
            """

        with open('Processed_data_for_EDA.csv', 'r') as f:
            with b.get_connection(self.__db_name) as conn:
                cursor = conn.cursor()
                cursor.copy_expert(sql=copy_table_sql, file=f)

    def load_cleaned_data_to_db(self):
        """Read and load cleaned dataset into bit.io from csv file"""
        self.__load_credentials()

        b = bitdotio.bitdotio(self.__api_key)

        # For preprocessed data
        create_clean_table_sql = """
            CREATE TABLE IF NOT EXISTS cleaned_data (
            id integer PRIMARY KEY,
            price numeric,
            listing_title text,
            sqft numeric,
            bedrooms numeric,
            bathrooms numeric,
            address text,
            listing_tags text,
            furnishing text,
            tenure text,
            url text,
            state text,
            pool text,
            fitness text,
            balcony text ,
            log_price numeric, 
            sqft_boxcox numeric, 
            landed_high_rise text, 
            district_enc text
        );
        """

        delete_table_sql = """DELETE FROM cleaned_data;"""

        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_clean_table_sql)

        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_table_sql)

        # Copy csv from a local file
        copy_table_sql = """
            COPY cleaned_data FROM stdin WITH CSV HEADER DELIMITER as ',';
            """

        with open('clean_data_v2.csv', 'r') as f:
            with b.get_connection(self.__db_name) as conn:
                cursor = conn.cursor()
                cursor.copy_expert(sql=copy_table_sql, file=f)
