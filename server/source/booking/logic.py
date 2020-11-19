from numpy.lib.npyio import save
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
import random
ox.config(use_cache=True, log_console=True)

location = "Delhi"


def create_graph(loc, dist, transport_mode):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    return G


def loadSample(G):
    Rpairs = []
    all = list(G.nodes(data=True))
    for i in range(5):
        src = all[random.randrange(0, len(all))]
        dest = all[random.randrange(0, len(all))]
        if(src != dest):
            Rpairs.append(
                (NPair(src[1], dest[1], "12", "12"), (src[0], dest[0])))
    return Rpairs


def find_route_pair(G, RPairs):
    routes = []
    for pair in RPairs:
        # st_node = ox.get_nearest_node(G, (pair[0].startLocation))
        # end_node = ox.get_nearest_node(G, pair[0].endLocation)
        st_node = pair[1][0]
        end_node = pair[1][1]
        try:
            routes.append(nx.shortest_path(
                G, st_node, end_node, weight='travel_time'))
        except:
            print("no route")
            pass
    return routes


def create_route(city, busList, bookingList):
    G = create_graph(city, 1000, "drive")
    RPairs = loadSample(G)
    routes = find_route_pair(G, RPairs)
    ox.plot_graph_routes(G, routes, save=True)
