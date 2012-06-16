from heapq import heappush, heappop
import math
import time
import random

class Node:
    def __init__(self, pos, cost, parent):
        self.pos = pos
        self.cost = cost
        self.parent = parent
    

def estimate(pos, dest):
    xd = dest[0]-pos[0]
    yd = dest[1]-pos[1]
    # Euclidian Distance
    #d = math.sqrt(xd * xd + yd * yd)
    # Manhattan distance
    d = abs(xd) + abs(yd)
    # Chebyshev distance
    # d = max(abs(xd), abs(yd))
    return(d)


def pathFind(level, start, dest): 
    closed_nodes_map = {}
    open_nodes_map = {}

    # create the start node and push into list of open nodes
    n0 = Node(start, 0+estimate(start,dest), None)  
    open_nodes_map[start] = n0
    
    for adj_node in level.nav_graph[start]:
        n1 = Node(adj_node, n0.cost+10+estimate(adj_node,dest), n0)
        open_nodes_map[adj_node] = n1
    closed_nodes_map[start] = n0
    open_nodes_map.pop(start)

    while len(open_nodes_map) > 0:
        # find lowest cost in open list
        low = 99999
        for i in open_nodes_map.itervalues():
            if i.cost < low:
                low = i.cost
                next_node = i
        #print 'Next node', next_node.pos
        
        open_nodes_map.pop(next_node.pos)
        closed_nodes_map[next_node.pos] = next_node
        
        if next_node.pos == dest:
            path = []
            path.append(next_node.pos)
            parent_node = next_node.parent
            while parent_node.pos != start:
                path.append(parent_node.pos)
                parent_node = closed_nodes_map[parent_node.pos].parent
            path.reverse()
            return path
        
        for adj_node in level.nav_graph[next_node.pos]:
            if not closed_nodes_map.has_key(adj_node):
                if open_nodes_map.has_key(adj_node):
                    if open_nodes_map[adj_node].cost > next_node.cost+10+estimate(adj_node,dest):
                        open_nodes_map[adj_node].cost = next_node.cost+10+estimate(adj_node,dest)
                        open_nodes_map[adj_node].parent = next_node
                else:
                    n1 = Node(adj_node, next_node.cost+10+estimate(adj_node,dest), next_node)
                    open_nodes_map[adj_node] = n1

