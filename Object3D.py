import math

class WavefrontOBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
    
        for line in open(filename, "r"):
            if line.startwith('#'): continue
            values = line.split()
            if not values: continue

            if values[0] == "v": # Vertices
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertives.append(v)
            
            elif values[0] == "vn": # Normals
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(V)

            elif values[0] == "vt": # Texture coordinates
                self.texcoords.append(map(float, values[1:3]))

            elif values[0] in ("usemtl", "usemat"): # Materials
                material = values[1]

            elif values[0] == "mtllib":
                pass
            
            elif values[0] == "f":
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(2) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

   

class Node:
    def __init__(self, coordinates):
        self.x, self.y, self.z = coordinates


class Edge:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

class Object3D:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def addNodes(self, nodeList):
        for node in nodeList:
            self.nodes.append(Node(node))

    def addEdges(self, edgeList):
        for (start, stop) in edgeList:
            self.edges.append(Edge(self.nodes[start], self.nodes[stop]))

    def findCentre(self):
        num_nodes = len(self.nodes)
        meanX = sum([node.x for node in self.nodes])/num_nodes
        meanY = sum([node.y for node in self.nodes])/num_nodes
        meanZ = sum([node.z for node in self.nodes])/num_nodes
        
        return (meanX, meanY, meanZ)

    def outputNodes(self):
        print "\n --- Nodes --- "
        for i, node in enumerate(self.nodes):
            print " %d: (%.2f, %.2f, %.2f)" % (i, node.x, node.y, node.z)

    def outputEdges(self):
        print "\n --- Edges --- "
        for i, edge in enumerate(self.edges):
            print " %d: (%.2f, %.2f, %.2f)" % (i, edge.start.x, edge.start.y, edge.start.z),
            print "to (%.2f, %.2f, %.2f)" % (edge.stop.x,  edge.stop.y,  edge.stop.z)

