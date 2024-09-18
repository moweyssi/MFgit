import streamlit as st
import pandas as pd
import requests
import numpy as np
from io import BytesIO


api_key = st.text_input('Mapy.cz API klic:')

def geocode_address(api_key, query, lang='cs', limit=5):
    url = "https://api.mapy.cz/v1/geocode"
    params = {
        'lang': lang,
        'apikey': api_key,
        'query': query,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses (4XX, 5XX)
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def get_address(address_string):
    response = geocode_address(api_key,address_string)
    st.text(response)
    if response['items']==[]:
        return None
    else:
        regional_address = response['items'][0]['regionalStructure'][0]['name'].split('/')
        # Check if the split resulted in exactly two parts
        if len(regional_address) == 2:
            cislo_domovni = regional_address[0]
            cislo_orientacni = regional_address[1]
        else:
            cislo_domovni = regional_address[0]
            cislo_orientacni = -1
        nazev_ulice =   response['items'][0]['regionalStructure'][1]['name']
        nazev_casti_obce = response['items'][0]['regionalStructure'][2]['name']
        nazev_obce = response['items'][0]['regionalStructure'][3]['name']
        psc = response['items'][0]['zip'].replace(' ','')

        text_address = ', '.join([nazev_ulice,'/'.join(regional_address),nazev_obce,nazev_casti_obce,psc])
        query_vector = np.array([nazev_obce, nazev_casti_obce, nazev_ulice,cislo_domovni,cislo_orientacni,psc])
        return query_vector, text_address


@st.cache_data
def get_data():
    # Fetch and load the file into memory
    embed_response = requests.get('https://raw.githubusercontent.com/moweyssi/MFgit/main/embedding.npy')
    embedding = np.load(BytesIO(embed_response.content), allow_pickle=True)

    adm_id_response = requests.get('https://raw.githubusercontent.com/moweyssi/MFgit/main/ruian_kod.npy')
    adm_id = np.load(BytesIO(adm_id_response.content), allow_pickle=True)
    return embedding, adm_id
embedding, adm_id = get_data()
def extract_int(s):
    # Extract only the numeric characters from the string
    numeric_part = ''.join(filter(str.isdigit, s))
    
    # Convert the numeric part to an integer
    return int(numeric_part)
def get_match(address):
    if address==None:
        return None,None
    else:
        query_vector, text_address = get_address(address)
        string_matches = np.array([
        embedding[:,0]==query_vector[0],
        embedding[:,1]==query_vector[1],
        embedding[:,2]==query_vector[2],
        embedding[:,3]==extract_int(query_vector[3]),
        embedding[:,4]==extract_int(query_vector[4]),
        embedding[:,5]==extract_int(query_vector[5])]).T

        closest_match = string_matches.sum(axis=1)

        return closest_match.argmax(), text_address

# Title of the app
st.title("Kod Adresniho Mista")

# Create an empty DataFrame with three columns and the number of rows selected
df = pd.DataFrame({
    'Adresa': [None]
})
editable_df = st.data_editor(df, num_rows="dynamic", key="editable_df",use_container_width =True)

if st.button("go!",use_container_width=True):
    if api_key is None:
        st.warning("You must provide an API key!")
    else:
        kod_adm = [] 
        mapycz_adresa = []
        my_bar = st.progress(0, text='Working')

        for i in range(len(editable_df['Adresa'])):
            kod, loc = get_match(editable_df['Adresa'][i])
            kod_adm.append(kod)
            mapycz_adresa.append(loc)

            # Correct calculation of percent complete
            percent_complete = (i + 1) / len(editable_df['Adresa']) 
            
            # Update progress bar correctly
            my_bar.progress(percent_complete, text=f'Working ({int(percent_complete * 100)}%)')

        # Display editable DataFrame
        result_df = pd.DataFrame({
            'Adresa': editable_df['Adresa'],
            'Kod Adresniho Mista RUIAN': kod_adm,
            'Mapy CZ Adresa': mapycz_adresa
        })
        show_result = st.dataframe(result_df, use_container_width=True)