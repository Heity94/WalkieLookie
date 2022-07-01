# Imports
import pickle
import os
#import folium
import pandas as pd
import numpy as np
import osmnx as ox
import networkx as nx
ox.config(log_console=True, use_cache=True)
from geopy.geocoders import Nominatim
import sklearn
from ast import literal_eval


# Function to calculate center node (if possible), otherwise return "No center found"
def center_nodes(street_graph, places_nodes_on_map):
    '''Calculate center node of each place of interest, if no center found return string'''
    try:
        return nx.center(street_graph.subgraph(places_nodes_on_map))[
            0]  #take first center node (in case there are more than 1)
    except:
        return "No center found"


def get_noi(street_graph, places_noi):
    '''Based on the graph data and the places of interest dataframe, check which nodes are also in the street data and calculate the center node.
  Return the dataframe + center nodes as well as a list of nodes to visit (center node per park)
  '''

    street_nodes = set(street_graph.nodes())

    # Create column whihc only includes nodes which are also within the berlin graph dats (streets)
    places_noi["park_nodes_within_graph"] = places_noi.nodes_within_park.apply(
        lambda x: [node for node in x if node in street_graph])

    places_noi = places_noi[places_noi.park_nodes_within_graph.apply(
        lambda x: len(x)) > 0].copy()  #Filter out empty parks

    # Get center node for each park
    places_noi["center_node"] = places_noi.park_nodes_within_graph.apply(
        lambda x: center_nodes(street_graph, x))

    # filter out parks without center (for now)
    places_noi = places_noi[places_noi.center_node != "No center found"].copy()

    # Select center park nodes and store as list for route planning
    nodes_to_visit = places_noi.loc[:, "center_node"].to_list()

    return places_noi, nodes_to_visit


def add_start_end_node(start_address,
                       street_graph,
                       nodes_to_visit,
                       end_address=None):
    '''Add start (and end address) to list of nodes which should be visited'''

    locator = Nominatim(user_agent="myapp")

    # stores the start and end points as geopy.point.Point objects
    start_latlng = locator.geocode(start_address).point
    #end_latlng = locator.geocode(end_location).point

    # Find nearest node on the street graph
    orig_node = ox.distance.nearest_nodes(street_graph, start_latlng[1],
                                          start_latlng[0])  #graph, long, lat

    nodes_to_visit = [orig_node
                      ] + nodes_to_visit  #add start node tto list to visit

    return nodes_to_visit


def get_route_stats(calc_route, street_graph, avg_speed=5):
    '''Calculate total length and travel time of calculated route'''

    # Sum up travel time and distance
    cols = ['osmid', 'length']  #, 'travel_time']
    attrs = ox.utils_graph.get_route_edge_attributes(street_graph, calc_route)
    df_route = pd.DataFrame(attrs)[cols]

    length_m = df_route.length.sum().round().astype("int")
    travel_time_min = round((df_route.length.sum() / (avg_speed * 1000)) * 60)

    return length_m, travel_time_min


def inital_nodes_to_consider(user_time,
                             nodes_to_visit_final,
                             street_graph,
                             optimizer="time",
                             avg_speed=5):
    '''
    Create first version of nodes the algorithm should consider in the route planning given the users time.
    For the inital route it will consider 1 node of interest for each 5 minutes the user has
    The first point a user visits after the start is the node closest to him/her
    '''

    # given on time: take the starting address and x number of nodes from list
    x = int(user_time / 5)  #one place of interest for each 5 minutes
    if x > len(
            nodes_to_visit_final[1:]
    ):  # if number of theoretical nodes to visit is higher than the points of interest in the list take lenght of list
        x = len(nodes_to_visit_final[1:])

    start_node = nodes_to_visit_final[0]  #extract start node

    #notes_to_visit_small = np.random.choice(nodes_to_visit_final[1:], x, replace=False).tolist() #sample

    #instead of random sampling of nodes to visit we calculate the distance from the start address and order the list accordingly and then slice it
    tmp_dict = {}

    for node in nodes_to_visit_final[1:]:

        shortest_route = nx.shortest_path(street_graph,
                                          start_node,
                                          node,
                                          weight=optimizer)

        #Calculate route statistics for each node
        length_m, travel_time_min = get_route_stats(shortest_route,
                                                    street_graph, avg_speed)

        # Add route and stats to tmp_dict
        tmp_dict[node] = {
            "shortest_path": shortest_route,
            "length_m": length_m,
            "travel_time_min": travel_time_min
        }

    # select shortest path and append to final path list
    df_tmp = pd.DataFrame.from_dict(tmp_dict, orient="index").sort_values(
        by=["travel_time_min"], ascending=True)
    notes_to_visit_sorted = df_tmp.index.to_list()

    notes_to_visit_small = notes_to_visit_sorted[:x]

    return notes_to_visit_small, notes_to_visit_sorted, x, start_node


