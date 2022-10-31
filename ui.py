import pygame,sys
import pygame.locals
import math
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" %(0,0)
class SpriteSheet(object):
    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert()
        self.width = 360/6
        self.height = 120/2
    def get_image(self,piece,color):
        indx = 0
        p = 0
        if piece == "Q":
            indx = 0
        elif piece == "K":
            indx = 1
        elif piece == "R":
            indx = 2
        elif piece == "N":
            indx = 3
        elif piece == "B":
            indx = 4
        elif piece == "P":
            indx = 5

        if color == "B":
            p = 0
        elif color == "W":
            p = 1

        image = pygame.Surface([self.width, self.height]).convert()
        image.blit(self.sprite_sheet,(0,0),(indx*self.width,p*self.height,self.width,self.height))
        image.set_colorkey((255,255,255))
        return image
    def get_cell_size(self):
        return [self.width,self.height]

class UI:
    def __init__(self, graph):
        pygame.init()
        self.scaleFactor = 2
        self.windowWidth = 640*self.scaleFactor
        self.windowHeight = 480 * self.scaleFactor
        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        self.screen.fill((255,255,255))
        self.clock = pygame.time.Clock()
        self.sprite = SpriteSheet('pieces.png')
        self.graph = graph


    def update(self):
        self.screen.fill((255,255,255))
        originX = (self.windowWidth - 600)/2
        originY = (self.windowHeight - 540)/2
        gray = (100,100,100)
        black = (240,240,240)
        light = (100,100,100)
        color = light
        off = 270/16 * self.scaleFactor
        c = (242, 235, 223)
        
        for key,cell in self.graph.chessPositions.items():
            pygame.draw.rect(self.screen,c, pygame.Rect(originX-off+self.scaleFactor*cell.x+1, originY-off+ self.scaleFactor*cell.y+1, off*2-1, off*2-1))
            sqrFile = ord(key[0])
            sqrRank = int(key[1])
            if (sqrFile%2 == 1 and sqrRank%2 == 1) or (sqrFile%2==0 and sqrRank%2 == 0):
                pygame.draw.rect(self.screen,(130, 159, 217), pygame.Rect(originX-off+self.scaleFactor*cell.x+1, originY-off+ self.scaleFactor*cell.y+1, off*2-1, off*2-1))
            else:
                pygame.draw.rect(self.screen,c, pygame.Rect(originX-off+self.scaleFactor*cell.x+1, originY-off+ self.scaleFactor*cell.y+1, off*2-1, off*2-1))
        
        m = self.graph.pathFromStartToEnd
        for i in range (0, len(self.graph.pathFromStartToEnd)-1):
            pygame.draw.line(self.screen,(217, 115, 123),(originX+m[i].x*self.scaleFactor,originY+m[i].y*self.scaleFactor),(originX+m[i+1].x*self.scaleFactor,originY+m[i+1].y*self.scaleFactor),6)

        for index,node in self.graph.nodes.items():                
            color = (255,200,200)
            radius = 5
            if node in self.graph.chessPositions.values():
                radius = 16
                
                if node == self.graph.origin:
                    color = (217, 115, 123)
                elif node == self.graph.destination:
                    color = (242, 173, 167)
                



            if node in self.graph.bufferLeft or node in self.graph.bufferRight:
                color = (242, 206, 162)
                pygame.draw.circle(self.screen,color,(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), radius)
            cellwidth,cellheight = self.sprite.get_cell_size()

            if not node.isEmpty():
                if node in self.graph.activeBufferLeft or node in self.graph.activeBufferRight:
                    transformedImage = pygame.transform.scale(self.sprite.get_image(node.piece.pieceType,node.piece.pieceColor),(30,30))
                    self.screen.blit(transformedImage,(originX-15+node.x*self.scaleFactor,originY-15+node.y*self.scaleFactor))
                else:
                    self.screen.blit(self.sprite.get_image(node.piece.pieceType,node.piece.pieceColor),(originX-(cellwidth//2)+node.x*self.scaleFactor,originY-(cellheight//2)+node.y*self.scaleFactor))

            if len(m) > 0:
                if node == m[0]:
                    pygame.draw.circle(self.screen,(5, 191, 125),(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), 8)
                if node == m[len(m)-1]:
                    pygame.draw.circle(self.screen,(255, 0, 0),(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), 8)
                    
            if node == self.graph.blackCaptureNode:
                pygame.draw.circle(self.screen,(255, 0,0),(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), 16)
                
            if node == self.graph.whiteCaptureNode:
                pygame.draw.circle(self.screen,(0, 255,0),(math.ceil(originX+node.x*self.scaleFactor), math.ceil(originY+node.y*self.scaleFactor)), 16)
                
        
        pygame.display.flip()
