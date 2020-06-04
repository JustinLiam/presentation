#!usr/bin/env python
# encoding:utf-8

'''
__Author__:JustinLiam
Conference:IEEE INFOCOM 2018 - IEEE Conference on Computer Communications
Paper:Coverage in Battery-Free Wireless Sensor Networks
'''
import numpy as np
import copy
import operator
from functools import reduce
from benefitcalculating import *
from math import *
import pandas as pd


def PT(V, u_min):
    delta = 3
    b_f = 3
    b_cap = 5
    nodes_num = np.shape(V)[0]
    PT = [[] for i in range(nodes_num)]
    for i in range(nodes_num):
        node = copy.deepcopy(V[i])
        node_2 = copy.deepcopy(V[i])
        PT[i].append(V[i])
        PT[i][0]['i&l'] = (i, 1)
        b_i_lef = min(b_cap, node['battery'] + u_min - delta)
        node['battery'] = b_i_lef
        PT[i].append(node)
        PT[i][1]['i&l'] = (i, 2)
        b_i_rig = min(b_cap, node_2['battery'] + u_min)
        node_2['battery'] = b_i_rig
        PT[i].append(node_2)
        PT[i][2]['i&l'] = (i, 3)
        if PT[i][1]['battery'] >= b_f:
            node = copy.deepcopy(PT[i][1])
            b_i_lef = min(b_cap, node['battery'] + u_min - delta)
            node['battery'] = b_i_lef
            PT[i].append(node)
            PT[i][3]['i&l'] = (i, 4)
        else:
            PT[i].append('NULL')
        PT[i].append('NULL')
        if PT[i][2]['battery'] >= b_f:
            node = copy.deepcopy(PT[i][2])
            b_i_lef = min(b_cap, node['battery'] + u_min - delta)
            node['battery'] = b_i_lef
            PT[i].append(node)
            PT[i][5]['i&l'] = (i, 6)
        else:
            PT[i].append('NULL')
        PT[i].append('NULL')
    return PT


