from threading import Thread
import matplotlib
from matplotlib import pyplot
from .models import *
import pandas as pd
import geopandas as gpd
import plotly_express as px
import networkx as nx
import osmnx as ox
from .perms import *
matplotlib.use('Agg')
ox.config(use_cache=True, log_console=True)


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


def create_graph(city, dist, transport_mode):
    # G = ox.graph_from_address(city, dist=dist, network_type=transport_mode)
    G = ox.graph_from_point(city, dist=dist, network_type=transport_mode)

    return G


def get_max_profit(dists, busLists, fixedPrice):
    groups = []
    dists = sorted(dists, key=lambda var: var[0], reverse=True)
    busLists = sorted(busLists, key=lambda var: var.fuelefficiency)
    profit = 0
    i = 0
    for di in dists:

        cur_profit = fixedPrice*di[1] - busLists[i].fuelefficiency*di[0]
        if(cur_profit > 0):
            profit += cur_profit
            groups.append(di[2])
            i += 1
            if(i >= len(busLists)):
                break
    return profit, groups


def colour_routes(G, routes):
    colours = ['r', 'g', 'b', 'y', 'c']
    cindex = 0
    froutes = []
    fcolours = []
    for grp in routes:
        for i in range(0, len(grp)-1):
            temp = ox.shortest_path(G, grp[i], grp[i+1])
            froutes.append(temp)
            fcolours.append(colours[cindex % len(colours)])
        cindex += 1
    return froutes, fcolours


def assign_osxid(G, booking):
    booking.osxsid = ox.get_nearest_node(
        G, (float(booking.src_lat), float(booking.src_long)))
    booking.osxdid = ox.get_nearest_node(
        G, (float(booking.dst_lat), float(booking.dst_long)))


# @start_new_thread
def create_route(city, busList, bookingList, fixedPrice=1):
    erFlag = 0
    try:
        sumx = 0
        sumy = 0
        for book in bookingList:
            sumx += float(book.src_lat)
            sumy += float(book.src_long)
        sumx = sumx/len(bookingList)
        sumy = sumy/len(bookingList)
        city = (float(sumx), float(sumy))
    except:
        print("internal errororor")
        return erFlag
    # city centre is taken as average of of lat,long pairs
    # print(city)
    G = create_graph(city, 5000, "drive")
    for booking in bookingList:
        assign_osxid(G, booking)
    inodes = []
    for pairs in bookingList:
        temp = [pairs.osxsid, pairs.osxdid, pairs.user.id, pairs.etime,
                nx.shortest_path_length(G, pairs.osxsid, pairs.osxdid)]
        inodes.append(temp)
    if(len(busList) == 0):
        return erFlag
    final_ans = {"max_profit": 0, "groups": []}
    for k in range(1, len(busList)+2):
        # +2 because to accomodate for none groups as well
        skp = sorted_k_partitions(inodes, k)
        for groups in skp:
            temp_dist = []
            cur_profit = 0
            print(k, groups)
            for test in groups:
                a, b, valid = create_perm(G, test)
                if valid:
                    temp = 0
                    for pair in test:
                        temp += pair[4]
                    temp_dist.append([a, temp, b])
            cur_profit, grps = get_max_profit(temp_dist, busList, fixedPrice)
            if cur_profit > final_ans["max_profit"]:
                final_ans["max_profit"] = cur_profit
                final_ans["groups"] = grps
    print(final_ans, "test")
    froutes, fcolours = colour_routes(G, final_ans["groups"])
    try:
        fig, ax = ox.plot_graph_routes(G, froutes, fcolours)
        fig.savefig('./booking/static/test.png')
        return final_ans["max_profit"]
    except:
        print("error printing")
        pass
    print(final_ans["max_profit"])
