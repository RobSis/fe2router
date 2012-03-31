import sys

import pygame
from pygame.locals import *

from Object3D import *

class ProjectionView:
    def __init__(self, width_height):
        self.models = {}
        self.width = width_height[0]
        self.height = width_height[1]

        self.nodeColour = (255,255,255)
        self.edgeColour = (200,200,200)
        self.nodeRadius = 4

    def addModel(self, name, wireframe):
        self.models[name] = wireframe

    def display(self, screen):
        for model in self.models.values():
            for edge in model.edges:
                pygame.draw.aaline(screen, self.edgeColour, (edge.start.x, edge.start.y), (edge.stop.x, edge.stop.y), 1)

            for node in model.nodes:
                pygame.draw.circle(screen, self.nodeColour, (int(node.x), int(node.y)), 2)



    #####################
    ## 3D Transformations
    def translate(self, model, axis, d):
        if axis in ['x', 'y', 'z']:
            for node in self.models[model].nodes:
                setattr(node, axis, getattr(node, axis) + d)

    def scale(self, model, scale):
        centre_x = self.width/2
        centre_y = self.height/2

        for node in self.models[model].nodes:
            node.x = centre_x + scale*(node.x - centre_x)
            node.y = centre_y + scale*(node.y - centre_y)
            node.z *= scale

    def rotateZ(self, model, radians):
        (cx,cy,cz) = self.models[model].findCentre()
    
        for node in self.models[model].nodes:
            x      = node.x - cx
            y      = node.y - cy
            d      = math.hypot(y, x)
            theta  = math.atan2(y, x) + radians
            node.x = cx + d * math.cos(theta)
            node.y = cy + d * math.sin(theta)

    def rotateX(self, model, radians):
        (cx,cy,cz) = self.models[model].findCentre()
    
        for node in self.models[model].nodes:
            y      = node.y - cy
            z      = node.z - cz
            d      = math.hypot(y, z)
            theta  = math.atan2(y, z) + radians
            node.y = cy + d * math.sin(theta)
            node.z = cz + d * math.cos(theta)

    def rotateY(self, model, radians):
        (cx,cy,cz) = self.models[model].findCentre()
    
        for node in self.models[model].nodes:
            x      = node.x - cx
            z      = node.z - cz
            d      = math.hypot(x, z)
            theta  = math.atan2(x, z) + radians
            node.x = cx + d * math.sin(theta)
            node.z = cz + d * math.cos(theta)

class Camera:
    def __init__(self, screen_size):
        self.position = (screen_size[0]/2.0, screen_size[1]/2.0)


    def calculate_view_distance(self, fov, screen_width):
        d = (screen_width/2.0) / math.tan(fov/2.0)
        return d

class VideoDriver:
    def __init__(self):
        pygame.init()

        self.screen_size = (640, 480)

        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Pylot space game")

        pygame.mouse.set_visible(1)

        self.KeyStatus = { "Left":False, "Right":False, "Up":False, 
                "Down":False,
        }

        self.clock = pygame.time.Clock()

        self.distance = 0
   
    def run(self):
        while 1:
            self.DoEvents()

            self.update()
                        

            self.clock.tick(40);
            self.screen.fill((0,32,0))

            cube.addNodes(cube_nodes)

#            cube.addEdges([(n,n+4) for n in range(0,4)])
#            cube.addEdges([(n,n+1) for n in range(0,8,2)])
#            cube.addEdges([(n,n+2) for n in (0,1,4,5)])

            self.pv = ProjectionView(self.screen_size)
            self.pv.addModel('cube', cube)


            self.pv.rotateX('cube', self.distance)
            self.pv.rotateY('cube', self.distance)
            self.pv.rotateZ('cube', self.distance)

            self.pv.display(self.screen)

            

            pygame.display.flip()

    def update(self):
        if self.KeyStatus["Up"] and not self.KeyStatus["Down"]:
            pass


        if self.KeyStatus["Down"] and not self.KeyStatus["Up"]:
            self.distance -= 0.1




    def flush(self):
        pygame.display.flip()

    def DoEvents(self):
        """Handle all the events on the queue"""
        for event in pygame.event.get():
            self.ProcessEvent(event)

    def ProcessEvent(self, event):
        """Low level processing of a singular event."""
        if event.type == pygame.QUIT:
            self.OnQuit()
        elif event.type == pygame.VIDEORESIZE:
            #self.OnSize(event.w, event.h)
            pass
        elif event.type == pygame.KEYDOWN:
            self.OnKeyDown(event)
        elif event.type == pygame.KEYUP:
            self.OnKeyUp(event)

    def OnKeyDown(self, event):
        if event.key == pygame.K_LEFT:
            self.KeyStatus["Left"] = True
        elif event.key == pygame.K_RIGHT:
            self.KeyStatus["Right"] = True
        elif event.key == pygame.K_UP:
            self.KeyStatus["Up"] = True
        elif event.key == pygame.K_DOWN:
            self.KeyStatus["Down"] = True

    def OnKeyUp(self, event):
        if event.key == pygame.K_LEFT:
            self.KeyStatus["Left"] = False
        elif event.key == pygame.K_RIGHT:
            self.KeyStatus["Right"] = False
        elif event.key == pygame.K_UP:
            self.KeyStatus["Up"] = False
        elif event.key == pygame.K_DOWN:
            self.KeyStatus["Down"] = False

    def OnQuit(self):
        print "Exit successful"
        pygame.quit()
        exit()
   


if __name__ == "__main__":
    VideoDriver().run()
