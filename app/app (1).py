from datetime import datetime
from gettext import install
import pandas as pd
import numpy as np
import streamlit as st
import requests
import json
import sys
#sys.path.insert(0, "/Users/sofiakramarova/Desktop/WalkieLookie-main/WalkieLookie") #here you have to change the path to the folder where the routing.py file is located on your machine
from routing import add_start_end_node, inital_nodes_to_consider, create_walking_route, evaluate_iterrate_route
import pickle
import os
from ast import literal_eval
import folium
from streamlit_folium import st_folium, folium_static
import osmnx as ox
import streamlit.components.v1 as components
from streamlit_metrics import metric, metric_row
from PIL import Image


st.set_page_config(layout="wide")
image = Image.open('/Users/sofiakramarova/Desktop/Logo.png')


st.title(" WalkieLookie Map",st.image(image, caption='Enter any caption here') )

'''### Please input your desired destination, time availability and type of a walk'''


#cola, colb = st.columns(2)
col3, col1, col2, col4 = st.columns((1,1,1,1))
user_time = col2.number_input('Time', 15)
start_address = col3.text_input('Starting address', value = "Arndtstraße 23, 10965 Berlin")
round_trip = col3.checkbox('Roundtrip', value = True)
destination_address = col1.text_input('Destination address', value = "To be developed")
type_walk = col4.text_input('Walk type', value = "To be developed")

col4.button('Plan the trip')

col1.text("")
col1.text("")
#col1.text("")
col2.text("")
col2.text("")

#dirname = os.path.dirname(os.path.abspath(__file__))  # directory where current file is located
#filename_places = "/Users/sofiakramarova/Desktop/WalkieLookie-main/WalkieLookie/data/bln_xberg_parks_park_nodes_wo_NaN.csv"
#filename_street_graph =  "/Users/sofiakramarova/Desktop/WalkieLookie-main/WalkieLookie/data/graph_berlin.obj"
data_path = "/Users/sofiakramarova/Desktop/WalkieLookie-main/WalkieLookie/Data 2/"

#Load DataFrame with nodes of interest (NOI)
places_noi = pd.read_csv(data_path+"parks_bln_complete_clean.csv", index_col=0, converters={'col1': literal_eval})

#load street data from berlin
with open(data_path+'graph_berlin.obj', 'rb') as fp:
  street_graph = pickle.load(fp)

# Load data
#places_noi = pd.read_csv(filename_places, index_col=0)
#places_noi["nodes_within_park"] = places_noi.nodes_within_park.apply(
    #lambda x: literal_eval(x)
  # Change type to list

# load street data from berlin
#with open(filename_street_graph, "rb") as fp:
    #street_graph = pickle.load(fp)

# User inputs
user_time = 60  # in minutes
start_address = "Arndtstraße 23, 10965 Berlin"  # address as a string
round_trip = True  # wheter you want to return to the start
avg_speed = 5  # in km/h
time_margin = 10  # in minutes -> the end route should be within a time range +- 10 minutes from what the user defined
optimizer = "time"  # optimizer for the shortest path algorithm

# call all functions
#places_noi, nodes_to_visit = get_noi(street_graph, places_noi)
nodes_to_visit_final, places_df_small, subgraph = add_start_end_node(start_address, street_graph, places_noi, user_time)
notes_to_visit_small, notes_to_visit_sorted, x, start_node = inital_nodes_to_consider(user_time, nodes_to_visit_final, subgraph, optimizer=optimizer, avg_speed=avg_speed)
final_path_flat, length_m, travel_time_min = create_walking_route(subgraph,  start_node, notes_to_visit_small, round_trip, avg_speed)
final_path_flat, length_m, travel_time_min, visited_nodes = evaluate_iterrate_route(final_path_flat, length_m, travel_time_min, notes_to_visit_sorted, x, start_node, user_time, subgraph, round_trip, time_margin, avg_speed)



#Plot final route
route_plot =ox.plot_route_folium(street_graph, final_path_flat)

# Add marker for start location
start_loc = final_path_flat[0]
latlng_start = (street_graph.nodes()[start_loc]["y"], street_graph.nodes()[start_loc]["x"])
marker = folium.Marker(
            location = latlng_start,
            icon = folium.Icon(color='red', icon="home"))

marker.add_to(route_plot)

# Add markers for nodes along the route
for i, park in enumerate(visited_nodes):
  latlng_parks = (street_graph.nodes()[park]["y"], street_graph.nodes()[park]["x"])
  marker = folium.Marker(
              location = latlng_parks,
              icon = folium.Icon(color='green', prefix='fa', icon="tree"))

  marker.add_to(route_plot)

components.html(route_plot.get_root().render(), height=500)

#route_plot #show plot


#st_folium(route_plot, width = 725)

#st_data = folium_static(route_plot)



#st.write("Metrices")
metric_row(
    { 
        "Travel Distance (meters)": length_m ,
        "Time travelled (minutes)": travel_time_min, 
      
    }
)

image = Image.open('/Users/sofiakramarova/Desktop/Logo.png')

st.image(image, caption='Enter any caption here')
