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
        
        load_dotenv()

        self.__api_key = os.getenv("BITDOTIO_API_KEY")
        self.__db_name = os.getenv("BITDOTIO_DATABASE")
        self.__postgres_url = os.getenv('BITDOTIO_URL')
        
    def load_data_to_db(self):
        
        self.__load_credentials()
        
        b = bitdotio.bitdotio(self.__api_key)
    
        # Create table, if it does not already exist
        create_table_sql = """
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
        
        delete_table_sql = """DELETE FROM clean_data;"""
        
        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
        
        with b.get_connection(self.__db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(delete_table_sql)
            
        # Copy csv from a local file
        copy_table_sql = """
            COPY clean_data FROM stdin WITH CSV HEADER DELIMITER as ',';
            """
        
        with open('clean_data.csv', 'r') as f:
            with b.get_connection(self.__db_name) as conn:
                cursor = conn.cursor()
                cursor.copy_expert(sql=copy_table_sql, file=f)
            
            
            