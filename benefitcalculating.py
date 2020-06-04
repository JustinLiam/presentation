from math import *
import numpy as np
import random
import itertools
import operator
from shapely.geometry import Point
from shapely.geometry import LineString
from matplotlib import pyplot
from shapely.geometry import Polygon
from descartes.patch import PolygonPatch
import pylab as plt
import matplotlib as mpl
import copy


from figures import BLUE, SIZE, set_limits, plot_coords, color_isvalid


def generateData(range1,range2,num):
    node = list(itertools.product(range(range1), range(range2)))
    nodes = random.sample(node, num)
    nodes.extend([(0, 0), (0, range1), (range2, 0), (range1,range2)])
    return nodes

def generateNodeData(range1,range2,nodes_num,sinks_num):
    node = list(itertools.product(range(range1), range(range2)))
    nodes = random.sample(node, nodes_num)
    #radius = np.random.randint(2, 6, size=nodes_num)
    radius = 3
    battery = 5
    sink = list(itertools.product(range(range1), range(range2)))
    sinks = random.sample(sink, sinks_num)
    V = []

    for i in range(nodes_num):
        new1 = nodes[i]
        #new2 = radius[i]
        new2 = radius
        b = {
            'centre': new1,
            'radius': new2,
            'battery':battery
        }
        V.append(b)
    return V,sinks
def loadDataSet(fileName):
    A = [];
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split('\t')
        area = eval(curLine[0])[0]
        new2 = eval(curLine[0])[1]
        new1 = LineString(area)
        a = {
            'area':new1,
            'weight':new2
        }
        A.append(a)
    return A

#
def benefitCalculating(A,D):
    D_num = np.shape(D)[0]
    total_benefit = 0
    for i in range(D_num):
        cur_un = Point((0, 0)).buffer(0)
        for b in D[i]:
            cur_un = cur_un.union(Point(b['centre']).buffer(b['radius']))
        cur_benefit = 0
        for a in A:
            ret = Polygon(a['area']).intersection(cur_un).area
            benefit = ret * a['weight']
            cur_benefit = benefit + cur_benefit
        total_benefit = total_benefit + cur_benefit

    return total_benefit

def LCQBenefit(V_ta,node):
    A = loadDataSet('area.txt')
    V_ta_num = np.shape(V_ta)[0]
    ben_1 = 0; ben_2 =0
    cur_un = Point((0, 0)).buffer(0)
    for b in V_ta:
        cur_un = cur_un.union(Point(b['centre']).buffer(b['radius']))
    cur_un_2 = cur_un.union(Point(node['centre']).buffer(node['radius']))
    cur_ben1 = 0
    cur_ben2 = 0
    for a in A:
        ret1 = Polygon(a['area']).intersection(cur_un).area
        ret2 = Polygon(a['area']).intersection(cur_un_2).area
        benefit1 = ret1 * a['weight']
        benefit2 = ret2 * a['weight']
        cur_ben1 = benefit1 + cur_ben1
        cur_ben2 = benefit2 + cur_ben2
    """ben_1 = ben_1 + cur_ben1
    ben_2 = ben_2 + cur_ben2"""
    return cur_ben2-cur_ben1


def drawNodesLocations(Nodes):
    nodes = np.array(Nodes)
    x1 = list(nodes[:, 0])
    y1 = list(nodes[:, 1])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Locations of BF-WSN nodes')
    ax.scatter(x1, y1, s=20, color='r', marker='o')
    for a, b in zip(x1, y1):
        ax.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)
    plt.savefig('Locations of BF-WSN nodes.jpg')
    plt.legend()
    plt.show()


def drawDisjointSet(D,sinks):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Disjoint Set of BF-WSN nodes')
    col = ['r','g','b','y']
    D_num = np.shape(D)[0]
    sinks_num = np.shape(sinks)[0]
    for i in range(D_num):
        nodes_num = np.shape(D[i])[0]
        for j in range(nodes_num):
            patch = PolygonPatch(Point(D[i][j]['centre']).buffer(D[i][j]['radius']),
                                 fc=col[i], ec=col[i], alpha=0.5, zorder=1)
            ax.add_patch(patch)
    for i in range(sinks_num):
        patch = PolygonPatch(Point(sinks[i]).buffer(10),fc='k', ec='k', alpha=0.2, zorder=1)
        ax.add_patch(patch)
        """x1 = list(nodes[:, 0])
        y1 = list(nodes[:, 1])
        ax.scatter(x1, y1, s=20, color=col[i], marker='o')
        #for a, b in zip(x1, y1):
        #    ax.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)"""
    set_limits(ax, 0, 50, 0, 50)
    plt.savefig('Disjoint Set of BF-WSN nodes.jpg')
    plt.legend()
    plt.show()

