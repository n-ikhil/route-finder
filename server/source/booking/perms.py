import sys
import networkx as nx
def validate(seq, RPairs):
    temp = [0]*len(RPairs)
    flag = 0
    for x in seq:
        for y in range(len(RPairs)):
            if x == RPairs[y][0]:
                temp[y] = 1
            elif ((x == RPairs[y][1]) and (temp[y] == 0)):
                flag = 1
    if flag == 0:
        return 0
    return 1

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


def next_permutation(L):
    n = len(L)
    i = n - 2
    while i >= 0 and L[i] >= L[i+1]:
        i -= 1

    if i == -1:
        return False
    j = i + 1
    while j < n and L[j] > L[i]:
        j += 1
    j -= 1
    L[i], L[j] = L[j], L[i]
    left = i + 1
    right = n - 1

    while left < right:
        L[left], L[right] = L[right], L[left]
        left += 1
        right -= 1

    return True


def create_perm(G, RPairs):
    perm = []
    int_nodes = []
    for pair in RPairs:
        int_nodes.append(pair[0])
        int_nodes.append(pair[1])
    L = int_nodes
    L.sort()
    min_dist = sys.maxsize
    count = 0
    min_perm = []
    while True:
        if validate(L, RPairs) == 0:
            temp = sequence_distance(G, L)
            if(temp < min_dist):
                min_dist = temp
                min_perm = L
            #print(L)
            count = count + 1
        if not next_permutation(L):
            break
    return min_dist,min_perm,min_dist!=sys.maxsize

def sorted_k_partitions(seq, k):
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

