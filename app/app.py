#Imports
import folium
import pickle
import os
import streamlit as st
import sys
sys.path.insert(0, "/Users/philippheitmann/code/Heity94/WalkieLookie/WalkieLookie") #here you have to change the path to the folder where the routing.py file is located on your machine
import routing

#instead of doing the above you can also install WalkieLookie as a package (in your terminal go tho this folder "/Users/philippheitmann/code/Heity94/WalkieLookie/"
# and in the Terminal enter: pip install -e . (ones this is done, you can import Walkielookie as any other package (e.g. pandas))
#from WalkieLookie import routing

from ast import literal_eval
import pandas as pd

## ---- Streamlit layout -----
st.set_page_config(layout="wide")


## ---- Load data -----
# Declare Filenames to load data
dirname = os.path.dirname(os.path.dirname(__file__))  # directory where current file is located
filename_places = os.path.join(dirname, "WalkieLookie", "data", "bln_xberg_parks_park_nodes_wo_NaN.csv")
filename_street_graph = os.path.join(dirname, "data", "graph_berlin.obj")

# Load places of interest df
places_noi = pd.read_csv(filename_places, index_col=0)
places_noi["nodes_within_park"] = places_noi.nodes_within_park.apply(lambda x: literal_eval(x))  # Change type to list

# load street data from berlin
with open(filename_street_graph, "rb") as fp:
    street_graph = pickle.load(fp)


## ---- User input -------
# Variables which have to be set by the user
user_time = st.number_input("Time for your walk (minutes)", min_value=0, value=int, step=5)  # in minutes
start_address = st.text_input("Start address", placeholder="Arndtstraße 23, 10965 Berlin")  # address as a string
round_trip = st.checkbox('Roundtrip', value=True)  # wheter you want to return to the start

# Variables which are predefined and dont have to be set by the user
avg_speed = 5  # in km/h
time_margin = 10  # in minutes -> the end route should be within a time range +- 10 minutes from what the user defined
optimizer = "time"  # optimizer for the shortest path algorithm

# Add a start route calculation button, which triggers the execution of all my functions below

## ----- Calculate route ------
# copy paste the code from routing.py here (from line 288-320)




## ----- Plot map and route -------
# Copy paste the route plotting from my notebook here and try to show it on the website + the route statistics (length and time)
