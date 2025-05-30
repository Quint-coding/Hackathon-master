import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from scipy.optimize import curve_fit
from scipy import stats
from sklearn.metrics import r2_score
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
                                    "🔊 Analyse vliegtuig modellen",
                                    "🔊 Geoplot geluidoverlast",
                                    "🔊 Conclusies & Discussie",
                                    "testing"
                                    ])


@st.cache_data
def load_and_process_data():
    df = pd.read_csv('timestamp vlucht df.csv')

    # Converteer kolommen naar numerieke waarden
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # Filter rijen met ontbrekende waarden
    df = df.dropna(subset=['Latitude', 'Longitude', 'FlightType', 'FlightNumber', 'Course', 'Speed_kph', 'Altitude_meters', 'Time'])

    # Unieke vluchtsoorten ophalen (Aankomst/Vertrek)
    vlucht_types = df['FlightType'].unique().tolist()
    vlucht_types.sort()

    # Kleur bepalen op basis van Noise_Level
    def get_noise_color(noise_level):
        """Gives a smooth color transition from red (high noise) → orange → green (low noise)"""
        
        if noise_level < 60:
            # Below 60 dB: Light Green
            return [50, 205, 50, 150]  # LimeGreen (softer than LightGreen)
        
        elif noise_level < 75:
            # 60 - 75 dB: Smooth transition from green to orange
            factor = (noise_level - 60) / (75 - 60)  # 0 to 1
            red = int(255 * factor + 50 * (1 - factor))  # 50 (green) → 255 (orange)
            green = int(165 * factor + 205 * (1 - factor))  # 205 (green) → 165 (orange)
            blue = 0  # No blue for a clean transition
            return [red, green, blue, 180]
        
        elif noise_level < 90:
            # 75 - 90 dB: Transition from orange to red
            factor = (noise_level - 75) / (90 - 75)  # 0 to 1
            red = 255  # Always full red
            green = int(165 * (1 - factor) + 50 * factor)  # 165 (orange) → 50 (deep red)
            blue = 0  # Keep pure warm colors
            return [red, green, blue, 200]
        
        else:
            # Above 90 dB: Deep Red
            return [255, 50, 50, 220]  # Strong red (softened with a slight reduction in blue)

    df['color'] = df['Noise_Level'].apply(get_noise_color)

    # Unieke vluchten ophalen
    vluchten = df['FlightNumber'].unique().tolist()
    vluchten.sort()

    return df, vlucht_types, vluchten
