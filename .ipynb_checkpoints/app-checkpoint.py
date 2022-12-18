import streamlit as st
import numpy as np
import glob
from joblib import dump, load
import pandas as pd
import os
from scipy.special import boxcox1p
from sklearn.preprocessing import OrdinalEncoder


def load_model():
    """Load the pre-trained model into memory."""
    pattern = 'models/rf*.joblib'
    filenames = glob.glob(pattern)
    filenames = sorted(filenames)
    model = load(filenames[-1])
    return model


def encoder(cols):
    enc = OrdinalEncoder()
    df = load_dataset()
    enc.fit(df[cols])
    return enc
    


def format_prediction(val: str) -> str:
    starter = -3
    num_separator = len(val) // 3

    if len(val) % 3 == 0:
        for i in range(num_separator - 1):
            val = val[:starter] + ',' + val[starter:]
            starter = starter - 3 - (i + 1)
    else:
        for i in range(num_separator):
            val = val[:starter] + ',' + val[starter:]
            starter = starter - 3 - (i + 1)

    return val

def imposed_constriant(df: pd.DataFrame):
    high_rise_tag = df[df.landed_high_rise == 'high-rise']['listing_tags'].unique().tolist()
    landed_tag = df[df.landed_high_rise == 'landed']['listing_tags'].unique().tolist()
    output = None
    tag = None
    if (property_type_selected in high_rise_tag) & (landed_high_rise_selected == 'landed'):
        output = True
        tag = 'high-rise'
    elif (property_type_selected in landed_tag) & (landed_high_rise_selected == 'high-rise'):
        output = True
        tag = 'landed'
    else:
        output = False
    return output, tag



def preprocess_prediction():
    prediction = np.array([sqft_selected, num_bedrooms_selected, num_bathrooms_selected,
                          property_type_selected, tenure_selected,
                          district_choice_selected, landed_high_rise_selected,
                          pool_selected, gym_selected, balcony_selected])

    prediction = prediction.reshape(1, -1)

    columns = ['sqft',
               'bedrooms',
               'bathrooms',
               'listing_tags',
               'tenure',
               'district_enc',
               'landed_high_rise',
               'pool',
               'fitness',
               'balcony']

    prediction_df = pd.DataFrame(prediction, columns=columns)

    raw_prediction_df = prediction_df.copy()

    bool_map = {'Yes': True, 'No': False}

    prediction_df['sqft'] = prediction_df['sqft'].astype('float64')
    
    lam = 0.1
    prediction_df['sqft_boxcox'] = boxcox1p(prediction_df['sqft'], lam)
    prediction_df = prediction_df.drop(columns = 'sqft')
    
    prediction_df['bedrooms'] = prediction_df['bedrooms'].astype('float64')
    prediction_df['bathrooms'] = prediction_df['bathrooms'].astype('float64')
    prediction_df['pool'] = prediction_df['pool'].map(bool_map).astype('bool')
    prediction_df['fitness'] = prediction_df['fitness'].map(bool_map).astype('bool')
    prediction_df['balcony'] = prediction_df['balcony'].map(bool_map).astype('bool')

    enc_cols = ['listing_tags','tenure','pool','fitness','balcony','landed_high_rise','district_enc']
    
    enc = encoder(enc_cols)
    prediction_df[enc_cols] = enc.transform(prediction_df[enc_cols])
    
    cols_order = ['bedrooms', 'bathrooms','listing_tags','tenure','pool','fitness','balcony','sqft_boxcox','landed_high_rise','district_enc']
    
    prediction_df = prediction_df[cols_order]
    return prediction_df, raw_prediction_df

def make_prediction():

    prediction_df, raw_prediction_df = preprocess_prediction()

    st.dataframe(raw_prediction_df, use_container_width = True)

    model = load_model()

    iserror, tag = imposed_constriant(df)

    if iserror:
        st.warning('The property type chosen does not tally.')
        st.warning(f'{property_type_selected} should be {tag}.')
    else:
        pass

    output = model.predict(prediction_df)[0]

    output = np.exp(output)

    return output


def load_dataset(filename: str = 'data/Cleaned_data_for_modelling.csv') -> pd.DataFrame:
    try:
        df = pd.read_csv(filename)
        return df
    except:
        raise FileNotFoundError(f'Datafile {filename} is not found. ')
        return None


df = load_dataset()

st.title('PropertyGuru Sales Property Prediction')

st.sidebar.header('Please choose which type of property do you want to predict:')
property_type_options = df['listing_tags'].unique().tolist()
property_type_selected = st.sidebar.selectbox(label='What type of property are you look for?',
                                              options=property_type_options)

sqft_selected = st.sidebar.slider(label='Decide the squared feet of your property: ',
                                  min_value=50, max_value=15000, value=500, step=50)

num_bedrooms_selected = st.sidebar.slider(label='Decide the number of bedrooms of your property: ',
                                          min_value=0, max_value=10, value=1, step=1)

num_bathrooms_selected = st.sidebar.slider(label='Decide the number of bathrooms of your property: ',
                                           min_value=0, max_value=10, value=1, step=1)

landed_high_rise_selected = st.sidebar.selectbox(label='Do you want landed or high-rise property?',
                                                 options=['landed', 'high-rise'])

district_options = df['district_enc'].unique().tolist()

district_choice_selected = st.sidebar.selectbox(label='Which district do you prefer to purchase the property?',
                                                options=district_options)

tenure_options = df['tenure'].unique().tolist()
tenure_selected = st.sidebar.selectbox(label='What type of property tenure are you look for?',
                                       options=tenure_options)

pool_selected = st.sidebar.radio(label='Do you want to have swimming pool?',
                                 options=['Yes', 'No'], index=0)

gym_selected = st.sidebar.radio(label='Do you want to have fitness facilities such as gym?',
                                options=['Yes', 'No'], index=0)

balcony_selected = st.sidebar.radio(label='Do you want to have balcony?',
                                    options=['Yes', 'No'], index=0)


predicted_price = str(int(make_prediction()))

predicted_price = format_prediction(predicted_price)

st.header('Predicted Property Price: ')
st.subheader(f'RM {predicted_price}')
