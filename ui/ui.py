import pygame,sys
import random
import math
class UI:
     
    scaleFactor = 2
    windowWidth = 640*scaleFactor
    windowHeight = 480 * scaleFactor
    screen = pygame.display.set_mode((windowWidth,windowHeight))
    def __init__(self, graph):
        self.graph = graph
        pygame.init()
        while True:
            for event in pygame.event.get():   
                if event.type == pygame.QUIT:
                    sys.exit()
            self.screen.fill((255,255,255))
            self.renderGraph()
            pygame.display.flip()
        return
    def renderGraph(self):
        originX = (self.windowWidth - 600)/2
        originY = (self.windowHeight - 540)/2
        gray = (100,100,100)
        black = (240,240,240)
        light = (100,100,100)
        color = light

        # for index, node in self.graph.nodes.items():
        #     if node in self.graph.chessPositions:
            
        for index,node in self.graph.nodes.items():
            
            for neighbor in node.neighbors:
                pygame.draw.line(self.screen, gray, (originX+neighbor.x*self.scaleFactor, originY+neighbor.y*self.scaleFactor), (originX+node.x*self.scaleFactor,originY+node.y*self.scaleFactor))

        for index,node in self.graph.nodes.items():
            color = (255,0,0)
            radius = 5
            if node in self.graph.chessPositions:
                radius = 16
            if node in self.graph.bufferLeft:
                color = (0,255,0)
            elif node in self.graph.bufferRight:
                color = (0,0,255)
            pygame.draw.circle(self.screen,color,(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), radius)
        m = self.graph.pathFromStartToEnd
        for i in range (0, len(self.graph.pathFromStartToEnd)-1):
            pygame.draw.line(self.screen,(0,0,255),(originX+m[i].x*self.scaleFactor,originY+m[i].y*self.scaleFactor),(originX+m[i+1].x*self.scaleFactor,originY+m[i+1].y*self.scaleFactor),5)