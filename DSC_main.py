#!usr/bin/env python
# encoding:utf-8

'''
__Author__:JustinLiam
Conference:IEEE INFOCOM 2018 - IEEE Conference on Computer Communications
Paper:Coverage in Battery-Free Wireless Sensor Networks
'''


import numpy as np
import operator
from functools import reduce
import copy
from benefitcalculating import *


# monitoring duration: T = { t_1 , t_2 , ... ,t_K }
# energy consumption rata: lambda
# minimum energy recharging rate mu_min
# delta = t * lambda
#R = 50*50
#r_s = [2,5]
#r_c = 10
#Bf = 3
#delta = 3
#mu_min = [0.5,2]



def DisjointSetCycling(D_num,r_c = 10,nodes=[],sinks=[]):
    A = loadDataSet('area.txt')
    D = [[]for i in range(D_num)]
    nodes_num = np.shape(nodes)[0]
    sinks_num = np.shape(sinks)[0]
    Ne_s = [[]for j in range(sinks_num)]
    Ne_v = [[]for i in range(nodes_num)]
    s_bf = []
    #step2
    for j in range(sinks_num):
        for i in range(nodes_num):
            dist = np.linalg.norm(np.array(sinks[j]) - np.array(nodes[i]['centre']))
            if dist <= r_c:
                Ne_s[j].append(nodes[i])
    Ne_li = reduce(operator.add, Ne_s)#转换为一维列表
    Ne_set = list(dedupe(Ne_li,key=lambda d:(d['centre'],d['radius'],d['battery'])))
    for i in range(np.shape(Ne_set)[0]):
        new1 = Ne_set[i]['centre']
        new2 = Ne_set[i]['radius']
        new3 = Ne_set[i]['battery']
        new = {
            'centre':new1,
            'radius':new2,
            'battery':new3
        }
        s_bf.append(new)
    s_bf = list(dedupe(s_bf,key=lambda d:(d['centre'],d['radius'],d['battery'])))

    # step5
    for i in range(nodes_num):
        node_i = copy.deepcopy(nodes[i])
        del nodes[i]
        for node in nodes:
            dist = np.linalg.norm(np.array(node_i['centre']) - np.array(node['centre']))
            if dist <= r_c:
                Ne_v[i].append(node)
        nodes.insert(i, node_i)

    while(s_bf):
        #step6-step10
        s_bf_num = np.shape(s_bf)[0]
        #Ne_bf = [[] * s_bf_num]
        benefit = [[]for i in range(s_bf_num)]
        for i in range(s_bf_num):
            #calculate the Ne-bf
            i_index = nodes.index(s_bf[i])
            #step7-step10
            for j in range(D_num):
                D_cur = copy.deepcopy(D)
                ret = [k for k in Ne_v[i_index] if k in D[j]]
                if((ret) or (s_bf[i] in Ne_set)):
                    D_cur[j].append(s_bf[i])
                    benefit_cur = benefitCalculating(A,D_cur) - benefitCalculating(A,D)
                    benefit[i].append(benefit_cur)
                else:
                    benefit[i].append(-1)
        ben_max_index = np.where(benefit == np.max(benefit))
        ben_max_num = np.shape(ben_max_index)[1]
        l = np.random.randint(ben_max_num)
        i = ben_max_index[0][l]
        j = ben_max_index[1][l]
        D[j].append(s_bf[i])
        D[j] = list(dedupe(D[j], key=lambda d: (d['centre'],d['radius'],d['battery'])))
        max_i_index = nodes.index(s_bf[i])
        del s_bf[i]
        temp = copy.deepcopy(Ne_v[max_i_index])
        for j in range(D_num):
            for node in D[j]:
                if (node in temp):
                    temp.remove(node)
        for j in range(np.shape(temp)[0]):
            new1 = temp[j]['centre']
            new2 = temp[j]['radius']
            new3 = temp[j]['battery']
            new = {
                'centre': new1,
                'radius': new2,
                'battery':new3
            }
            s_bf.append(new)
        s_bf = list(dedupe(s_bf, key=lambda d: (d['centre'],d['radius'],d['battery'])))
        print(np.shape(s_bf))
    for i in range(D_num):
        print(np.shape(D[i]))
        print(D[i])

    return D




if __name__ == '__main__':
    V,sinks = generateNodeData(50,50,250,15)
    D = DisjointSetCycling(3,10,V,sinks)
    drawDisjointSet(D,sinks)
    drawSingleDisjointSet(D)
    Cov = CoverageConstruct(V,1,D)
    print(Cov)
    coverage_quality = CoverageQuality(Cov)
    print(coverage_quality)
