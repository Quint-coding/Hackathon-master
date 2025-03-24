import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

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

    # df["coordinates"] = df["waypoints"].apply(lambda f: [item["coordinates"] for item in f])
    # df["timestamps"] = df["waypoints"].apply(lambda f: [item["timestamp"] - 1554772579000 for item in f])

    # df.drop(["waypoints"], axis=1, inplace=True)

    # df['path'] = df['Latitude'].astype('string') + ", " + df['Longitude'].astype('string')

    df['path'] = df.apply(lambda row: [[row['Longitude'], row['Latitude']]], axis=1)

    layer = pdk.Layer(
        "TripsLayer",
        df,
        get_path="path",
        get_timestamps="timestamp",
        get_color=[253, 128, 93],
        opacity=0.8,
        width_min_pixels=5,
        rounded=True,
        trail_length=600,
        current_time=500,
    )

    view_state = pdk.ViewState(latitude=52.3080392, 
                               longitude=4.7621975, 
                               zoom=11, 
                               bearing=0, 
                               pitch=45)

    deck = pdk.Deck(layers=[layer], initial_view_state=view_state)

    # Render the map in Streamlit
    st.pydeck_chart(deck)


elif page == "🔊 pagina 2":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""hello""")


elif page == "🔊 pagina 3":
    st.title("Geluid overlast")
    st.subheader("Welkom bij ons schiphol dashboard over geluid overlast")

    st.write("""bonjour""")