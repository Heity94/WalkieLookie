#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import osmnx as ox
#ox.config(log_console=True, use_cache=True)
ox.settings.log_console = True
import os

# Data path
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "WalkieLookie", "data")
graph_path = os.path.join(data_path,"graph_berlin.obj")

# check if graph data has been downloaded before
if os.path.exists(graph_path):
    print(f"File is already stored under {data_path}")

else:
    # location where you want to find your route
    place = 'Berlin, Germany'
    # find shortest route based on the mode of travel
    mode = 'walk'       # 'drive', 'bike', 'walk'

    # create graph from OSM within the boundaries of some geocodable place(s) and save as pickle file
    graph = ox.graph_from_place(place, network_type = mode)
    with open(graph_path, 'wb') as fp:
        pickle.dump(graph, fp)
        print(f"File was successfully stored under {data_path}")