# Home Page
if page == "🔊 Home":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""
    Dit dashboard geeft inzicht in de theoretische geluids overlast veroorzaakt door vliegtuigen van en naar schiphol.
    Gebruik de navigatie aan de linkerzijde om naar de visualisaties te gaan.
    
    De kaagbaan en polderbaan hebben respectievelijk voorkeur voor aankomende en vertrekkende vluchten, dit omdat deze banen voor minder overlast zorgen. 
    Het wil nog wel eens voorkomen dat er wordt gekozen voor andere banen wegens de veiligheid, het zicht, de wind- en weersomstandigheden, de milieuregels en de beschikbaarheid van de banen.
             
    Team 8:
    - Tammo van Leeuwen, 
    - Jorik Stavenuiter, 
    - Burhan Canbaz, 
    - Quint Klaassen
    """)


    st.image("Schiphol-plaza-ns.jpg")
    

elif page == "🔊 Theoretische context":
    st.title("Natuurkundige overlast")
    st.subheader("Hier zullen wij meer context geven bij de overlast veroorzaakt door vliegtuigen")

    st.write("""Gebruik is gemaakt van de inverse square law om per vliegtuig model een coëfficient te berekenen dat weergeeft hoe luid een vligtuig direct onder zich is.""")


    df = pd.read_csv('Geluid per callsign.csv')
    # Verwijder ongeldige waarden (NaN, oneindige waarden, en negatieve hoogtes)
    df_cleaned = df.dropna(subset=['max_db_onder', 'altitude'])
    df_cleaned = df_cleaned[~df_cleaned['max_db_onder'].isin([float('inf'), float('-inf')])]
    df_cleaned = df_cleaned[df_cleaned['altitude'] > 0]  # Ensure positive altitude for log


    if df_cleaned.empty:
        st.warning("Waarschuwing: De data is leeg na het opschonen. Er kan niets worden geplot.")
        st.stop()

    # Sorteer de DataFrame op 'altitude' (goede praktijk voor visualisatie)
    df_cleaned = df_cleaned.sort_values(by='altitude')

    # Gegeven data
    afstanden = df_cleaned['altitude']
    decibels = df_cleaned['max_db_onder']

    # Logarithmic function for fitting
    def logaritmische_functie(afstand, a, b):
        return a + b * np.log10(afstand)

    # Fit the data to the logarithmic function
    try:
        parameters, _ = curve_fit(logaritmische_functie, afstanden, decibels, p0=[90, -10])  # Initial guesses
        a, b = parameters
        st.write(f"Fit parameters: a = {a:.2f}, b = {b:.2f}") # Display fitted parameters
    except RuntimeError as e:
        st.error(f"Optimalisatie is mislukt: {e}. Controleer de data of probeer andere startwaarden.")
        st.stop()

    # Genereer lijn voor de fitting
    x_fit = np.linspace(min(afstanden), max(afstanden), 100)
    y_fit = logaritmische_functie(x_fit, a, b)
    fit_df = pd.DataFrame({'altitude': x_fit, 'max_db_onder_fit': y_fit}) # Create DataFrame for fit line

    # Bereken de R²-waarde
    y_pred = logaritmische_functie(afstanden, a, b)
    r2 = r2_score(decibels, y_pred)
    st.write(f"R²-waarde: {r2:.2f}")

    # Create a scatter plot with Plotly
    fig = px.scatter(df_cleaned, x='altitude', y='max_db_onder',
                    labels={'altitude': 'Hoogte (meter)', 'max_db_onder': 'Max Geluidsniveau Onder (dB)'},
                    title=f"Relatie tussen Vlieghoogte en Maximaal Geluidsniveau",
                    hover_data=['altitude', 'max_db_onder'],
                    opacity=0.8)

    # Add the fitted line to the plot (AFTER adding the scatter plot)
    fig.add_trace(px.line(fit_df, x='altitude', y='max_db_onder_fit',
                        color_discrete_sequence=['red'],
                        labels={'max_db_onder_fit': f'y = {a:.2f} + {b:.2f} * log10(x)'}).data[0])

    # Show the plot in Streamlit
    st.plotly_chart(fig)

    df = pd.read_csv('Geluid per callsign.csv')

    # Convert relevant columns to numeric if they aren't already
    numeric_cols = ['max_db_onder', 'altitude']
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=numeric_cols, inplace=True)

    # Filter the DataFrame based on the number of entries per type
    filtered_df = df.groupby('type').filter(lambda x: len(x) >= 100) # Reduced for example data

    st.subheader("Scatterplot of Altitude vs. dB with Logarithmic Fits")

    if not filtered_df.empty:
        fig = px.scatter(filtered_df, x='max_db_onder', y='altitude', color='type',
                        labels={'max_db_onder': 'Max Geluidsniveau Onder (dB)', 'altitude': 'Hoogte (meter)'},
                        title='Altitude vs. Max dB Onder by Type with Logarithmic Fits', 
                        opacity= 0.8)

        # Function for logarithmic fit
        def logaritmische_functie(afstand, a, b):
            return a + b * np.log10(afstand)

        unique_types = filtered_df['type'].unique()
        fit_equations = {}

        for aircraft_type in unique_types:
            group = filtered_df[filtered_df['type'] == aircraft_type].copy()
            afstanden = group['max_db_onder']
            decibels = group['altitude']

            try:
                parameters, covariantie = curve_fit(logaritmische_functie, afstanden, decibels)
                a, b = parameters

                x_fit = np.linspace(min(afstanden), max(afstanden), 100)
                y_fit = logaritmische_functie(x_fit, a, b)

                r2 = r2_score(decibels, logaritmische_functie(afstanden, a, b))
                fit_equations[aircraft_type] = f"y = {a:.2f} + {b:.2f} * log10(x) (R² = {r2:.2f})"

                fig.add_scatter(x=x_fit, y=y_fit, mode='lines', name=f'{aircraft_type} Fit')

            except (RuntimeError, ValueError):
                st.warning(f"Could not perform logarithmic fit for {aircraft_type}.")
                fit_equations[aircraft_type] = "Fit failed"

        # Limit the y-axis to start from 0
        fig.update_layout(yaxis=dict(range=[0, filtered_df['altitude'].max() * 1.1])) # Adjust multiplier as needed

        st.plotly_chart(fig)

        st.subheader("Logarithmic Fit Equations:")
        for aircraft_type, equation in fit_equations.items():
            st.write(f"{aircraft_type}: {equation}")

    else:
        st.warning("Not enough data points per 'type' to display the plot after filtering.")

elif page == "🔊 Analyse vliegtuig modellen":
    st.title("Kenmerken van vliegtuigmodellen")
    st.subheader("Hier zullen wij a.d.h.v. meerdere grafieken 4 vliegtuigmodellen vergelijken")

    st.write("""Er is gekozen voor 4 vliegtuigmodellen op basis van de natuurkundige analyse die hiervoor is verricht.
             Deze 4 modellen kwamen het meest voor en gaven daardoor een betrouwbaar beeld bij hun geluidsoverlast.""")

    plane_specs = pd.read_csv('plane_specs_zonder_fouten.csv')

    fig1 = px.bar(plane_specs, 'type', 'seats', color='type', title='Passagierscapaciteit per vliegtuigmodel')

    fig2 = px.bar(plane_specs, 'max_takeoff_weight_t', 'type', color='type', title='Startgewicht (\'massa rijklaar\' in autotermen) per vliegtuigmodel')

    fig3 = px.bar(plane_specs, 'type', 'range_km', color='type', title='Actieradius per vliegtuigmodel')

    fig4 = px.bar(plane_specs, 'seats', 'range_km', color='type', title='Actieradius per passagierscapaciteit')

    fig5 = px.bar(plane_specs, 'max_takeoff_weight_t', 'range_km', color='type', title='Actieradius per startgewicht (\'massa rijklaar\' in autotermen)')

    fig6 = px.bar(plane_specs, 'empty_weight_t', 'range_km', color='type', title='Actieradius per leeggewicht (\'massa ledig voertuig\' in autotermen)')

    fig7 = px.bar(plane_specs, 'wingspan_m', 'range_km', color='type', title=('Actieradius per spanwijdte'))

    # fig4 = px.bar(plane_specs, 'seats', 'ceiling_m', color='type', title='Dienstplafond per passagierscapaciteit')

    # fig5 = px.bar(plane_specs, 'max_takeoff_weight_t', 'ceiling_m', color='type', title='Dienstplafond per startgewicht (\'massa rijklaar\' in autotermen)')

    # fig6 = px.bar(plane_specs, 'empty_weight_t', 'ceiling_m', color='type', title='Dienstplafond per leeggewicht (\'massa ledig voertuig\' in autotermen)')



    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)
    st.plotly_chart(fig5)
    st.plotly_chart(fig6)
    st.plotly_chart(fig7)

elif page == "🔊 Geoplot geluidoverlast":

    tab1, tab2= st.tabs(['2D Geoplot geluidoverlast', "3D Geoplot geluidoverlast"])

    with tab1:
        st.title("Geoplot geluidoverlast")
        st.subheader("Schiphol Geo visualisatie van het geluidsoverlast van diverse vluchten")

        st.write("""Hieronder kunt u de keuze maken naar het type vlucht en eventueel verder specificeren naar exacte vluchten.
                Het Transfer of Control principe zorgt voor de korte vlucht paden van vertrekkende vluchten. De VFR kaarten hiervoor zijn niet beschikbaar.""")

        # Laad de data en vluchtsoorten met behulp van de gecachte functie
        df_full, vlucht_types, vluchten_all = load_and_process_data()

        # Layer selectie
        layer_choice = st.radio(
        "Kies de visualisatielaag:",
        ["Geluidszones (Cirkels)","Geluidszones (heatmap)"]
        )


        # Streamlit interface - Keuze tussen Aankomst of Vertrek
        selected_type = st.radio("Selecteer type vlucht:", vlucht_types)

        # Filter de dataset op basis van vluchtsoort
        df_filtered_by_type = df_full[df_full['FlightType'] == selected_type].copy()

        # Keuze tussen slider e         n multiselect
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

        # Create Pydeck Layers
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
                            "Speed_kph": flight_df['Speed_kph'].iloc[0],
                            "Altitude_meters": flight_df['Altitude_meters'].iloc[0],
                            "Time": flight_df['Time'].iloc[0]
                        }],
                        get_path="path",
                        get_width=4,
                        get_color=[100, 100, 255],
                        width_min_pixels=2,
                        pickable=True,
                    )
                )

        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=df_to_visualize,
            get_position=["Longitude", "Latitude"],
            get_weight="Noise_Level",
            radius=500,
            intensity=1,
            opacity=0.6
        )

        # Geluidsimpact toevoegen als cirkels rond elke locatie (gebaseerd op df_to_visualize)
        df_to_visualize['Noise_Level_expanded'] = (df_to_visualize['Noise_Level'] * df_to_visualize['Noise_Level']) / 5

        radius_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_to_visualize,
            get_position=["Longitude", "Latitude"],
            get_radius='Noise_Level_expanded',
            get_fill_color="color",
            pickable=True,
            opacity=0.3
        )

        if layer_choice == "Geluidszones (Cirkels)":
            selected_layers = route_layers + [radius_layer]
        elif layer_choice == "Geluidszones (heatmap)":
            selected_layers = route_layers + [heatmap_layer]

        # Define initial view
        initial_view_state = pdk.ViewState(
            latitude=52.308056,
            longitude=4.764167,
            zoom=8
        )

        # Fix tooltip formatting
        tooltip = {
            "html": """
                <b>Flight ID:</b> {FlightNumber}<br/>
                <b>Course:</b> {Course}<br/>
                <b>Speed:</b> {Speed_kph} kph<br/>
                <b>Height:</b> {Altitude_meters} m<br/>
                <b>Time:</b> {Time}<br/>
                <b>Noise level:</b> {Noise_Level}
            """,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "z-index": "10000"
            }
        }

        deck = pdk.Deck(
            layers=selected_layers,
            initial_view_state=initial_view_state,
            map_style="mapbox://styles/mapbox/streets-v11",
            tooltip=tooltip
        )


        # Toon de kaart in Streamlit
        st.pydeck_chart(deck)

    with tab2:
        st.title("Geoplot geluidoverlast (Basic 3D)")
        st.subheader("Basic 3D Visualization of Flight Paths with Matplotlib")
        st.write("This is a basic 3D visualization of flight paths using Matplotlib. It is not interactive in the same way as PyDeck.")

        df_full, vlucht_types, vluchten_all = load_and_process_data()

        selected_type = st.radio("Selecteer type vlucht:", vlucht_types)
        df_filtered_by_type = df_full[df_full['FlightType'] == selected_type].copy()

        selected_flights = st.multiselect("Selecteer vlucht(en):", df_filtered_by_type['FlightNumber'].unique(), default=df_filtered_by_type['FlightNumber'].unique()[:5])
        df_to_visualize = df_filtered_by_type[df_filtered_by_type['FlightNumber'].isin(selected_flights)].copy()

        st.write(f"Visualizing {len(df_to_visualize['FlightNumber'].unique())} flights.")

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        for flight_number, flight_df in df_to_visualize.groupby('FlightNumber'):
            lon = flight_df['Longitude'].values
            lat = flight_df['Latitude'].values
            alt = flight_df['Altitude_meters'].values
            ax.plot(lon, lat, alt, label=flight_number)

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Altitude (meters)')
        ax.set_title(f'3D Flight Paths ({selected_type})')
        ax.legend()

        st.pyplot(fig)

elif page == "🔊 Conclusies & Discussie":

    st.title("Conclusie en Discussie")

    st.subheader("Conclusies")

    st.write("""- Geluid heeft een logaritmische verband met afstand. 
            - Het model geeft een goede voorspelling tussen de hoogtes 100 - 1000 m.
            - Verschillende vliegtuig modellen hebben verschillende coefficienten en de Embraer heeft onze voorkeur.             
            - Boeing 777 is een groot vliegtuig die veel geluid maakt.
            - Stijgende vliegtuigen zijn sneller minder hoorbaar dan dalende vliegtuigen.
            - Schiphol maakt duidelijk gebruik van verschillende aanvlieg en vertrek routes.
            - Voor minder overlast kunnen deze routes gewijzigd worden.""")

    st.subheader("Discussies")

    st.write("""Weer meenemen in coefficient bepaling, gemiddelde coeeficient gebruiken voor modellen waar de coefficient niet is berekend, weinig metingen op hogere afstanden
                Dataset van de vliegtuig specificaties.
                Heatmap is werkt niet samen met zoomlevel.
                Scatterplot kaart geeft niet goed weer dat het geluid zachter wordt naarmate deze verder is van de bron.
                """)
    
elif page == "testing":

    # Title
    st.title("✈️ 3D Flight Path Viewer (from Parquet)")

    df = pd.read_parquet('flights_hackaton_20230701-20230801.parquet')

    st.write(df.head())

    # Ensure required columns exist
    required_columns = {'lat', 'lon', 'alt', 'flight_id'}
    if not required_columns.issubset(df.columns):
        st.error(f"Parquet file must contain columns: {required_columns}")
        st.stop()

    # Let user select one flight
    flight_ids = df['flight_id'].unique()
    selected_flight = st.selectbox("Select a Flight ID to Visualize", flight_ids)

    # Filter only the selected flight
    flight_data = df[df['flight_id'] == selected_flight]

    # Create the 3D plot
    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=flight_data['lon'],
        y=flight_data['lat'],
        z=flight_data['alt'],
        mode='lines',
        line=dict(
            color=flight_data['alt'],
            colorscale='Viridis',
            width=3
        ),
        name=str(selected_flight)
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude (ft)',
            aspectratio=dict(x=2, y=1, z=0.5),
            bgcolor='rgba(240,240,240,0.95)'
        ),
        title=f'3D Flight Path: {selected_flight}',
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)