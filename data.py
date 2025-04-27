import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import streamlit as st
import csv

# fetching data using aviationstack api
@st.cache_data(ttl=43200)
def get_data():
    url=st.secrets['aviationstack']['URL']
    params={
        'access_key':st.secrets['aviationstack']['API']
    }
    response=requests.get(url,params=params)
    if response.status_code==200:
        data=response.json()
        return data
    elif response.status_code==429:
        return 429
    else:
        print(f'Failed to fetch data {response.status_code}')



def get_cleaned_df():
    #Data extraction and crating Dataframe
    json_data=get_data()
    airline_name=[]
    flight_date=[]
    flight=[]
    flight_status=[]
    departure_airport=[]
    departure_scheduled=[]
    arrival_airport=[]
    arrival_scheduled=[]
    arrival_delay=[]
    departure_iata=[]
    arrival_iata=[]
    if json_data==429:
        st.toast('⚠️ sorry..api usage limit exceeded. Live data cannot be tracked. but still you can see old data.')
     

    else:
        for i in json_data['data']:
            airline_name.append(i['airline']['name'])
            flight_date.append(i['flight_date'])
            flight.append(i['flight']['iata'])
            flight_status.append(i['flight_status'])
            departure_airport.append(i['departure']['airport'])
            departure_scheduled.append(i['departure']['scheduled'])
            arrival_airport.append(i['arrival']['airport'])
            arrival_scheduled.append(i['arrival']['scheduled'])
            arrival_delay.append(i['arrival']['delay'])
            departure_iata.append(i['departure']['iata'])
            arrival_iata.append(i['arrival']['iata'])

        df=pd.DataFrame({'airline_name':airline_name,'flight_date':flight_date,'flight':flight,'flight_status':flight_status,'departure_airport':departure_airport,
                        'departure_scheduled':departure_scheduled,'arrival_airport':arrival_airport,'arrival_scheduled':arrival_scheduled,'arrival_delay':arrival_delay,'departure_iata':departure_iata,'arrival_iata':arrival_iata})

        # Data cleaning
        df['flight']=df['flight'].fillna('Unknown')
        df['arrival_airport']=df['arrival_airport'].fillna('Unknown')
        df['arrival_delay']=df['arrival_delay'].fillna(0)
        df['airline_name']=df['airline_name'].fillna('Unknown')
        departure_time=[datetime.fromisoformat(time).strftime('%I:%M %p') for time in df['departure_scheduled']]
        arrival_time=[datetime.fromisoformat(time).strftime('%I:%M %p') for time in df['arrival_scheduled']]
        df['departure_scheduled']=departure_time
        df['arrival_scheduled']=arrival_time
        df['airline_name']=df['airline_name'].str.replace('empty','Unknown')
        df.index=df.index+1
        df.to_csv('cleaned_flights.csv',mode='w')


    