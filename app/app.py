#Imports
import folium
import pickle
import os
import streamlit as st
from WalkieLookie import routing
from ast import literal_eval
import pandas as pd

## ---- Streamlit layout -----



## ---- Load data -----
#Filenames to load data
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




## ----- Calculate route ------


## ----- Plot map and route -------
