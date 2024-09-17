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
    text_address = response['items'][0]['name']
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


    print("nazev_obce: ",nazev_obce)
    print("nazev_casti_obce: ",nazev_casti_obce)
    print("nazev_ulice: ",nazev_ulice)
    print("cislo_domovni: ",cislo_domovni)
    print("cislo_orientacni: ",cislo_orientacni)
    print("psc: ",psc)
    query_vector = np.array([nazev_obce, nazev_casti_obce, nazev_ulice,cislo_domovni,cislo_orientacni,psc])
    return query_vector, text_address

def get_match(address,embedding):
    query_vector, text_address = get_address(address)
    string_matches = np.array([
    embedding[:,0]==query_vector[0],
    embedding[:,1]==query_vector[1],
    embedding[:,2]==query_vector[2],
    embedding[:,3]==int(query_vector[3]),
    embedding[:,4]==int(query_vector[4]),
    embedding[:,5]==int(query_vector[5])]).T

    closest_match = string_matches.sum(axis=1)

    print(str(int((100*closest_match.max()/6)))+ "% match")
    return closest_match.argmax(), text_address

@st.cache_data
def get_data():
    # Fetch and load the file into memory
    embed_response = requests.get('https://raw.githubusercontent.com/moweyssi/MFgit/main/embedding.npy')
    embedding = np.load(BytesIO(embed_response.content), allow_pickle=True)

    adm_id_response = requests.get('https://raw.githubusercontent.com/moweyssi/MFgit/main/ruian_kod.npy')
    adm_id = np.load(BytesIO(adm_id_response.content), allow_pickle=True)
    return embedding, adm_id
embedding, adm_id = get_data()

# Title of the app
st.title("Dynamic DataFrame with Editable Column")

# Slider to select the number of rows
num_rows = st.number_input('Set the number of rows', min_value=1, max_value=100, value=5, step=1)
# Create an empty DataFrame with three columns and the number of rows selected
df = pd.DataFrame({
    'Adresa': [None] * num_rows
})

# Display editable DataFrame
editable_df = st.data_editor(df, num_rows="dynamic", key="editable_df",use_container_width =True)
result_df = pd.DataFrame({
    'Adresa': editable_df['Adresa'],
    'Kod Adresniho Mista RUIAN': editable_df['Adresa'],
    'Mapy CZ Adresa': editable_df['Adresa']
})
result_df['Kod Adresniho Mista RUIAN'], result_df['Mapy CZ Adresa'] = result_df['Adresa'].apply(get_match(embedding=embedding))

show_result = st.dataframe(result_df,use_container_width =True)
