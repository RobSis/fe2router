# Licensed under the terms of the GPL v3. See LICENCE for details

import math
from itertools import product

from galaxy import StarSystem
from milkyway import SolX, SolY


class AStar(object):
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, node, start, end):
        raise NotImplementedError

    def search(self, start, end):
        openset = set()
        closedset = set()
        current = start
        openset.add(current)
        while openset:
            current = min(openset, key=lambda o: o.h)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            openset.remove(current)
            closedset.add(current)
            for node in self.graph[current]:
                if node in closedset:
                    continue
                if node not in openset:
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None


class AStarNode(StarSystem):
    def __init__(self, star, x, y, z):
        self.ax, self.ay, self.az = x, y, z
        self.h = 0
        self.parent = None

        super(AStarNode, self).__init__(star)


class AStarSpace(AStar):
    def heuristic(self, node, start, end):
        return math.sqrt(
                (end.ax - node.ax) ** 2 + (end.ay - node.ay) ** 2 +
                (end.az - node.az) ** 2 + (end.az - node.az) ** 2) / 16.0


def select_sectors((x0, y0), (x1, y1)):
    # select sectors (Bresenham's algorithm)
    # TODO: thickness of line should be dependend on jumpRange...

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1
    if (x0 >= x1):
        sx = -sx

    sy = 1
    if (y0 >= y1):
        sy = -sy

    sectors = set()

    err = dx - dy
    loop = True
    while (loop):
        sectors.add((x0, y0))

        if (x0 == x1) and (y0 == y1):
            loop = False

        e2 = 2 * err
        if (e2 > -dy):
            err = err - dy
            x0 = x0 + sx
        if (e2 < dx):
            err = err + dx
            y0 = y0 + sy

    return sectors


# create adjacency list
def make_graph(g, start, end, jumpRange):
    sectors = select_sectors((start.coordx, start.coordy),
                             (end.coordx, end.coordy))

    graph = {}
    nodes = []

    startNode = None
    endNode = None

    for coordx, coordy in sectors:
        sector = g.getSector(coordx, coordy)
        for star in sector.stars:
            fx = (start.coordx - sector.coordx) * 128
            fy = (start.coordy - sector.coordy) * 128

            t = AStarNode(star, star.x - fx, star.y - fy, star.z)

            if (star.uid() == start.uid()):
                startNode = t
            if (star.uid() == end.uid()):
                endNode = t

            nodes.append(t)

    for n in nodes:
        dist = lambda s: math.sqrt((n.ax - s.ax) ** 2 +
                                   (n.ay - s.ay) ** 2 +
                                   (n.az - s.az) ** 2) / 16.0 <= jumpRange
        graph[n] = filter(dist, nodes)

    return graph, nodes, startNode, endNode


def find_path(g, start, end, jumpRange):
    graph, nodes, start, end = make_graph(g, start, end, jumpRange)
    paths = AStarSpace(graph)
    return paths.search(start, end)


def find_star(g, address):
    name, coords = address.split(':')
    cx, cy = coords.split(',')

    for s in g.getSector(SolX + int(cx), SolY + int(cy)).stars:
        if (s.name.lower() == name.lower()):
            return s

    return None