def drawSingleDisjointSet(D):
    fig = plt.figure()
    ax1 = fig.add_subplot(131)
    ax1.set_title('Disjoint Set 1')
    col = ['r','g','b','y']
    i = 0
    nodes_num = np.shape(D[i])[0]
    for j in range(nodes_num):
        patch = PolygonPatch(Point(D[i][j]['centre']).buffer(D[i][j]['radius']),
                             fc=col[i], ec=col[i], alpha=0.5, zorder=1)
        ax1.add_patch(patch)
    set_limits(ax1, 0, 50, 0, 50)

    ax2 = fig.add_subplot(132)
    ax2.set_title('Disjoint Set 2')
    col = ['r', 'g', 'b', 'y']
    i = 1
    nodes_num = np.shape(D[i])[0]
    for j in range(nodes_num):
        patch = PolygonPatch(Point(D[i][j]['centre']).buffer(D[i][j]['radius']),
                             fc=col[i], ec=col[i], alpha=0.5, zorder=1)
        ax2.add_patch(patch)
    set_limits(ax2, 0, 50, 0, 50)

    ax3 = fig.add_subplot(133)
    ax3.set_title('Disjoint Set 3')
    col = ['r', 'g', 'b', 'y']
    i = 2
    nodes_num = np.shape(D[i])[0]
    for j in range(nodes_num):
        patch = PolygonPatch(Point(D[i][j]['centre']).buffer(D[i][j]['radius']),
                             fc=col[i], ec=col[i], alpha=0.5, zorder=1)
        ax3.add_patch(patch)
    set_limits(ax3, 0, 50, 0, 50)

    plt.savefig('Disjoint Single Set of BF-WSN nodes.jpg')
    plt.legend()
    plt.show()

def dedupe(items,key=None):
    seen=set()
    for item in items:
        val=item if key is None else key(item)
        if val not in seen:
            yield item
            seen.add(val)

def CoverageConstruct(V,u_min,D,delta = 3,T = 48):
    Cov = []
    D_pre =copy.deepcopy(D)
    r_c = 10
    b_f = 4
    b_cap = 5
    u = [1.0, 1.5]
    D_num = np.shape(D)[0]
    nodes_num = np.shape(V)[0]
    Ne_v = [[] for i in range(nodes_num)]
    for i in range(nodes_num):
        node_i = copy.deepcopy(V[i])
        del V[i]
        for node in V:
            dist = np.linalg.norm(np.array(node_i['centre']) - np.array(node['centre']))
            if dist <= r_c:
                Ne_v[i].append(node)
        V.insert(i, node_i)
    for t in range(T):
        D = copy.deepcopy(D_pre)
        u_t = random.choice(u)
        j = int((t%((delta/u_min)-1)) + 1)
        I = [i for i in V if i not in D[j]]
        for i in I:
            i_index = V.index(i)
            for num in range(D_num):
                if i in D[num]:
                    l = num
            ret = [k for k in Ne_v[i_index] if k in D[j]]
            b_next = min(b_cap,i['battery'] - delta + u_t + abs(l-j-1)*u_min)
            if ret and (i['battery']>=b_f):
                if b_next>=b_f:
                    i['battery'] = b_next#TODO
                    if i not in D[j]:
                        D[j].append(i)
        Cov.append(D[j])
    return Cov

def CoverageQuality(Cov):
    A = loadDataSet('area.txt')
    K = np.shape(Cov)[0]
    cq = 0
    for i in range(K):
        cur_un = Point((0, 0)).buffer(0)
        for b in Cov[i]:
            cur_un = cur_un.union(Point(b['centre']).buffer(b['radius']))
        cur_cq = 0
        for a in A:
            ret = Polygon(a['area']).intersection(cur_un).area
            cur_cq += ret*a['weight']
        cq +=cur_cq
    cq_a = 0
    for a in A:
        ar = Polygon(a['area']).area
        cq_a += ar*a['weight']
    coverage_quality = cq/(cq_a*K)
    print(coverage_quality)
    return coverage_quality