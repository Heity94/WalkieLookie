#from datetime import datetime
import pandas as pd
import numpy as np
import streamlit as st
#import requests
#import json
#import sys
import pickle
import os
from ast import literal_eval
import folium
#from streamlit_folium import st_folium, folium_static
from WalkieLookie.routing import add_start_end_node, inital_nodes_to_consider, create_walking_route, evaluate_iterrate_route
import osmnx as ox
from PIL import Image
import streamlit.components.v1 as components

# Page configs
st.set_page_config(layout="wide")

# Load data
logo = Image.open(os.path.join(os.path.dirname(__file__),"Logo.png"))
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "WalkieLookie", "data")
#data_path = "/Users/sofiakramarova/Desktop/WalkieLookie-main/WalkieLookie/Data 2/"

#Load DataFrame with nodes of interest (NOI)
places_noi = pd.read_csv(data_path+"/parks_bln_complete_clean.csv", index_col=0, converters={'col1': literal_eval})
#load street data from berlin
with open(data_path+'/graph_berlin.obj', 'rb') as fp:
    street_graph = pickle.load(fp)

## Content of the side

# Logo on top of the page
st.image(logo)

# User inputs
with st.form("my_form"):
    col3, col1, col2, col4 = st.columns((1, 1, 1, 1))
    user_time = col2.number_input('Time', value=60,
                                    min_value=15,
                                    step=5,
                                    help="Time in minutes you plan for your walk")
    start_address = col3.text_input('Starting address',
                                    value="Arndtstraße 23, 10965 Berlin",
                                    help="Starting point of your walk, as a valid address in Berlin")
    round_trip = col3.checkbox('Roundtrip', value=True, help="Do you want to end up back at the start")
    destination_address = col1.text_input(
                                    'Destination address',
                                    value="Yet to be developed",
                                    disabled=True,
                                    help="(Yet to be developed!) End point of your walk, as a valid address in Berlin")
    type_walk = col4.text_input('Walk type',
                                value="To be developed",
                                disabled=True,
                                help="(Yet to be developed!) What kind of places do you want to pass by along your route?")

    # General variables (not set by user)
    avg_speed = 5  # in km/h
    time_margin = 10  # in minutes -> the end route should be within a time range +- 10 minutes from what the user defined
    optimizer = "length"  # optimizer for the shortest path algorithm

    submitted= col4.form_submit_button('Plan the trip')


if submitted:
    nodes_to_visit_final, places_df_small, subgraph = add_start_end_node(
        start_address, street_graph, places_noi, user_time)
    notes_to_visit_small, notes_to_visit_sorted, x, start_node = inital_nodes_to_consider(
        user_time,
        nodes_to_visit_final,
        subgraph,
        optimizer=optimizer,
        avg_speed=avg_speed)
    final_path_flat, length_m, travel_time_min = create_walking_route(
        subgraph, start_node, notes_to_visit_small, round_trip, avg_speed)
    final_path_flat, length_m, travel_time_min, visited_nodes = evaluate_iterrate_route(
        final_path_flat, length_m, travel_time_min, notes_to_visit_sorted, x,
        start_node, user_time, subgraph, round_trip, time_margin, avg_speed)

    #Plot final route
    route_plot = ox.plot_route_folium(street_graph, final_path_flat)

    # Add marker for start location
    start_loc = final_path_flat[0]
    latlng_start = (street_graph.nodes()[start_loc]["y"],
                    street_graph.nodes()[start_loc]["x"])
    marker = folium.Marker(location=latlng_start,
                        icon=folium.Icon(color='red', icon="home"))

    marker.add_to(route_plot)

    # Add markers for nodes along the route
    for i, park in enumerate(visited_nodes):
        latlng_parks = (street_graph.nodes()[park]["y"],
                        street_graph.nodes()[park]["x"])
        marker = folium.Marker(location=latlng_parks,
                            icon=folium.Icon(color='green',
                                                prefix='fa',
                                                icon="tree"))

        marker.add_to(route_plot)

    st.text("")
    st.text("")
    colm1, colm2 = st.columns([4, 1])
    with colm1:
        components.html(route_plot.get_root().render(), height=500)

    colm2.metric(label="Route length", value=f"{length_m} m")
    colm2.metric(label="Estimated travel time", value=f"{travel_time_min} min")
