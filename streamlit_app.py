import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime
import json

# Set page configuration
st.set_page_config(page_title="Schiphol geluidoverlast Dashboard", page_icon="🔊", layout="wide")

# Custom CSS to style the sidebar (dark theme)
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #1E1E1E !important;  /* Dark sidebar */
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] p {
            color: white !important;  /* White text */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("📍 Navigatie")
page = st.sidebar.radio("Ga naar", ["🔊 Home", 
                                    "🔊 pagina 1", 
                                    "🔊 pagina 2", 
                                    "🔊 pagina 3"])

# Home Page
if page == "🔊 Home":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""
    Dit dashboard geeft inzicht in de overlast veroorzaakt door vliegtuigen van en naar schiphol.
    Gebruik de navigatie aan de linkerzijde om naar de visualisaties te gaan.
    
    
    De kaagbaan en polderbaan hebben respectievelijk voorkeur voor aankomende en vertrekkende vluchten, dit omdat deze banen voor minder overlast zorgen. 
             Het wil nog wel eens voorkomen dat er voor andere banen gekozen wordt wegens de veiligheid, het zicht, de wind- en weersomstandigheden, de milieuregels en de beschikbaarheid van de banen.

    op basis van data over het weer en omwonende bepalen hoe de landingsbanen anders ingericht kunnen worden.
             
    optie om klachten aantal  op een kaart te visualiseren

    Team 8:
    - Tammo van Leeuwen, 
    - Jorik Stavenuiter, 
    - Burhan Canbaz, 
    - Quint Klaassen
    """)

elif page == "🔊 pagina 1":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""hello""")

    df = pd.read_csv('timestamp vlucht data.csv')

    # Converteer kolommen naar numerieke waarden
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    # Filter rijen met ontbrekende waarden
    df = df.dropna(subset=['Latitude', 'Longitude', 'FlightType', 'FlightNumber'])
    
    # Unieke vluchtsoorten ophalen (Aankomst/Vertrek)
    vlucht_types = df['FlightType'].unique().tolist()
    vlucht_types.sort()
    
    # Streamlit interface - Keuze tussen Aankomst of Vertrek
    selected_type = st.radio("Selecteer type vlucht:", vlucht_types)
    
    # Filter de dataset op basis van vluchtsoort
    df = df[df['FlightType'] == selected_type]
    
    # Unieke vluchten ophalen
    vluchten = df['FlightNumber'].unique().tolist()
    vluchten.insert(0, "Alle vluchten")  # Voeg optie toe om alles te tonen
    
    # Streamlit interface - Keuze van vlucht
    selected_flight = st.selectbox("Selecteer een vlucht:", vluchten)
    
    # Filter de dataset op basis van de selectie
    if selected_flight != "Alle vluchten":
        df = df[df['FlightNumber'] == selected_flight]
    
    # Maak een lijst van vluchten als afzonderlijke routes
    route_layers = []
    for flight_number, flight_df in df.groupby('FlightNumber'):
        route_coordinates = flight_df[['Longitude', 'Latitude']].values.tolist()
    
        # Voeg alleen routes toe met minstens twee punten
        if len(route_coordinates) > 1:
            # Kleur bepalen: Blauw voor Aankomst, Groen voor Vertrek, Rood als een specifieke vlucht is geselecteerd
            if selected_flight != "Alle vluchten":
                color = [255, 0, 0]  # Rood voor de geselecteerde vlucht
            else:
                color = [0, 0, 255] if selected_type == "Arrivals" else [0, 255, 0]  # Blauw = Aankomst, Groen = Vertrek
    
            route_layers.append(
                pdk.Layer(
                    "PathLayer",
                    data=[{"path": route_coordinates}],
                    get_path="path",
                    get_width=4,
                    get_color=color,
                    width_min_pixels=2,
                )
            )
    
    # Definieer de initiële weergave van de kaart
    initial_view_state = pdk.ViewState(
        latitude=df['Latitude'].mean(),
        longitude=df['Longitude'].mean(),
        zoom=8,
        pitch=0,
    )
    
    # Maak een pydeck Deck (kaart)
    deck = pdk.Deck(
        layers=route_layers,
        initial_view_state=initial_view_state,
        map_style="mapbox://styles/mapbox/streets-v11",
    )
    
    # Toon de kaart in Streamlit
    st.pydeck_chart(deck)
    

elif page == "🔊 pagina 2":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""hello""")

elif page == "🔊 pagina 3":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""bonjour""")