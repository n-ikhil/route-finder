import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
import random
from models import NPair
ox.config(use_cache=True, log_console=True)

location = "Delhi"


def create_graph(loc, dist, transport_mode):
    """Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’"""
    G = ox.graph_from_address(loc, dist=dist, network_type=transport_mode)
    return G


def load_graph():
    G = ox.load_graphml("./data/graph.graphml")
    return G


def loadSample(G):
    Rpairs = []
    all = list(G.nodes(data=True))
    for i in range(2):
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
        # routes.append([pair[1][0]])
    return routes

def check(perm,RPairs):
    result = []
    for comb in perm:
        temp = [0]*len(RPairs)
        flag = 0
        for x in comb:
            for y in range(len(RPairs)):
                if x == RPairs[y][1][0]:
                    temp[y] = 1
                elif ((x == RPairs[y][1][1]) and (temp[y] == 0)):
                    flag = 1
        if flag == 0:
            result.append(comb)
    return result
    


def permutation(lst): 
  
    # If lst is empty then there are no permutations 
    if len(lst) == 0: 
        return [] 
  
    # If there is only one element in lst then, only 
    # one permuatation is possible 
    if len(lst) == 1: 
        return [lst] 
  
    # Find the permutations for lst if there are 
    # more than 1 characters 
  
    l = [] # empty list that will store current permutation 
  
    # Iterate the input(lst) and calculate the permutation 
    for i in range(len(lst)): 
       m = lst[i] 
  
       # Extract lst[i] or m from the list.  remLst is 
       # remaining list 
       remLst = lst[:i] + lst[i+1:] 
  
       # Generating all permutations where m is first 
       # element 
       for p in permutation(remLst):
            l.append([m] + p) 
    return l 






def create_perm(RPairs):
    perm = []
    int_nodes = []
    for pair in RPairs:
        int_nodes.append(pair[1][0])
        int_nodes.append(pair[1][1])
    perm = permutation(int_nodes)
    print(len(perm))
    result = check(perm,RPairs)
    print(len(result))

    return result



# G = create_graph(location, 1000, "drive")
G = load_graph()
RPairs = loadSample(G)
perm = create_perm(RPairs)
#routes = find_route_pair(G, RPairs)
#ox.plot_graph_routes(G, routes)