def create_walking_route(street_graph,
                         start_node,
                         notes_to_visit_small,
                         round_trip,
                         avg_speed=5):
    '''
    Create first version of the walking route based on the list created in inital_nodes_to_consider
    The algorithm will always check the distance between the start and all other nodes and then choose the one closest.
    From there it will do the same for the remaining nodes until all nodes have been reached
    In case of a round trip it will also incude the way back home to the end of the route
    '''

    final_path = []  #list to store all the final paths

    iterrations = len(
        notes_to_visit_small)  # number of times we heave to run a for loop

    for i in range(iterrations):

        # from the starting address calculate shortest path to all other nodes and store distance in list
        tmp_dict = {}

        for node in notes_to_visit_small:

            shortest_route = nx.shortest_path(street_graph,
                                              start_node,
                                              node,
                                              weight=optimizer)

            #Calculate route statistics for each node
            length_m, travel_time_min = get_route_stats(shortest_route,
                                                        street_graph,
                                                        avg_speed=5)

            # Add route and stats to tmp_dict
            tmp_dict[node] = {
                "shortest_path": shortest_route,
                "length_m": length_m,
                "travel_time_min": travel_time_min
            }

        # select shortest path and append to final path list
        df_tmp = pd.DataFrame.from_dict(tmp_dict, orient="index")
        node_sh_path_overall = df_tmp.travel_time_min.idxmin()
        shortest_path_overall = df_tmp.loc[node_sh_path_overall,
                                           "shortest_path"]
        final_path.append(
            shortest_path_overall[:-1]
        )  #add all nodes except the last (because the start of next will start at same route)

        start_node = notes_to_visit_small.pop(
            notes_to_visit_small.index(node_sh_path_overall)
        )  #remove new start node from list and set as new start point for next iterration

    #If it is a round trip add one more path from last point to start address to list
    if round_trip == True:

        shortest_route = nx.shortest_path(street_graph,
                                          start_node,
                                          nodes_to_visit_final[0],
                                          weight=optimizer)

        final_path.append(shortest_route)

    final_path_flat = [x for xs in final_path for x in xs]

    #Calculate route statistics for each node
    length_m, travel_time_min = get_route_stats(final_path_flat, street_graph)

    return final_path_flat, length_m, travel_time_min


def evaluate_iterrate_route(final_path_flat,
                            length_m,
                            travel_time_min,
                            notes_to_visit_sorted,
                            x,
                            start_node,
                            user_time,
                            street_graph,
                            round_trip,
                            time_margin=10,
                            avg_speed=5):
    '''
    This function will take the  inital walking route calculated in "create_walking_route" and check wheter it fits the users timeframe
    If the route is too short or too long it will add/ remove nodes from the list of nodes and rerun the "create_walking_route" function until it fits the timeframe
    '''

    x_init = None

    #Check if travel time is in between +-10 minutes from user time -> if yes return route
    while not ((travel_time_min <= user_time + time_margin) &
               (travel_time_min >= user_time - time_margin)) | (x_init == x):

        #save inital x
        x_init = x

        #Check if travel time much smaller than the user time -> if yes add more route points
        if (travel_time_min < (user_time + time_margin)):
            x += 1  #(user_time-travel_time_min)/5
        elif (travel_time_min > (user_time + time_margin)):
            x -= 1  #(user_time-travel_time_min)/5

        #update nodes_to_visist
        notes_to_visit_small = notes_to_visit_sorted[:x]
        final_path_flat, length_m, travel_time_min = create_walking_route(
            street_graph,
            start_node,
            notes_to_visit_small,
            round_trip=round_trip,
            avg_speed=5)

    print("Route found")
    return final_path_flat, length_m, travel_time_min, [
        node for node in notes_to_visit_sorted if node in final_path_flat
    ]

if __name__ == "__main__":

    dirname = os.path.dirname(__file__) #directory where current file is located
    filename_places = os.path.join(dirname, 'data', 'bln_xberg_parks_park_nodes_wo_NaN.csv')
    filename_street_graph = os.path.join(dirname, 'data', 'graph_berlin.obj')

    #Load data
    places_noi = pd.read_csv(filename_places, index_col=0)
    places_noi["nodes_within_park"]=places_noi.nodes_within_park.apply(lambda x: literal_eval(x)) #Change type to list

    #load street data from berlin
    with open(filename_street_graph, 'rb') as fp:
        street_graph = pickle.load(fp)


    # User inputs
    user_time = 60 # in minutes
    start_address = "Arndtstraße 23, 10965 Berlin" #address as a string
    round_trip=True # wheter you want to return to the start
    avg_speed =5 # in km/h
    time_margin = 10 # in minutes -> the end route should be within a time range +- 10 minutes from what the user defined
    optimizer = "time" #optimizer for the shortest path algorithm

    # call all functions
    places_noi, nodes_to_visit = get_noi(street_graph, places_noi)
    nodes_to_visit_final = add_start_end_node(start_address, street_graph,
                                            nodes_to_visit)
    notes_to_visit_small, notes_to_visit_sorted, x, start_node = inital_nodes_to_consider(
        user_time,
        nodes_to_visit_final,
        street_graph,
        optimizer=optimizer,
        avg_speed=avg_speed)
    final_path_flat, length_m, travel_time_min = create_walking_route(
        street_graph, start_node, notes_to_visit_small, round_trip, avg_speed)
    final_path_flat, length_m, travel_time_min, visited_nodes = evaluate_iterrate_route(
        final_path_flat, length_m, travel_time_min, notes_to_visit_sorted, x,
        start_node, user_time, street_graph, round_trip, time_margin, avg_speed)

    # Print result of final route
    print("Route length:", length_m)
    print("Estimated Travel time:", travel_time_min)
    print("Defined Timeframe from user:", user_time)
