import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import plotly_express as px
import networkx as nx
import osmnx as ox
import random
from models import NPair
import sys
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
    for i in range(3):
        src = all[random.randrange(0, len(all))]
        dest = all[random.randrange(0, len(all))]
        if(src != dest):
            Rpairs.append(
                (NPair(src[1], dest[1], "12", "12"), (src[0], dest[0])))
    return Rpairs


def find_route_pair(G, RPairs):
    routes = []
    for pair in RPairs:
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


def validate(seq, RPairs):
    temp = [0]*len(RPairs)
    flag = 0
    for x in seq:
        for y in range(len(RPairs)):
            if x == RPairs[y][1][0]:
                temp[y] = 1
            elif ((x == RPairs[y][1][1]) and (temp[y] == 0)):
                flag = 1
    if flag == 0:
        return 0
    return 1


def next_permutation(L):
    '''
    Permute the list L in-place to generate the next lexicographic permutation.
    Return True if such a permutation exists, else return False.
    '''

    n = len(L)

    # ------------------------------------------------------------

    # Step 1: find rightmost position i such that L[i] < L[i+1]
    i = n - 2
    while i >= 0 and L[i] >= L[i+1]:
        i -= 1

    if i == -1:
        return False

    # ------------------------------------------------------------

    # Step 2: find rightmost position j to the right of i such that L[j] > L[i]
    j = i + 1
    while j < n and L[j] > L[i]:
        j += 1
    j -= 1

    # ------------------------------------------------------------

    # Step 3: swap L[i] and L[j]
    L[i], L[j] = L[j], L[i]

    # ------------------------------------------------------------

    # Step 4: reverse everything to the right of i
    left = i + 1
    right = n - 1

    while left < right:
        L[left], L[right] = L[right], L[left]
        left += 1
        right -= 1

    return True


def sequence_distance(G, seq):
    res = 0
    for i in range(len(seq)-1):
        try:
            res = res + \
                nx.shortest_path_length(
                    G, seq[i], seq[i+1], weight='travel_time')
        except:
            return sys.maxsize
    return res


def create_perm(G, RPairs):
    perm = []
    int_nodes = []
    for pair in RPairs:
        int_nodes.append(pair[1][0])
        int_nodes.append(pair[1][1])
    L = int_nodes
    L.sort()
    min_dist = sys.maxsize
    count = 0
    while True:
        if validate(L, RPairs) == 0:
            temp = sequence_distance(G, L)
            if(temp < min_dist):
                min_dist = temp
            print(L)
            count = count + 1
        if not next_permutation(L):
            break
    print(min_dist)
    print(count)
    print(sys.maxsize)


def sorted_k_partitions(seq, k):
    """Returns a list of all unique k-partitions of `seq`.

    Each partition is a list of parts, and each part is a tuple.

    The parts in each individual partition will be sorted in shortlex
    order (i.e., by length first, then lexicographically).

    The overall list of partitions will then be sorted by the length
    of their first part, the length of their second part, ...,
    the length of their last part, and then lexicographically.
    """
    n = len(seq)
    groups = []  # a list of lists, currently empty

    def generate_partitions(i):
        if i >= n:
            yield list(map(tuple, groups))
        else:
            if n - i > k - len(groups):
                for group in groups:
                    group.append(seq[i])
                    yield from generate_partitions(i + 1)
                    group.pop()

            if len(groups) < k:
                groups.append([seq[i]])
                yield from generate_partitions(i + 1)
                groups.pop()

    result = generate_partitions(0)

    # Sort the parts in each partition in shortlex order
    result = [sorted(ps, key=lambda p: (len(p), p)) for ps in result]
    # Sort partitions by the length of each part, then lexicographically.
    result = sorted(result, key=lambda ps: (*map(len, ps), ps))

    return result


# G = create_graph(location, 1000, "drive")
G = load_graph()
RPairs = loadSample(G)
inodes = []
for pairs in RPairs:
    temp = []
    temp.append(pairs[1][0])
    temp.append(pairs[1][1])
    inodes.append(temp)

for k in range(1, 3):
    for groups in sorted_k_partitions(inodes, k):
        print(k, groups)
create_perm(G, RPairs)
#routes = find_route_pair(G, RPairs)
# ox.plot_graph_routes(G, routes)       print(k, groups)
