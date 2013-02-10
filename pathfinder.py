from galaxy import StarSystem
import math


class AStarNode(object):
    def __init__(self):
        self.g = 0
        self.h = 0
        self.parent = None


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
            current = min(openset, key=lambda o: o.g + o.h)
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
                if node in openset:
                    new_g = current.g
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                else:
                    node.g = current.g
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None


class StarNode(StarSystem):
    def __init__(self, star, x, y, z):
        self.ax, self.ay, self.az = x, y, z
        self.h = 0
        self.g = 0
        self.parent = None

        super(StarNode, self).__init__(star)


class AStarSpace(AStar):
    def heuristic(self, node, start, end):
        return math.sqrt(
                (end.ax - node.ax) ** 2 + (end.ay - node.ay) ** 2 +
                (end.az - node.az) ** 2 + (end.az - node.az) ** 2) / 16.0


def select_sectors((x0, y0), (x1, y1)):
    # select sectors (Bresenham's algorithm)
    # thickness of line should be dependend on jumpRange...

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


#create adjacency list
def make_graph(g, startSector, endSector, jumpRange):
    sectors = select_sectors((startSector.coordx, startSector.coordy),
                             (endSector.coordx, endSector.coordy))

    graph = {}
    nodes = []

    start = None
    end = None

    for coordx, coordy in sectors:
        sector = g.getSector(coordx, coordy)
        for star in sector.stars:
            fx = (startSector.coordx - sector.coordx) * 128
            fy = (startSector.coordy - sector.coordy) * 128

            t = StarNode(star, star.x - fx, star.y - fy, star.z)

            if (star.uid() == startSector.uid()):
                start = t
            if (star.uid() == endSector.uid()):
                end = t

            nodes.append(t)

    for n in nodes:
        dist = lambda s: math.sqrt((n.ax - s.ax) ** 2 +
                                   (n.ay - s.ay) ** 2 +
                                   (n.az - s.az) ** 2) / 16.0 <= jumpRange
        graph[n] = filter(dist, nodes)

    return graph, nodes, start, end


def find_path(g, start, end, jumpRange):
    graph, nodes, start, end = make_graph(g, start, end, jumpRange)
    paths = AStarSpace(graph)
    return paths.search(start, end)