def M_LCQ(V, S, u_min, j):
    r_c = 10
    PTree = PT(V, u_min)
    # print(PTree)
    WN_tj = [[], []]  # denote the nodes that work in t_j or t_(j+1)#TODO
    Connected = []
    sinks_num = np.shape(S)[0]
    nodes_num = np.shape(V)[0]
    Ne_s = [[] for k in range(sinks_num)]
    for k in range(sinks_num):
        for i in range(nodes_num):
            dist = np.linalg.norm(np.array(S[k]) - np.array(V[i]['centre']))
            if dist <= r_c:
                Ne_s[k].append(V[i])
    Ne_li = reduce(operator.add, Ne_s)
    Ne_set = list(
        dedupe(
            Ne_li,
            key=lambda d: (
                d['centre'],
                d['radius'],
                d['battery'],
                d['i&l'])))
    for i in range(nodes_num):
        con_cur = []
        for k in range(3):
            if (PTree[i][0] in Ne_set) and (PTree[i][2 * k + 1] != 'NULL'):
                con_cur.append(PTree[i][k])
        Connected.append(con_cur)
    # print(Connected)
    Con_set = list(
        dedupe(
            reduce(
                operator.add,
                Connected),
            key=lambda d: (
                d['centre'],
                d['radius'],
                d['battery'],
                d['i&l'])))
    V_ta = [[], []]  # denote t_(j-1) and t_j
    while(Con_set):
        n_range = np.shape(Connected)[0]
        b = []
        for n in range(n_range):
            row_ran = np.shape(Connected[n])[0]
            b_cur = []
            for l in range(row_ran):
                a = int(log(l + 1))
                b_cur.append(LCQBenefit(V_ta[a], Connected[n][0]))
            b.append(b_cur)
        print(b)
        b = pd.DataFrame(b)
        b_index_1, b_index_2 = b.stack().idxmax()
        i = Connected[b_index_1][b_index_2]['i&l'][0]
        l = Connected[b_index_1][b_index_2]['i&l'][1]
        if i == b_index_1:
            print("T1")
        if l == b_index_2:
            print("T2")
        a = int(log(l))
        V_ta[a].append(PTree[i][0])
        print(V_ta)
        i_l = Connected[b_index_1].pop(b_index_2)
        print(i_l)
        if l == 1:
            if i_l not in WN_tj[0]:
                WN_tj[0].append(i_l)
            for t in range(np.shape(Connected[b_index_1])[0]):
                if Connected[i][t]['i&l'][1] == 3:
                    del Connected[i][t]
                    continue
        elif l == 2:
            if i_l not in WN_tj[1]:
                WN_tj[1].append(i_l)
            for t in range(np.shape(Connected[b_index_1])[0]):
                if Connected[i][t]['i&l'][1] == 3:
                    del Connected[i][t]
                    continue
        else:
            if i_l not in WN_tj[1]:
                WN_tj[1].append(i_l)
            if(np.shape(Connected[b_index_1])[0]) == 1:
                del Connected[i][0]
            if(np.shape(Connected[b_index_1])[0]) == 2:
                del Connected[i][0]
                del Connected[i][0]
        # step15
        Ne_il = []
        for ii in range(nodes_num):
            dist = np.linalg.norm(
                np.array(
                    V[ii]['centre']) -
                np.array(
                    i_l['centre']))
            if dist <= r_c:
                Ne_il.append(V[ii])
        Ne_il.remove(V[i])
        Ne_il_set = list(
            dedupe(
                Ne_il,
                key=lambda d: (
                    d['centre'],
                    d['radius'],
                    d['battery'])))
        for ii in range(nodes_num):
            for k in range(3):
                if (PTree[ii][0] in Ne_il_set) and (2**int(log(l)) <= k <= 2**(int(log(l)) + 1)) \
                        and (PTree[i][2 * k + 1] != 'NULL') and (PTree[ii][k] not in Connected[ii])\
                        and (PTree[ii][k] not in WN_tj[0]) and (PTree[ii][k] not in WN_tj[1])\
                        and (PTree[ii][0] not in V_ta[0] and (PTree[ii][0] not in WN_tj[1])):
                    Connected[ii].append(PTree[ii][k])
        Con_set = list(
            dedupe(
                reduce(
                    operator.add,
                    Connected),
                key=lambda d: (
                    d['centre'],
                    d['radius'],
                    d['battery'])))
        print(np.shape(Con_set))
    cov = CoverageQuality(WN_tj)
    return cov


