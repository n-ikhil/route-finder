from math import dist
from threading import Thread
import matplotlib
from matplotlib import pyplot
from networkx.algorithms.shortest_paths.dense import floyd_warshall
from .models import *
import pandas as pd
import geopandas as gpd
import plotly_express as px
import networkx as nx
import osmnx as ox
from .perms import *
import time
matplotlib.use('Agg')
ox.config(use_cache=True, log_console=True)


class SampleNode:
    def __init__(self, data):
        self.id = data["id"]
        self.issrc = data["issrc"]
        self.userid = data["userid"]


def create_graph(city, dist, transport_mode):
    # G = ox.graph_from_address(city, dist=dist, network_type=transport_mode)
    G = ox.graph_from_point(city, dist=dist, network_type=transport_mode)
    return G


def get_max_profit(dists, busLists, fixedPrice):
    groups = []
    dists = sorted(dists, key=lambda var: var[0], reverse=True)
    busLists = sorted(busLists, key=lambda var: var.fuelefficiency)
    cdist = 0
    bdist = 0
    profit = 0
    i = 0
    for di in dists:
        cur_profit = fixedPrice*di[1] - busLists[i].fuelefficiency*di[0]
        if(cur_profit > 0):
            cdist += di[0]
            bdist += di[1]
            profit += cur_profit
            groups.append(di[2])
            i += 1
            if(i >= len(busLists)):
                break
    return profit, groups, {"cdist": cdist, "bdist": bdist, "profit": profit}


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


def modified_floyd(G, inodes):
    dists = {}
    for i in range(len(inodes)):
        dists[inodes[i].id] = {}
    for i in range(len(inodes)):
        for j in range(i+1, len(inodes)):
            curDist = nx.shortest_path_length(
                G, inodes[i].id, inodes[j].id, weight="travel_time")
            dists[inodes[i].id][inodes[j].id] = curDist
            dists[inodes[j].id][inodes[i].id] = curDist
    return dists  # this return floyd-warshall distance pairs


def get_source_node(G, snodes):
    ans = None
    temp = None
    for node in snodes:
        cur = (G.nodes[node.id]["x"], G.nodes[node.id]["y"])
        if(not temp or (temp[1] > cur[1]) or (temp[0] > cur[0] and temp[1] == cur[1])):
            temp = cur
            ans = node
    return ans


def create_greedy_ordering(G, inodes, dists, src):
    discovered_src_uid = set()
    completed = set()
    route = []
    for node in inodes:
        if src.id == node.id and node.issrc:
            discovered_src_uid.add(node.userid)
    route.append(src.id)
    cur_node = src
    # while completed.size()!=inodes.size()/2:
    while len(completed) != len(inodes)/2:
        if cur_node == None:
            break
        next_node = None
        # for adj in dists[cur_node]:
        for onedes in inodes:
            if(onedes.id == cur_node.id):
                continue
            valid = False
            # temp_node = dists[adj]
            # for node in inodes:
            # if node.id == onedes.id:
            # if ((node.userid in discovered_src_uid) or node.issrc):
            #     valid = True
            #     break
            # print(discovered_src_uid, onedes.userid, onedes.issrc, route)
            if ((onedes.userid in discovered_src_uid) or (onedes.issrc and onedes.userid not in completed)):
                # if valid:
                # print("val", onedes.id, onedes.userid)
                if((not next_node) or (dists[cur_node.id][next_node.id] > dists[cur_node.id][onedes.id])):
                    next_node = onedes
        if not next_node:
            # print(route)
            break
        route.append(next_node.id)
        for node in inodes:
            if node.id == next_node.id:
                if node.userid in discovered_src_uid:
                    completed.add(node.userid)
                    discovered_src_uid.remove(node.userid)
                if node.issrc and (node.userid not in completed):
                    discovered_src_uid.add(node.userid)

        cur_node = next_node
    # print(route)
    sdist = sequence_distance(G, route)
    return sdist, route


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
    G = create_graph(city, 2000, "drive")
    for booking in bookingList:
        assign_osxid(G, booking)
    inodes = []
    for pairs in bookingList:
        temp = [pairs.osxsid, pairs.osxdid, pairs.user.id, pairs.etime,
                nx.shortest_path_length(G, pairs.osxsid, pairs.osxdid)]
        inodes.append(temp)
    if(len(busList) == 0):
        return erFlag
    final_ans = {"max_profit": 0, "groups": [], "report": ""}
    stTime = time.time()
    for k in range(1, len(busList)+2):
        # +2 because to accomodate for none groups as well
        skp = sorted_k_partitions(inodes, k)
        for groups in skp:
            temp_dist = []
            cur_profit = 0
            print(k, groups)
            brute = True
            for test in groups:
                valid = False
                if brute:
                    a, b, valid = create_perm(G, test)
                else:
                    snodes = []
                    for nodes in test:
                        snodes.append(SampleNode(
                            {"id": nodes[0], "issrc": True, "userid": nodes[2]}))
                        snodes.append(SampleNode(
                            {"id": nodes[1], "issrc": False, "userid": nodes[2]}))
                    # print(snodes)
                    dists = modified_floyd(G, snodes)
                    # print(dists)
                    src = get_source_node(G, snodes)
                    a, b = create_greedy_ordering(
                        G, snodes, dists, src)
                    # return 0
                    valid = True
                if valid:
                    temp = 0
                    for pair in test:
                        temp += pair[4]
                    temp_dist.append([a, temp, b])
            cur_profit, grps, report = get_max_profit(
                temp_dist, busList, fixedPrice)
            if cur_profit > final_ans["max_profit"]:
                final_ans["max_profit"] = cur_profit
                final_ans["groups"] = grps
                final_ans["report"] = report
    # print(final_ans, "test")
    print("##########################")
    print(final_ans["report"], "time taken: ", time.time()-stTime)
    print("##########################")

    froutes, fcolours = colour_routes(G, final_ans["groups"])
    try:
        fig, ax = ox.plot_graph_routes(G, froutes, fcolours)
        fig.savefig('./booking/static/test.png')
        return final_ans["max_profit"]
    except:
        print("error printing")
        pass
    # print(final_ans["max_profit"])
