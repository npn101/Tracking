#Mr. Siwakorn Prasertsingkul
import streamlit as st
import pandas as pd
import numpy as np
import folium as fo
from streamlit_folium import folium_static
import geopandas as gp
import pydeck as pdk
import altair as alt

#Once upon a time I stumbled with this issue.
# If you're using macOS go to Macintosh HD > Applications > Python3.6 folder (or whatever version of python you're using)
# > double click on "Install Certificates.command" file. :D


st.title('Streamlit Homework')

#Heading
"""
## Data tracking (2019/01) please input date
"""



st.markdown(
""" The date available for 1 to 5, if you do not input
    number, it'll show table for 2019/01/01 data as default
""")

df1 = pd.read_csv('https://raw.githubusercontent.com/SiwakornPr/Tracking/master/20190101.csv')
date = st.text_input(label='Date')
if date == '' or '1':
    df = df1
if date == '2':
    df = pd.read_csv('https://raw.githubusercontent.com/SiwakornPr/Tracking/master/20190102.csv')
if date == '3':
    df = pd.read_csv('https://raw.githubusercontent.com/SiwakornPr/Tracking/master/20190103.csv')
if date == '4':
    df = pd.read_csv('https://raw.githubusercontent.com/SiwakornPr/Tracking/master/20190104.csv')
if date =='5':
    df = pd.read_csv('https://raw.githubusercontent.com/SiwakornPr/Tracking/master/20190105.csv')

if st.checkbox("Show raw data", False):
    st.write(df)

crs = "EPSG:4326"
geometry = gp.points_from_xy(df.lonstartl, df.latstartl)
geo_df = gp.GeoDataFrame(df, crs=crs, geometry=geometry)


hour_set = st.slider("Hour to look at (Every 3 hours)", 0, 23, step = 3)
#print(hour_set)
def load_data(start, stop):
    data = geo_df
    data[start] = pd.to_datetime(data[start])
    data[stop] = pd.to_datetime(data[stop])
    return data

time = load_data('timestart', 'timestop')
#print(timeI.timestart[0].year)

st.subheader("Searching ID")

longitude = 100.501800
latitude = 13.756300
station_map = fo.Map(
    location = [latitude, longitude],
    zoom_start = 9)

latitudes1 = list(geo_df.latstartl)
longitudes1 = list(geo_df.lonstartl)
timebegin = list(time.timestart)
timefinish = list(time.timestop)
labels = list(geo_df.ID)
latitudes2 = list(geo_df.latstop)
longitudes2 = list(geo_df.lonstop)

ID_Q = st.text_input(label='ID')
st.markdown(
""" Red as picked up location and Blue as deliveried location
""")

st.markdown(
""" Note: Some point, picked up location and deliveried location
    are the same location then it'll appear only one point.
""") #Such as ID: 900

def ID_Query(latitudes, longitudes, t, color):
    for lat, lng, ID, start in zip(latitudes, longitudes, labels, t):
        if ID_Q == str(ID):
            fo.Marker(
                location = [lat, lng],
                popup = ['ID: ' + str(ID), lat, lng, start],
                icon = fo.Icon(color=color, icon='heart')
            ).add_to(station_map)

ID_Query(latitudes1, longitudes1, timebegin, 'red')
ID_Query(latitudes2, longitudes2, timefinish, 'blue')
folium_static(station_map)
#print(type(geo_df.timestart[0]))

midpoint = (np.average(latitude), np.average(longitude))
data = time[time["timestart"].dt.hour == hour_set]
def geo_3d(lon, lat):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 11,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=[lon, lat],
                radius=500,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ],
    ))
st.subheader("Geo data (Picked up) at %i:00" % (hour_set))
geo_3d('lonstartl', 'latstartl')
st.subheader("Geo data (Deliveried) at %i:00" % (hour_set))
geo_3d('lonstop', 'latstop')


st.subheader("Engagement (picked up) by minute %i:00" % (hour_set))
def chart(time, type):
    filtered = data[
        (data[time].dt.hour >= hour_set) & (data[time].dt.hour < (hour_set + 1))
    ]
    hist = np.histogram(filtered[time].dt.minute, bins=60, range=(0, 60))[0]
    chart_data = pd.DataFrame({"minute": range(60), type: hist})

    st.altair_chart(alt.Chart(chart_data)
        .mark_area(
            interpolate='step-after',
        ).encode(
            x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
            y=alt.Y(type + ":Q"),
            tooltip=['minute', type]
        ), use_container_width=True)
chart('timestart', 'pickups')
st.subheader("Engagement (deliveried) by minute %i:00" % (hour_set))
chart('timestop', 'deliveried')
