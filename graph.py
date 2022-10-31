import math
import uuid
import chess
import time
from heapq import heappush, heappop
import random

class Node:
    def __init__(self,nodeIndex, x = 0, y = 0):
        self.nodeIndex = nodeIndex
        self.neighbors = dict()
        self.x = x
        self.y = y
        self.parent = None
        self.costs = dict()
        self.f = 0
        self.g = 0
        self.piece = None
        return
    
    def addNeighbor(self, newNode, cost):
        self.costs[newNode] = cost
        self.g = cost
        if not newNode in self.neighbors.keys():
            self.neighbors[newNode] = cost
            if self not in newNode.neighbors.keys():
                newNode.addNeighbor(self,cost)
    def isEmpty(self):
        return self.piece == None

    def removeAllNeighbors(self):
        for neighbor in self.neighbors.keys():
            if (self in neighbor.neighbors.keys()):
                del neighbor.neighbors[self]
        self.neighbors = dict()
    def __str__(self):
        return 'X: ' + str(self.x) + " Y: " + str(self.y)+'\n'
    def distanceTo(self, node):
        return math.sqrt((self.x-node.x)**2+(self.y-node.y)**2)
    def getDensity(self):
        pass        

class Graph:
    blackCaptureNode = None
    whiteCaptureNode = None
    blackSquares = []
    whiteSquares = [] 
    bufferLeft = []
    bufferRight = []
    activeBufferLeft = []
    activeBufferRight = []
    chessPositions = dict()
    initialUnOccupiedCells = []
    pathFromStartToEnd = []

    def __init__(self, board):
        self.g = dict()
        self.nodes = dict()
        self.origin = None
        self.destination = None
        self.initialize()
        self.addEightNeighbors(self.chessPositions['a1'])
        self.addEightNeighbors(self.chessPositions['h8'])
        self.updateGraph(board)
        return

    def updateGraph(self, board):
        for i in range (0,64):
            if board.piece_at(i) != None:
                self.removeNeighbors(self.chessPositions[chess.SQUARE_NAMES[i]])
 
    def isBufferLeftFull(self):
        return len(self.bufferLeft) == 0
    def isBufferRightFull(self):
        return len(self.bufferRight) == 0
        
    def moveNodetoBuffer(self, node):
        
        pass

    def addNode(self, node,indexTuple):
        self.nodes[indexTuple] = node

    def __str__(self):
        res = ''
        for key,value in self.nodes.items():
            res += str(value)
        return res

    def getNodes(self):
        return self.nodes

    def addToBuffer(self, node, left_right):
        if str.upper(left_right) == 'L':
            self.bufferLeft.append(node)
        else:
            self.bufferRight.append(node)

    def addToChessPositions(self, key, node):
        self.chessPositions[key] = node



    def openNode(self,node):
        return

    def a_star(self,startNode, endNode):
        if startNode in self.chessPositions.values():
            self.addEightNeighbors(startNode)
        if endNode in self.chessPositions.values():
            self.addEightNeighbors(endNode)

        self.origin = startNode
        self.destination = endNode
        openList = []
        closeList = []
        startNode.g = 0
     
        startNode.f = self.distance(startNode,endNode)
        heappush(openList,(startNode.f,uuid.uuid1(), startNode))
        camefrom = dict()
        while openList:
            f,i,current = heappop(openList)
            closeList.append(current)
            if current == endNode:
                endNode.removeAllNeighbors()
                pathList = [current]
                while current in camefrom.keys():
                    current = camefrom[current]
                    pathList.insert(0,current)
                self.pathFromStartToEnd = pathList
                return pathList
            for neighbor in current.neighbors:
                if neighbor in closeList:
                    continue
           
                neighbor.g = current.g + current.costs[neighbor]
                neighbor.h = self.distance(neighbor,endNode)
                neighbor.f = neighbor.g + neighbor.h
                for f,i, openNode in openList:
                    if self.isNodeinList(neighbor,openList):
                        if neighbor.g > openNode.g:
                            continue
                    
                camefrom[neighbor] = current
               
                heappush(openList,(neighbor.f, uuid.uuid1(), neighbor)) 
                

    def isNodeinList(self,node,lst):
        for f,i,n in lst:
            if node == n:
                return True
        return False      
    def distance(self,node1, node2):
        return math.sqrt((node2.x-node1.x)**2+(node2.y-node1.y)**2)

    def pathCost(self, node1, node2):
        return node1.neighbors[node2]
    def addEightNeighbors(self, node):
        i,j = node.nodeIndex
        node.addNeighbor(self.nodes[(i-1,j-1)],math.sqrt(2)) # top left
        node.addNeighbor(self.nodes[(i-1,j)],1) # top center
        node.addNeighbor(self.nodes[(i-1,j+1)],math.sqrt(2)) # top right
        node.addNeighbor(self.nodes[(i,j-1)],1) # middle left
        node.addNeighbor(self.nodes[(i,j+1)],1) # middle right
        node.addNeighbor(self.nodes[(i+1,j-1)],math.sqrt(2)) # bottom left
        node.addNeighbor(self.nodes[(i+1,j)],1) # bottom center
        node.addNeighbor(self.nodes[(i+1,j+1)],math.sqrt(2)) # bottom right

    def removeNeighbors(self, node):
        node.removeAllNeighbors()

    def setOccupied(self, positionStr):
        self.removeNeighbors(self.chessPositions[positionStr])

    def setOpen(self, positionStr):
        self.addEightNeighbors(self.chessPositions[positionStr])
    
    def initialize(self):
        startX = (300-(270/8)*9)/2
        for i in range(0,19):
            for j in range(0,17):
                nodeIndex = (i,j)
                newNode = Node(nodeIndex, min(max(startX+i*270/16,0),300),j*270/16)
                self.addNode(newNode,(i,j))
                if i == 0:
                    self.addToBuffer(newNode,'R')
                elif i == 18:
                    self.addToBuffer(newNode,'L')
                if (i%2 == 0 and (i != 0 and i != 18)) and (j%2 != 0):
                    key = str(chr(96+i//2)) + str(9-(j+1)//2)
                    self.addToChessPositions(key,newNode)
        counter = 0
        for i in range(2,17):
            pawn_counter = 1
            for j in range(0,17):
                if i%2 == 0 and j%2 != 0:
                    counter += 1
                    self.addEightNeighbors(self.nodes[(i,j)])
                    pawn_counter += 1
                    self.nodes[(i-1,j-1)].addNeighbor(self.nodes[(i,j-1)],1) # bottom center
                    self.nodes[(i-1,j-1)].addNeighbor(self.nodes[(i-1,j)],1) # bottom right
                    self.nodes[(i,j-1)].addNeighbor(self.nodes[(i+1,j-1)],1) # bottom right
                    self.nodes[(i+1,j-1)].addNeighbor(self.nodes[(i+1,j)],1) # bottom right
                    self.nodes[(i+1,j)].addNeighbor(self.nodes[(i+1,j+1)],1) # bottom right
                    self.nodes[(i+1,j+1)].addNeighbor(self.nodes[(i,j+1)],1) # bottom right
                    self.nodes[(i,j+1)].addNeighbor(self.nodes[(i-1,j+1)],1) # bottom right
                    self.nodes[(i-1,j+1)].addNeighbor(self.nodes[(i-1,j)],1) # bottom right

        for i in range(0,19):
            for j in range(0,17):
                if i == 0:
                    counter+=1
                    self.nodes[(i,j)].addNeighbor(self.nodes[(i+1,j)],1)
                if i+1 == 19:
                    self.nodes[(i,j)].addNeighbor(self.nodes[(i-1,j)],1)
                    counter+=1
        self.whiteCaptureNode = self.nodes[(0,0)]
        self.blackCaptureNode = self.nodes[(18,16)]
    def findClosetEmptyNode(self, node): 
        shortestNode = None
        distanceH = 1000000
        for nextNode in self.initialUnOccupiedCells:
            if not nextNode.isEmpty():
                continue
            distance = ((node.x - nextNode.x)**2 + (node.y - nextNode.y)**2)**(1/2)
            if distance < distanceH:
                shortestNode = nextNode
                distanceH = distance
                print("distance: ", distance, "shortest: ",distanceH)
        print("shortest distance ", distanceH)

        return shortestNode
  