if __name__ == '__main__':
    V = [{'centre': (14, 22), 'radius': 3, 'battery': 5}, {'centre': (22, 20), 'radius': 3, 'battery': 5},
         {'centre': (18, 32), 'radius': 3, 'battery': 5}, {'centre': (24, 33), 'radius': 3, 'battery': 5},
         {'centre': (35, 41), 'radius': 3, 'battery': 5}, {'centre': (21, 26), 'radius': 3, 'battery': 5},
         {'centre': (31, 33), 'radius': 3, 'battery': 5}, {'centre': (27, 40), 'radius': 3, 'battery': 5},
         {'centre': (22, 13), 'radius': 3, 'battery': 5}, {'centre': (21, 38), 'radius': 3, 'battery': 5},
         {'centre': (15, 27), 'radius': 3, 'battery': 5}, {'centre': (2, 17), 'radius': 3, 'battery': 5},
         {'centre': (4, 29), 'radius': 3, 'battery': 5}, {'centre': (43, 10), 'radius': 3, 'battery': 5},
         {'centre': (34, 15), 'radius': 3, 'battery': 5}, {'centre': (8, 21), 'radius': 3, 'battery': 5},
         {'centre': (47, 14), 'radius': 3, 'battery': 5}, {'centre': (39, 47), 'radius': 3, 'battery': 5},
         {'centre': (18, 18), 'radius': 3, 'battery': 5}, {'centre': (8, 46), 'radius': 3, 'battery': 5},
         {'centre': (36, 21), 'radius': 3, 'battery': 5}, {'centre': (32, 9), 'radius': 3, 'battery': 5},
         {'centre': (29, 23), 'radius': 3, 'battery': 5}, {'centre': (26, 47), 'radius': 3, 'battery': 5},
         {'centre': (16, 43), 'radius': 3, 'battery': 5}, {'centre': (46, 48), 'radius': 3, 'battery': 5},
         {'centre': (28, 15), 'radius': 3, 'battery': 5}, {'centre': (31, 44), 'radius': 3, 'battery': 5},
         {'centre': (2, 46), 'radius': 3, 'battery': 5}, {'centre': (40, 37), 'radius': 3, 'battery': 5},
         {'centre': (22, 43), 'radius': 3, 'battery': 5}, {'centre': (1, 23), 'radius': 3, 'battery': 5},
         {'centre': (47, 22), 'radius': 3, 'battery': 5}, {'centre': (5, 38), 'radius': 3, 'battery': 5},
         {'centre': (10, 41), 'radius': 3, 'battery': 5}, {'centre': (5, 11), 'radius': 3, 'battery': 5},
         {'centre': (10, 34), 'radius': 3, 'battery': 5}, {'centre': (36, 29), 'radius': 3, 'battery': 5},
         {'centre': (13, 47), 'radius': 3, 'battery': 5}, {'centre': (20, 48), 'radius': 3, 'battery': 5},
         {'centre': (18, 12), 'radius': 3, 'battery': 5}, {'centre': (48, 30), 'radius': 3, 'battery': 5},
         {'centre': (13, 13), 'radius': 3, 'battery': 5}, {'centre': (9, 29), 'radius': 3, 'battery': 5},
         {'centre': (46, 3), 'radius': 3, 'battery': 5}, {'centre': (30, 30), 'radius': 3, 'battery': 5},
         {'centre': (48, 42), 'radius': 3, 'battery': 5}, {'centre': (9, 17), 'radius': 3, 'battery': 5},
         {'centre': (22, 8), 'radius': 3, 'battery': 5}, {'centre': (2, 42), 'radius': 3, 'battery': 5},
         {'centre': (15, 6), 'radius': 3, 'battery': 5}, {'centre': (41, 25), 'radius': 3, 'battery': 5},
         {'centre': (45, 35), 'radius': 3, 'battery': 5}, {'centre': (26, 22), 'radius': 3, 'battery': 5},
         {'centre': (37, 32), 'radius': 3, 'battery': 5}, {'centre': (44, 20), 'radius': 3, 'battery': 5},
         {'centre': (34, 24), 'radius': 3, 'battery': 5}, {'centre': (30, 49), 'radius': 3, 'battery': 5},
         {'centre': (38, 5), 'radius': 3, 'battery': 5}, {'centre': (36, 15), 'radius': 3, 'battery': 5},
         {'centre': (37, 37), 'radius': 3, 'battery': 5}, {'centre': (12, 39), 'radius': 3, 'battery': 5},
         {'centre': (43, 29), 'radius': 3, 'battery': 5}, {'centre': (26, 3), 'radius': 3, 'battery': 5},
         {'centre': (32, 3), 'radius': 3, 'battery': 5}, {'centre': (7, 9), 'radius': 3, 'battery': 5},
         {'centre': (26, 18), 'radius': 3, 'battery': 5}, {'centre': (31, 21), 'radius': 3, 'battery': 5},
         {'centre': (3, 0), 'radius': 3, 'battery': 5}, {'centre': (20, 5), 'radius': 3, 'battery': 5},
         {'centre': (6, 36), 'radius': 3, 'battery': 5}, {'centre': (40, 1), 'radius': 3, 'battery': 5},
         {'centre': (5, 41), 'radius': 3, 'battery': 5}, {'centre': (21, 0), 'radius': 3, 'battery': 5},
         {'centre': (49, 46), 'radius': 3, 'battery': 5}, {'centre': (14, 49), 'radius': 3, 'battery': 5},
         {'centre': (23, 12), 'radius': 3, 'battery': 5}, {'centre': (37, 23), 'radius': 3, 'battery': 5},
         {'centre': (35, 17), 'radius': 3, 'battery': 5}, {'centre': (36, 2), 'radius': 3, 'battery': 5},
         {'centre': (34, 32), 'radius': 3, 'battery': 5}, {'centre': (31, 1), 'radius': 3, 'battery': 5},
         {'centre': (10, 38), 'radius': 3, 'battery': 5}, {'centre': (25, 26), 'radius': 3, 'battery': 5}, {'centre': (15, 23), 'radius': 3, 'battery': 5},
         {'centre': (21, 15), 'radius': 3, 'battery': 5}, {'centre': (28, 33), 'radius': 3, 'battery': 5},
         {'centre': (20, 33), 'radius': 3, 'battery': 5}, {'centre': (39, 43), 'radius': 3, 'battery': 5},
         {'centre': (27, 39), 'radius': 3, 'battery': 5}, {'centre': (24, 20), 'radius': 3, 'battery': 5},
         {'centre': (32, 42), 'radius': 3, 'battery': 5}, {'centre': (14, 18), 'radius': 3, 'battery': 5},
         {'centre': (2, 23), 'radius': 3, 'battery': 5}, {'centre': (32, 11), 'radius': 3, 'battery': 5},
         {'centre': (47, 11), 'radius': 3, 'battery': 5}, {'centre': (38, 16), 'radius': 3, 'battery': 5},
         {'centre': (2, 31), 'radius': 3, 'battery': 5}, {'centre': (36, 36), 'radius': 3, 'battery': 5},
         {'centre': (22, 38), 'radius': 3, 'battery': 5}, {'centre': (9, 20), 'radius': 3, 'battery': 5},
         {'centre': (12, 28), 'radius': 3, 'battery': 5}, {'centre': (9, 46), 'radius': 3, 'battery': 5},
         {'centre': (46, 17), 'radius': 3, 'battery': 5}, {'centre': (14, 42), 'radius': 3, 'battery': 5},
         {'centre': (3, 40), 'radius': 3, 'battery': 5}, {'centre': (19, 23), 'radius': 3, 'battery': 5},
         {'centre': (19, 45), 'radius': 3, 'battery': 5}, {'centre': (33, 20), 'radius': 3, 'battery': 5},
         {'centre': (22, 10), 'radius': 3, 'battery': 5}, {'centre': (28, 45), 'radius': 3, 'battery': 5},
         {'centre': (38, 8), 'radius': 3, 'battery': 5}, {'centre': (38, 23), 'radius': 3, 'battery': 5},
         {'centre': (33, 48), 'radius': 3, 'battery': 5}, {'centre': (33, 32), 'radius': 3, 'battery': 5},
         {'centre': (47, 45), 'radius': 3, 'battery': 5}, {'centre': (8, 36), 'radius': 3, 'battery': 5},
         {'centre': (14, 48), 'radius': 3, 'battery': 5}, {'centre': (17, 38), 'radius': 3, 'battery': 5},
         {'centre': (31, 25), 'radius': 3, 'battery': 5}, {'centre': (47, 3), 'radius': 3, 'battery': 5},
         {'centre': (47, 27), 'radius': 3, 'battery': 5}, {'centre': (3, 49), 'radius': 3, 'battery': 5},
         {'centre': (45, 8), 'radius': 3, 'battery': 5}, {'centre': (33, 15), 'radius': 3, 'battery': 5},
         {'centre': (43, 49), 'radius': 3, 'battery': 5}, {'centre': (18, 13), 'radius': 3, 'battery': 5},
         {'centre': (7, 11), 'radius': 3, 'battery': 5}, {'centre': (39, 28), 'radius': 3, 'battery': 5},
         {'centre': (28, 18), 'radius': 3, 'battery': 5}, {'centre': (44, 36), 'radius': 3, 'battery': 5},
         {'centre': (6, 31), 'radius': 3, 'battery': 5}, {'centre': (0, 16), 'radius': 3, 'battery': 5},
         {'centre': (37, 48), 'radius': 3, 'battery': 5}, {'centre': (7, 3), 'radius': 3, 'battery': 5},
         {'centre': (0, 11), 'radius': 3, 'battery': 5}, {'centre': (24, 34), 'radius': 3, 'battery': 5},
         {'centre': (11, 39), 'radius': 3, 'battery': 5}, {'centre': (38, 38), 'radius': 3, 'battery': 5},
         {'centre': (2, 43), 'radius': 3, 'battery': 5}, {'centre': (33, 6), 'radius': 3, 'battery': 5},
         {'centre': (42, 23), 'radius': 3, 'battery': 5}, {'centre': (24, 41), 'radius': 3, 'battery': 5},
         {'centre': (19, 7), 'radius': 3, 'battery': 5}, {'centre': (6, 41), 'radius': 3, 'battery': 5},
         {'centre': (24, 13), 'radius': 3, 'battery': 5}, {'centre': (23, 3), 'radius': 3, 'battery': 5},
         {'centre': (39, 3), 'radius': 3, 'battery': 5}, {'centre': (13, 2), 'radius': 3, 'battery': 5},
         {'centre': (29, 31), 'radius': 3, 'battery': 5}, {'centre': (36, 30), 'radius': 3, 'battery': 5},
         {'centre': (48, 49), 'radius': 3, 'battery': 5}, {'centre': (49, 42), 'radius': 3, 'battery': 5},
         {'centre': (29, 21), 'radius': 3, 'battery': 5}, {'centre': (11, 36), 'radius': 3, 'battery': 5},
         {'centre': (29, 1), 'radius': 3, 'battery': 5}, {'centre': (44, 27), 'radius': 3, 'battery': 5},
         {'centre': (35, 3), 'radius': 3, 'battery': 5}, {'centre': (37, 24), 'radius': 3, 'battery': 5},
         {'centre': (6, 37), 'radius': 3, 'battery': 5}, {'centre': (20, 0), 'radius': 3, 'battery': 5},
         {'centre': (44, 0), 'radius': 3, 'battery': 5}, {'centre': (13, 45), 'radius': 3, 'battery': 5},
         {'centre': (0, 24), 'radius': 3, 'battery': 5}, {'centre': (22, 9), 'radius': 3, 'battery': 5},
         {'centre': (23, 0), 'radius': 3, 'battery': 5}, {'centre': (27, 20), 'radius': 3, 'battery': 5},
         {'centre': (32, 22), 'radius': 3, 'battery': 5}, {'centre': (49, 44), 'radius': 3, 'battery': 5},
         {'centre': (9, 38), 'radius': 3, 'battery': 5},
         {'centre': (17, 26), 'radius': 3, 'battery': 5}, {'centre': (17, 16), 'radius': 3, 'battery': 5},
         {'centre': (25, 32), 'radius': 3, 'battery': 5}, {'centre': (25, 38), 'radius': 3, 'battery': 5},
         {'centre': (25, 23), 'radius': 3, 'battery': 5}, {'centre': (19, 35), 'radius': 3, 'battery': 5},
         {'centre': (31, 41), 'radius': 3, 'battery': 5}, {'centre': (32, 34), 'radius': 3, 'battery': 5},
         {'centre': (11, 23), 'radius': 3, 'battery': 5}, {'centre': (37, 39), 'radius': 3, 'battery': 5},
         {'centre': (43, 12), 'radius': 3, 'battery': 5}, {'centre': (34, 14), 'radius': 3, 'battery': 5},
         {'centre': (21, 11), 'radius': 3, 'battery': 5}, {'centre': (22, 28), 'radius': 3, 'battery': 5},
         {'centre': (37, 20), 'radius': 3, 'battery': 5}, {'centre': (24, 18), 'radius': 3, 'battery': 5},
         {'centre': (29, 28), 'radius': 3, 'battery': 5}, {'centre': (5, 16), 'radius': 3, 'battery': 5},
         {'centre': (4, 33), 'radius': 3, 'battery': 5}, {'centre': (43, 42), 'radius': 3, 'battery': 5},
         {'centre': (45, 7), 'radius': 3, 'battery': 5}, {'centre': (12, 43), 'radius': 3, 'battery': 5},
         {'centre': (34, 47), 'radius': 3, 'battery': 5}, {'centre': (18, 44), 'radius': 3, 'battery': 5},
         {'centre': (6, 28), 'radius': 3, 'battery': 5}, {'centre': (4, 44), 'radius': 3, 'battery': 5},
         {'centre': (11, 19), 'radius': 3, 'battery': 5}, {'centre': (1, 24), 'radius': 3, 'battery': 5},
         {'centre': (44, 17), 'radius': 3, 'battery': 5}, {'centre': (27, 48), 'radius': 3, 'battery': 5},
         {'centre': (11, 30), 'radius': 3, 'battery': 5}, {'centre': (31, 20), 'radius': 3, 'battery': 5},
         {'centre': (2, 6), 'radius': 3, 'battery': 5}, {'centre': (38, 33), 'radius': 3, 'battery': 5},
         {'centre': (10, 36), 'radius': 3, 'battery': 5}, {'centre': (30, 8), 'radius': 3, 'battery': 5},
         {'centre': (19, 19), 'radius': 3, 'battery': 5}, {'centre': (23, 42), 'radius': 3, 'battery': 5},
         {'centre': (12, 47), 'radius': 3, 'battery': 5}, {'centre': (36, 43), 'radius': 3, 'battery': 5},
         {'centre': (48, 48), 'radius': 3, 'battery': 5}, {'centre': (1, 37), 'radius': 3, 'battery': 5},
         {'centre': (34, 29), 'radius': 3, 'battery': 5}, {'centre': (46, 22), 'radius': 3, 'battery': 5},
         {'centre': (39, 26), 'radius': 3, 'battery': 5}, {'centre': (8, 9), 'radius': 3, 'battery': 5},
         {'centre': (7, 39), 'radius': 3, 'battery': 5}, {'centre': (7, 49), 'radius': 3, 'battery': 5},
         {'centre': (46, 31), 'radius': 3, 'battery': 5}, {'centre': (24, 12), 'radius': 3, 'battery': 5},
         {'centre': (33, 24), 'radius': 3, 'battery': 5}, {'centre': (0, 12), 'radius': 3, 'battery': 5},
         {'centre': (47, 2), 'radius': 3, 'battery': 5}, {'centre': (17, 8), 'radius': 3, 'battery': 5},
         {'centre': (38, 49), 'radius': 3, 'battery': 5}, {'centre': (16, 48), 'radius': 3, 'battery': 5},
         {'centre': (49, 41), 'radius': 3, 'battery': 5}, {'centre': (24, 6), 'radius': 3, 'battery': 5},
         {'centre': (45, 27), 'radius': 3, 'battery': 5}, {'centre': (34, 3), 'radius': 3, 'battery': 5},
         {'centre': (40, 35), 'radius': 3, 'battery': 5}, {'centre': (12, 26), 'radius': 3, 'battery': 5},
         {'centre': (11, 2), 'radius': 3, 'battery': 5}, {'centre': (19, 3), 'radius': 3, 'battery': 5},
         {'centre': (39, 4), 'radius': 3, 'battery': 5}, {'centre': (28, 2), 'radius': 3, 'battery': 5},
         {'centre': (0, 44), 'radius': 3, 'battery': 5}, {'centre': (21, 41), 'radius': 3, 'battery': 5},
         {'centre': (36, 18), 'radius': 3, 'battery': 5}, {'centre': (32, 45), 'radius': 3, 'battery': 5},
         {'centre': (27, 19), 'radius': 3, 'battery': 5}, {'centre': (26, 40), 'radius': 3, 'battery': 5},
         {'centre': (48, 45), 'radius': 3, 'battery': 5}, {'centre': (5, 0), 'radius': 3, 'battery': 5},
         {'centre': (8, 35), 'radius': 3, 'battery': 5}, {'centre': (10, 39), 'radius': 3, 'battery': 5},
         {'centre': (24, 1), 'radius': 3, 'battery': 5}, {'centre': (31, 22), 'radius': 3, 'battery': 5},
         {'centre': (15, 44), 'radius': 3, 'battery': 5}, {'centre': (0, 23), 'radius': 3, 'battery': 5}
         ]
    for i in range(np.shape(V)[0]):
        V[i]['radius'] = 5
    sinks = [(32, 32), (34, 11), (8, 4), (2, 24), (33, 48), (11, 4), (38, 19),
             (7, 47), (35, 43), (29, 6), (13, 11), (17, 31), (4, 2), (42, 27), (42, 8)]
    cov = M_LCQ(V, sinks, 1, 2)
    print(cov)
