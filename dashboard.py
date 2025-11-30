import streamlit as st
import pandas as pd
import pydeck as pdk

from src.tg_scraper.scraper import get_telegram_post_text
from src.styles import hide_streamlit_style
from src.transcriber.llm_transcriber import extract_location_local_prompt
from src.geocoder.geocoder import geocode_location
from src.firms.firms_grabber import fetch_fires


st.set_page_config(
    page_title="Telegram Post Mapper",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if 'fires_df' not in st.session_state:
    st.session_state.fires_df = None
if 'strike_location' not in st.session_state:
    st.session_state.strike_location = None


def process_telegram_post(url, get_fires_data):
    progress_bar = st.progress(0)
    
    try:
        extracted_text = get_telegram_post_text(url)
        if not extracted_text:
            st.error("Scraping failed or post contains no text content.", icon="❌")
            return
        
        with st.expander("Extracted text"):
            st.write(extracted_text)
        progress_bar.progress(33)
        
        with st.spinner("Extracting location data...", show_time=True):
            location_data = extract_location_local_prompt(extracted_text)
        
        if not location_data:
            st.error("Location data extraction failed.", icon="❌")
            return
        
        with st.expander("Extracted location data"):
            st.write(location_data)
        
        geocode_result = geocode_location(location_data["final_answer"])
        lat, lon = geocode_result[0], geocode_result[1]
        
        st.session_state.strike_location = {'lat': lat, 'lon': lon}
        st.write(f"**Approximate location:** `{lat}`, `{lon}`")
        progress_bar.progress(66)
        
        if get_fires_data:
            fires_df = fetch_fires(lat, lon)
            if fires_df is not None and not fires_df.empty:
                st.session_state.fires_df = fires_df
            else:
                st.warning("No fires data found in the area.", icon="⚠️")
                st.session_state.fires_df = None
        else:
            st.session_state.fires_df = None
        
        progress_bar.progress(100)
        
    except Exception as e:
        st.error(f"An error occurred: {e}", icon="❌")
        progress_bar.progress(0)


def create_map_layers(strike_location, fires_df):
    layers = []
    
    strike_df = pd.DataFrame({"lat": [strike_location['lat']], "lon": [strike_location['lon']]})
    layers.append(pdk.Layer(
        'ScatterplotLayer',
        data=strike_df,
        get_position='[lon, lat]',
        get_color='[0, 0, 255, 40]',
        get_radius=5000,
        pickable=True,
    ))
    
    if fires_df is not None:
        fires_display = fires_df.copy()
        if 'latitude' in fires_display.columns and 'longitude' in fires_display.columns:
            fires_display = fires_display.rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=fires_display,
            get_position='[lon, lat]',
            get_color='[255, 165, 0, 120]',
            get_radius=1500,
            pickable=True,
        ))
    
    return layers


def display_map(strike_location, fires_df):
    if st.session_state.fires_df is not None:
        col1, col2 = st.columns([2, 1])
    else:
        col1 = st.container()
        col2 = None
    
    with col1:
        layers = create_map_layers(strike_location, fires_df)
        view_state = pdk.ViewState(
            latitude=strike_location['lat'],
            longitude=strike_location['lon'],
            zoom=8,
            pitch=0
        )
        
        st.pydeck_chart(pdk.Deck(
            map_style=None,
            initial_view_state=view_state,
            layers=layers,
            tooltip={"text": "Location: {lat}, {lon}"}
        ))
    
    if col2 is not None and fires_df is not None:
        with col2:
            st.dataframe(fires_df, use_container_width=True, height=400)
            st.download_button(
                label="Download fires data",
                data=fires_df.to_csv(index=False).encode('utf-8'),
                file_name="fires_data.csv",
                mime="text/csv"
            )


st.subheader("Extract Location from Telegram Post")
st.caption("See GitHub repo for further details.")

tg_post_addr = st.text_input("Enter Telegram post URL:", help="Syntax: t.me/username/post_id")
get_fires = st.checkbox("Get FIRMS fires data", value=False)

if st.button("Extract Location"):
    process_telegram_post(tg_post_addr, get_fires)

if st.session_state.strike_location is not None:
    display_map(st.session_state.strike_location, st.session_state.fires_df)