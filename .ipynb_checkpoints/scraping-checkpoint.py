#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 20:31:48 2022

@author: samuelwong
"""

from bs4 import BeautifulSoup
import cloudscraper
import time
import requests
import pandas as pd
import numpy as np
import os
import hashlib
import argparse
import pprint
import random
import glob


def run_scraper(url, max_trials = 10):
    '''Run cloud scraper to bypass cloudflare and return soup object'''
    num_trials = 0 # initial number of trials made
    success = False
    while success != True:
        if num_trials <= max_trials: # if the num of trials still have not exceeded max trials
            try:
                scraper = cloudscraper.create_scraper(delay=10)
                s = scraper.get(url)
                soup = BeautifulSoup(s.content, 'html.parser')
                success = True
            except:
                # print('trying... ')
                time.sleep(2)
                num_trials += 1
        else:
            soup = None
            break
            
    return soup

def get_listings_url(startpage, endpage):
    ''' Generate a list of urls for different pages'''
    list_urls = []
    for i in range(startpage, endpage + 1):
        if i == 1:
            url = 'https://www.propertyguru.com.my/property-for-sale?listing_type=sale&market=residential&region_code=MY10&freetext=Selangor&search=true'
            list_urls.append(url)
        else:
            url = f'https://www.propertyguru.com.my/property-for-sale/{i}?freetext=Selangor&region_code=MY10&search=true'
            list_urls.append(url)
            
    return list_urls

def extract_info(soup):
    
    # price of property
    try:
        price = soup.find('span', {'class': 'element-label price'}).get_text().replace('\n','').strip()
    except:
        price = np.nan
    
    # listing title
    try:
        listing_title = soup.find('div', {'class': 'listing-detail-header-bar container clearfix'})\
                            .h1.text.replace('\n', '').strip()
    except:
        listing_title = np.nan
        
        
    # listing subtitle
    try:
        listing_subtitle = soup.find('div', {'class': 'listing-detail-header-bar container clearfix'})\
                            .h2.get_text()
    except:
        listing_subtitle = np.nan
    
    # property name (may be same as listing title)
    try:
        name = soup.find('div', {'class': 'listing-title text-transform-none'}).text
    except:
        name = np.nan
    
    # property sqft
    try:
        sqft = soup.find('div', {'class': 'property-info-element area'})\
                .get_text().replace('\n','').replace('sqft', '').strip()
    except:
        sqft = np.nan
    
    # num of bedrooms
    try:
        bedrooms = soup.find('div', {'class': 'property-info-element beds'}).span.text.strip()
    except:
        bedrooms = np.nan
    # num of bathrooms        
    try:
        bathrooms = soup.find('div', {'class': 'property-info-element baths'}).span.text.strip()
    except:
        bathrooms = np.nan
    # address
    try:
        address = soup.find('div', {'class': 'listing-address'}).span.text
    except:
        address = np.nan
    
    try:
        price_per_sqft = soup.find('span', {'class': 'price-value'}).text
    except:
        price_per_sqft = np.nan

    # listings tags
    try:
        listing_tags = soup.find('ul', {'class': 'listing-property-type'}).get_text().replace('\n', ',').split(',')
        listing_tags = ', '.join([a for a in listing_tags if a != ''])
    except:
        listing_tags = np.nan
        
    # listings descriptions
    try:
        listings_desc = soup.find('div', {'class': 'listing-details-text'}).get_text()
    except:
        listings_desc = np.nan
        
    # extract details from the "Detail" divider
    try:
        # find all items under the "Detail" divider
        details = soup.find('div', {'id': 'details'}).find_all('tbody', {'class': 'col-xs-12 col-sm-6'})

        output_dict = {}
        for det in details:
            # item title as dict key, item value as dict value
            output_dict[det.h4.get_text().strip()] = det.find('td', {'class': 'value-block'}).get_text().strip()
    except:
        pass
    
    try:
        developer = output_dict['Developer']
    except:
        developer= np.nan
    try:
        property_title_type = output_dict['Property Title Type']
    except:
        property_title_type= np.nan
    try:
        furnishing = output_dict['Furnishing']
    except:
        furnishing= np.nan
    try:
        built_year = output_dict['Built Year']
    except:
        built_year= np.nan
    try:
        listed_on = output_dict['Listed on']
    except:
        listed_on= np.nan
    try:
        tenure = output_dict['Tenure']
    except:
        tenure = np.nan
    try:
        property_type = output_dict['Property Type']
    except:
        property_type = np.nan 
    try:
        floor_lv = output_dict['Floor Level']
    except:
        floor_lv = np.nan
    try:
        psf_det = output_dict['PSF']
    except:
        psf_det = np.nan
    try:
        floor_size_det = output_dict['Floor size']
    except:
        floor_size_det = np.nan
   
    # getting number of units for the project
    num_units = np.nan
    try:
        div_tag = list(soup.find('div', {'class': 'condo-profile-box__project-info'}).children) # all the tags under the divider

        for i in div_tag:
            try:
                if i.find('div', {'class': 'label-block'}).text == 'Total Unit(s)':
                    num_units = i.find('div', {'class': 'value-block'}).text
            except:
                pass
    except:
        pass
    
    # list of facilities
    try:
        facilities_table = soup.find('div', {'id': 'facilities'}).find_all('li')

        facilities = []

        for i in facilities_table:
            facilities.append(i.get_text().replace('\n', '').strip())

        facilities = ', '.join(facilities)
    except:
        facilities = np.nan
    
    return [price, listing_title, listing_subtitle, name, sqft, bedrooms, bathrooms, address,
            price_per_sqft, listing_tags, listings_desc, developer, property_title_type, 
            furnishing, built_year, listed_on, tenure, property_type, floor_lv, psf_det, floor_size_det,
               num_units, facilities]

page_urls = get_listings_url(1, 50)
page_urls

unit_listings_url = []
failed_page = []
# go through every page and extract all the listings' urls
for i, url in enumerate(page_urls):
    # print(f'Scraping page {i}')
    if i%5==0:
        print(f'Scraping page {i}')
        
    soup = run_scraper(url)
    
    # if the scraper failed:
    if soup is None:
        failed_page.append(url)
        print(failed_page)
    else:
        # return all the listing's url
        for val in list(soup.find_all('a', {'class': 'nav-link'})):
            unit_listings_url.append(val['href'])
    # sleep
    tosleep = random.randint(1,5)
    time.sleep(tosleep)
    
print(f'Num of listings: {len(unit_listings_url)}')
print(f'Num of unique listings: {len(set(unit_listings_url))}')
pprint.pprint(unit_listings_url[:5])

working_dir = '/Users/samuelwong/Projects/PropertyGuru Analysis/Web Scraping'

# change working directory
if os.getcwd() != working_dir:
    os.chdir(working_dir)
    print(os.getcwd())
else:
    print(os.getcwd())
        
# get the latest full dataset file and get the scraped url
latest_file = sorted(glob.glob('Full_dataset*.csv'))[0]

scraped_data = pd.read_csv(latest_file)

scraped_listings = scraped_data['url'].tolist()

# obtaining the unique urls only
unique_listings = list(set(unit_listings_url))

# make sure the listings to be scraped are not scraped in advanced
unscraped_listings = []
for link in unique_listings:
    if link not in scraped_listings:
        unscraped_listings.append(link)
        
print(len(unscraped_listings))


listings_data = []
links_with_issues = []

starttime = time.time()

print(f'Num of listings to be scraped: {len(unscraped_listings)}')
for i, link in enumerate(unscraped_listings): # separate it into [:400], [400:800], [800:1200], [1200:]
    if i % 10 == 0:
        print(i)
    
    soup = run_scraper(link)
    
    if soup is None:
        # log the links with issues
        links_with_issues.append(link)
        print(f'{len(links_with_issues)} links got issues')
    else:
        if 'Starting from' not in soup.get_text():
            listing_row = extract_info(soup)
            listing_row.append(link)
            listings_data.append(listing_row)
        else:
            pass
    
    tosleep = random.randint(1,5)
    time.sleep(tosleep)

endtime = time.time()
duration = endtime - starttime
print(f'Total time took: {round(duration/60,1)}mins')

column_names = [
    'price', 'listing_title', 'listing_subtitle', 'name', 'sqft', 'bedrooms', 'bathrooms', 'address',
    'price_per_sqft', 'listing_tags', 'listings_desc', 'developer', 'property_title_type', 
    'furnishing', 'built_year', 'listed_on', 'tenure', 'property_type', 'floor_lv', 'psf_det', 'floor_size_det',
    'num_units', 'facilities', 'url'
]

df = pd.DataFrame(listings_data, columns = column_names)

# df.to_csv('selangor_1-50_20221130.csv')




