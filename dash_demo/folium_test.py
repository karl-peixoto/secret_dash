import streamlit as st
import folium
from streamlit_folium import folium_static

# Create a simple map
mymap = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

# Display the map in Streamlit
st.title("Folium Map Test")
st.title('fasf')
folium_static(mymap)