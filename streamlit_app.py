import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
# from datetime import datetime
# import json

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
                                    "🔊 Theoretische context", 
                                    "🔊 Geoplot geluidoverlast", 
                                    "🔊 pagina 3"])

# Home Page
if page == "🔊 Home":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""
    Dit dashboard geeft inzicht in de theoretische geluids overlast veroorzaakt door vliegtuigen van en naar schiphol.
    Gebruik de navigatie aan de linkerzijde om naar de visualisaties te gaan.
    
    De kaagbaan en polderbaan hebben respectievelijk voorkeur voor aankomende en vertrekkende vluchten, dit omdat deze banen voor minder overlast zorgen. 
    Het wil nog wel eens voorkomen dat er voor andere banen gekozen wordt wegens de veiligheid, het zicht, de wind- en weersomstandigheden, de milieuregels en de beschikbaarheid van de banen.

    Ideen voor meer aanvulling aan de opdracht:
    Aanpassen van vlieggtuig type.
    meer data inwinnen over de vliegtuigen en welke het beste is om geluidsoverlast te minderen.
    Geluidcoefficient aanpasbaar maken
    Meer context krijgen bij de situatie
             
    Team 8:
    - Tammo van Leeuwen, 
    - Jorik Stavenuiter, 
    - Burhan Canbaz, 
    - Quint Klaassen
    """)

elif page == "🔊 Theoretische context":
    st.title("Natuurkundige overlast")
    st.subheader("Hier zullen wij meer context geven bij de overlast veroorzaakt door vliegtuigen")

    st.write("""Gebruik is gemaakt van de inverse square law om per vliegtuig model een coëfficient te berekenen dat weergeeft hoe luid een vligtuig direct onder zich is.""")


elif page == "🔊 Geoplot geluidoverlast":
    st.title("Geoplot geluidoverlast")
    st.subheader("Schiphol Geo visualisatie van het geluidsoverlast van diverse vluchten")

    st.write("""Hieronder kunt u de keuze maken naar het type vlucht en eventueel verder specificeren naar exacte vluchten.
             Het Transfer of Control principe zorgt voor de korte vlucht paden van vertrekkende vluchten. De VFR kaarten hiervoor zijn niet beschikbaar.""")

    @st.cache_data
    def load_and_process_data():
        df = pd.read_csv('timestamp vlucht df.csv')
        
        # Converteer kolommen naar numerieke waarden
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Filter rijen met ontbrekende waarden
        df = df.dropna(subset=['Latitude', 'Longitude', 'FlightType', 'FlightNumber'])
        
        # Simuleer tijdelijke geluidsdata (Noise_Level)
        np.random.seed(42)
        df['Noise_Level'] = np.random.randint(50, 100, size=len(df))
        
        # Unieke vluchtsoorten ophalen (Aankomst/Vertrek)
        vlucht_types = df['FlightType'].unique().tolist()
        vlucht_types.sort()

        # Kleur bepalen op basis van Noise_Level
        def get_noise_color(noise_level):
            """Geeft een kleur op basis van de geluidssterkte"""
            if noise_level < 65:
                return [0, 255, 0, 100]  # Groen (rustig)
            elif noise_level < 80:
                return [255, 165, 0, 150]  # Oranje (middelmatig geluid)
            else:
                return [255, 0, 0, 200]  # Rood (luid)
        
        df['color'] = df['Noise_Level'].apply(get_noise_color)

        # Unieke vluchten ophalen en multiselect maken
        vluchten = df['FlightNumber'].unique().tolist()
        
        return df, vlucht_types, vluchten

    # Laad de data en vluchtsoorten met behulp van de gecachte functie
    df, vlucht_types, vluchten = load_and_process_data()

    # Streamlit interface - Keuze tussen Aankomst of Vertrek
    selected_type = st.radio("Selecteer type vlucht:", vlucht_types)

    # Filter de dataset op basis van vluchtsoort
    df = df[df['FlightType'] == selected_type]

    # Haal de vluchten binnen de geselecteerde vluchtsoort op
    vluchten_binnen_type = df['FlightNumber'].unique().tolist()

    # Voeg de geselecteerde vluchtsoort toe aan de lijst met vluchten
    vluchten_met_type = ["Alle vluchten"] + vluchten_binnen_type

    # Streamlit multiselect met de aangepaste lijst
    selected_flights = st.multiselect("Selecteer vlucht(en):", vluchten_met_type, default=["Alle vluchten"])

    # Filter op geselecteerde vluchten
    if "Alle vluchten" not in selected_flights:
        df_filtered = df[df['FlightNumber'].isin(selected_flights)].copy()
    else:
        df_filtered = df.copy()

    # Streamlit slider om het aantal getoonde vluchten te selecteren
    num_available_flights = len(df_filtered['FlightNumber'].unique())
    max_flights_to_show = st.slider(
        "Aantal vluchten om te tonen:",
        min_value=5,
        max_value=num_available_flights if num_available_flights > 0 else 5,
        value=min(20, num_available_flights) if num_available_flights > 0 else 20,
        step=5
    )
    
    # Haal een gesamplede subset van de DataFrame op basis van het aantal geselecteerde vluchten
    unique_flights_to_show = df_filtered['FlightNumber'].unique()
    if len(unique_flights_to_show) > max_flights_to_show:
        selected_flight_subset = np.random.choice(unique_flights_to_show, size=max_flights_to_show, replace=False)
        df_to_visualize = df_filtered[df_filtered['FlightNumber'].isin(selected_flight_subset)].copy()
    else:
        df_to_visualize = df_filtered.copy()

    # Check of "Alle vluchten" is geselecteerd
    if "Alle vluchten" not in selected_flights:
        df = df[df['FlightNumber'].isin(selected_flights)]

    st.write(f"Toont data van {len(df_to_visualize['FlightNumber'].unique())} vluchten.")
    
    route_layers = []
    for flight_number, flight_df in df.groupby('FlightNumber'):
        route_coordinates = flight_df[['Longitude', 'Latitude']].values.tolist()
    
        if len(route_coordinates) > 1:
            route_layers.append(
                pdk.Layer(
                    "PathLayer",
                    # Data voor de tooltip en path defineren
                    data=[{
                        "path": route_coordinates, 
                        "FlightNumber": flight_number, 
                        "Course": flight_df['Course'].iloc[0], 
                        "Speed": flight_df['Speed_kph'].iloc[0], 
                        "Height": flight_df['Altitude_meters'].iloc[0],
                        "Datetime": flight_df['Time'].iloc[0]
                        }],
                    get_path="path",
                    get_width=4,
                    get_color=[100, 100, 255],
                    width_min_pixels=2,
                    pickable=True, # pickable toegevoegd.
                )
            )

    df['Noise_Level'] = df['Noise_Level'] * 10
    
    # Geluidsimpact toevoegen als cirkels rond elke locatie
    radius_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["Longitude", "Latitude"],
        get_radius='Noise_Level',
        get_fill_color="color",
        pickable=True,
        opacity=0.3,
    )
    
    # Definieer de initiële weergave van de kaart
    initial_view_state = pdk.ViewState(
        latitude=52.308056,
        longitude=4.764167,
        zoom=8
    )
    
    # Maak een pydeck Deck (kaart)
    deck = pdk.Deck(
    layers= route_layers + [radius_layer],
    initial_view_state=initial_view_state,
    map_style="mapbox://styles/mapbox/streets-v11",
    tooltip={
        "html": "<b>Vlucht ID:</b> {FlightNumber}<br/><b>Course:</b> {Course}<br/><b>Speed:</b> {Speed_kph} kph<br/><b>Height:</b> {Altitude_meters} m<br/><b>Time:</b> {Time}",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "z-index": "10000"
        }
    }
)

    # Toon de kaart in Streamlit
    st.pydeck_chart(deck)

elif page == "🔊 pagina 3":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""bonjour""")


    @st.cache_data
    def load_and_process_data():
        df = pd.read_csv('timestamp vlucht df.csv')

        # Converteer kolommen naar numerieke waarden
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

        # Filter rijen met ontbrekende waarden
        df = df.dropna(subset=['Latitude', 'Longitude', 'FlightType', 'FlightNumber', 'Course', 'Speed_kph', 'Altitude_meters', 'Time'])

        # Simuleer tijdelijke geluidsdata (Noise_Level)
        np.random.seed(42)
        df['Noise_Level'] = np.random.randint(50, 100, size=len(df))

        # Unieke vluchtsoorten ophalen (Aankomst/Vertrek)
        vlucht_types = df['FlightType'].unique().tolist()
        vlucht_types.sort()

        # Kleur bepalen op basis van Noise_Level
        def get_noise_color(noise_level):
            """Geeft een kleur op basis van de geluidssterkte"""
            if noise_level < 65:
                return [0, 255, 0, 100]  # Groen (rustig)
            elif noise_level < 80:
                return [255, 165, 0, 150]  # Oranje (middelmatig geluid)
            else:
                return [255, 0, 0, 200]  # Rood (luid)

        df['color'] = df['Noise_Level'].apply(get_noise_color)

        # Unieke vluchten ophalen
        vluchten = df['FlightNumber'].unique().tolist()
        vluchten.sort()

        return df, vlucht_types, vluchten

    # Laad de data en vluchtsoorten met behulp van de gecachte functie
    df_full, vlucht_types, vluchten_all = load_and_process_data()

    # Streamlit interface - Keuze tussen Aankomst of Vertrek
    selected_type = st.radio("Selecteer type vlucht:", vlucht_types)

    # Filter de dataset op basis van vluchtsoort
    df_filtered_by_type = df_full[df_full['FlightType'] == selected_type].copy()

    # Keuze tussen slider en multiselect
    selection_mode = st.radio("Selecteer weergavemodus:", ["Slider (willekeurige subset)", "Multiselect (specifieke vluchten)"])

    df_to_visualize = pd.DataFrame()  # Initialiseer de DataFrame voor visualisatie

    if selection_mode == "Slider (willekeurige subset)":
        num_available_flights = len(df_filtered_by_type['FlightNumber'].unique())
        max_flights_to_show = st.slider(
            "Aantal vluchten om te tonen:",
            min_value=5,
            max_value=num_available_flights if num_available_flights > 0 else 5,
            value=min(20, num_available_flights) if num_available_flights > 0 else 20,
            step=5
        )
        unique_flights_all = df_filtered_by_type['FlightNumber'].unique()
        if len(unique_flights_all) > max_flights_to_show:
            selected_flight_subset = np.random.choice(unique_flights_all, size=max_flights_to_show, replace=False)
            df_to_visualize = df_filtered_by_type[df_filtered_by_type['FlightNumber'].isin(selected_flight_subset)].copy()
        else:
            df_to_visualize = df_filtered_by_type.copy()

    elif selection_mode == "Multiselect (specifieke vluchten)":
        vluchten_binnen_type = df_filtered_by_type['FlightNumber'].unique().tolist()
        vluchten_binnen_type.sort()
        vluchten_met_type = ["Alle vluchten"] + vluchten_binnen_type
        selected_flights = st.multiselect("Selecteer vlucht(en):", vluchten_met_type, default=["Alle vluchten"])
        if "Alle vluchten" not in selected_flights:
            df_to_visualize = df_filtered_by_type[df_filtered_by_type['FlightNumber'].isin(selected_flights)].copy()
        else:
            df_to_visualize = df_filtered_by_type.copy()

    st.write(f"Toont data van {len(df_to_visualize['FlightNumber'].unique())} vluchten.")

    st.write(df_to_visualize)

    route_layers = []
    for flight_number, flight_df in df_to_visualize.groupby('FlightNumber'):
        route_coordinates = flight_df[['Longitude', 'Latitude']].values.tolist()

        if len(route_coordinates) > 1:
            route_layers.append(
                pdk.Layer(
                    "PathLayer",
                    data=[{
                        "path": route_coordinates,
                        "FlightNumber": flight_number,
                        "Course": flight_df['Course'].iloc[0],
                        "Speed": flight_df['Speed_kph'].iloc[0],
                        "Height": flight_df['Altitude_meters'].iloc[0],
                        "Datetime": flight_df['Time'].iloc[0]
                    }],
                    get_path="path",
                    get_width=4,
                    get_color=[100, 100, 255],
                    width_min_pixels=2,
                    pickable=True,
                )
            )

    df_to_visualize['Noise_Level'] = df_to_visualize['Noise_Level'] * 10

    # Geluidsimpact toevoegen als cirkels rond elke locatie (gebaseerd op df_to_visualize)
    radius_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_to_visualize,
        get_position=["Longitude", "Latitude"],
        get_radius='Noise_Level',
        get_fill_color="color",
        pickable=True,
        opacity=0.3,
        tooltip={
            "html": "<b>Vlucht ID:</b> {FlightNumber}<br/><b>Course:</b> {Course}<br/><b>Speed:</b> {Speed_kph} kph<br/><b>Height:</b> {Altitude_meters} m<br/><b>Time:</b> {Time}",
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "z-index": "10000"
            }
        }
    )

    # Definieer de initiële weergave van de kaart
    initial_view_state = pdk.ViewState(
        latitude=52.308056,
        longitude=4.764167,
        zoom=8
    )

    # Maak een pydeck Deck (kaart)
    deck = pdk.Deck(
        layers= route_layers + [radius_layer],
        initial_view_state=initial_view_state,
        map_style="mapbox://styles/mapbox/streets-v11"
    )

    # Toon de kaart in Streamlit
    st.pydeck_chart(deck)