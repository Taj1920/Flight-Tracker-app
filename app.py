import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import json
import threading as th
from data import get_cleaned_df

st.set_page_config(page_title='Flight Tracker Dashboard',page_icon='images/flight_tracker.png',layout='wide',initial_sidebar_state='auto')
def load_anime():
    file='flight_anime.json'
    with open(file,'r') as f:
        return json.load(f)

st.sidebar.image('images/flight_tracker.png')
selected=option_menu(menu_title=None,options=['Home','Flights','Dashboard'],orientation='horizontal',icons=['house','bi-airplane','bi-bar-chart-line'])
get_cleaned_df()
df=pd.read_csv('cleaned_flights.csv').drop('Unnamed: 0',axis=1)
if not df.empty:
    with st.sidebar:
        airline_name=st.selectbox('**Airline Name**',options=['All']+list(df['airline_name'].unique()))
        flight_status=st.selectbox('**Flight Status**',options=['All']+list(df['flight_status'].unique()))
        flight_date=st.selectbox('**Flight Date**',options=['All']+list(df['flight_date'].unique()))
        departure_airport=st.selectbox('**Departure Airport**',options=['All']+sorted(list([str(i) for i in df['departure_airport'].unique()])))
        departure_time=st.selectbox('**Departure Time**',options=['All']+sorted(list(df['departure_scheduled'].unique())))

    #filters
    filtered = df.copy()
    if airline_name != 'All':
        filtered = filtered[filtered['airline_name'] == airline_name]

    if flight_status != 'All':
        filtered = filtered[filtered['flight_status'] == flight_status]

    if flight_date != 'All':
        filtered = filtered[filtered['flight_date'] == flight_date]

    if departure_time != 'All':
        filtered = filtered[filtered['departure_scheduled'] == departure_time]
    if departure_airport!='All':
        filtered = filtered[filtered['departure_airport'] == departure_airport]

    filtered = filtered.reset_index(drop=True)
    filtered.index = filtered.index + 1
    if selected=='Home':
        col1,col2=st.columns(2)
        with col1:
            anime=load_anime()
            st_lottie(anime,width=500,height=350,speed=10,quality='low')
        col2.subheader('Welcome! to Flight Tracker App')
        col2.write("Easily track and explore real-time flights.")
        col2.markdown('''**App Features:**
                    <br>
                    -> Real time updates.
                    <br>
                    -> Track Flights by Airline name,date,departure airport etc.
                    <br>
                    -> Track Flight status in Dashboard Section.
                    <br>
                    -> Check Flight details in Flights Section.
                    
                    ''',unsafe_allow_html=True)
        col2.write('**App Navigation:**')
        col2.markdown("🛩️ Flights: Check for available flights")
        col2.markdown("📊 Dashboard: Visual overview of flight trends")
        col2.markdown("🏠 Home: You are here!")

    elif selected=='Flights':
        if airline_name!='All':
            with st.container(border=True,height=350):
                for i in range(1,len(filtered)+1):
                    st.markdown(f'''<h3 style="text-align:center">{filtered['airline_name'][i]}''',unsafe_allow_html=True)
                    a1,a2,a3,a4=st.columns(4,border=True,)
                    a1.image('images/flight_png.png',width=350)
                    a2.write(f"**Flight:** {filtered['flight'][i]}")
                    a2.write(f"**Date:** {filtered['flight_date'][i]}")
                    a2.write(f"**Status:** {filtered['flight_status'][i]}")
                    a3.write(f"**Departure:** {filtered['departure_airport'][i]}")
                    a3.write(f"**Scheduled:** {filtered['departure_scheduled'][i]}")
                    a3.write(f"**iata:** {filtered['departure_iata'][i]}")
                    a4.write(f"**Arrival:** {filtered['arrival_airport'][i]}")
                    a4.write(f"**Scheduled:** {filtered['arrival_scheduled'][i]}")
                    a4.write(f"**Delay:** {filtered['arrival_delay'][i]}")
                    a4.write(f"**iata:** {filtered['arrival_iata'][i]}")
                    st.write('---')
        else:
            filtered=filtered.sort_values(by='departure_scheduled').reset_index().drop('index',axis=1)
            filtered.index=filtered.index+1
            st.dataframe(filtered, height=350)
            st.info('👉 use **Airline Name** dropdown on the left to see specific flights.')
    elif selected=='Dashboard':
        choice=st.pills(None,options=['Page 1','Page 2','Page 3'],selection_mode='single',default='Page 1')
        if choice=='Page 1':
            a1,a2=st.columns([1,2],vertical_alignment='top',border=True)
            with a1:
                flight_status_count=filtered.groupby('flight_status')['flight_status'].count()
                flight_status_count=pd.DataFrame(flight_status_count).rename(columns={'flight_status':'count'}).reset_index()
                st.markdown('''<h6 style="text-align:center;">Flight status''',unsafe_allow_html=True)
                fig=px.pie(flight_status_count,values=flight_status_count['count'],names=flight_status_count['flight_status'],hole=0.6,height=350,color='flight_status',color_discrete_map={'scheduled':'#F77534','landed':'#f4d03f','active':'#af601a','cancelled':'#f0b27a'})
                st.plotly_chart(fig)
            with a2:
                total_flights=filtered['airline_name'].count()
                scheduled=filtered['flight_status'][filtered['flight_status']=='scheduled'].count()
                landed=filtered['flight_status'][filtered['flight_status']=='landed'].count()
                cancelled=filtered['flight_status'][filtered['flight_status']=='cancelled'].count()
                active=filtered['flight_status'][filtered['flight_status']=='active'].count()
                m1,m2,m3,m4,m5=st.columns(5,border=True)
                m1.image('icons/bi-flights.png',width=60)
                m1.metric('Total Flights',value=total_flights)

                m2.image('icons/takeoff.png',width=60)
                m2.metric('Scheduled',value=scheduled)

                m3.image('icons/landed.png',width=60)
                m3.metric('Landed',value=landed)

                m4.image('icons/cancel.png',width=60)
                m4.metric('Cancelled',value=cancelled)

                m5.image('icons/active.png',width=60)
                m5.metric('Active',value=active)
                
                st.bar_chart(filtered,x='flight',y='arrival_delay',height=200,x_label='Flight',y_label='Delay (mins)',color='#F77534')
                
        elif choice=='Page 2':
            b1,b2=st.columns([1,2],gap='small',vertical_alignment='top',border=True)
            with b1:
                st.markdown('''<h6 style="text-align:center;">Count of Flights over Time''',unsafe_allow_html=True)
                time_count=pd.DataFrame(filtered['departure_scheduled'].value_counts().reset_index())
                st.line_chart(time_count,x='departure_scheduled',y='count',x_label='Time',y_label='count',height=350,color='#F77534')
            with b2:
                airline_count=pd.DataFrame(filtered['airline_name'].value_counts()).reset_index()
                st.subheader(' ')
                st.markdown('''<h6 style="text-align:center">Count of Flights by Airline''',unsafe_allow_html=True)
                st.bar_chart(airline_count,y='count',x='airline_name',x_label='Airline',y_label='Count',height=300,color='#F77534')
        elif choice=='Page 3':
            #Map
            @st.cache_data(ttl=43200)
            def flight_map():
                df1=pd.read_csv('airports.csv')
                df1=df1[df1['iata_code'].notnull()]
                df1=df1.iloc[:,[4,5,13]].reset_index().drop('index',axis=1)
                df1.index=df1.index+1
                dep=df1.rename(columns={'iata_code':'departure_iata'})
                arrival=df1.rename(columns={'iata_code':'arrival_iata'})
                merged=pd.merge(filtered,dep,on='departure_iata').rename(columns={'latitude_deg':'dep_lat','longitude_deg':'dep_lon'})
                df1=pd.merge(merged,arrival,on='arrival_iata').rename(columns={'latitude_deg':'arr_lat','longitude_deg':'arr_lon'})
                fig=go.Figure()

                for i in range(len(df1)):
                    fig.add_trace(go.Scattermapbox(mode='lines+markers',lat=[df1['dep_lat'][i],df1['arr_lat'][i]],
                                                                        lon=[df1['dep_lon'][i],df1['arr_lon'][i]],showlegend=False,text=f"✈️ {df1['airline_name'][i]} ({df1['departure_airport'][i]} to {df1['arrival_airport'][i]})"))

                fig.update_layout(
                    mapbox = {
                        'style': "open-street-map",  # You can use 'satellite' with a token
                        'zoom': 2,
                        'center': {'lat': 22.5, 'lon': 78.9}
                    },
                    height=450,
                    margin={"r":0,"t":0,"l":0,"b":0}
                )
                st.plotly_chart(fig) 

            
            with st.spinner('Map is Loading...',show_time=True):
                time.sleep(3)
                flight_map()        


