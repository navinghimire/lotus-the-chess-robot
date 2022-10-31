from ui import UI
import math
import uuid
from heapq import heappush, heappop
class Node:
    def __init__(self, x = 0, y = 0):
        self.neighbors = dict()
        self.x = x
        self.y = y
        self.piece = None
        self.parent = None
        self.costs = dict()
        self.f = 0
        self.g = 0
        return
    
    # takes node, cost and adds the tuple to neighbor property (edge)
    
    def addNeighbor(self, newNode, cost):
        self.costs[newNode] = cost
        self.g = cost
        # if newNode not in self.neighbors:
        #     self.neighbors.append({newNode: cost})
        #     if (self not in newNode.neighbors):
        #         newNode.addNeighbor(self,cost)
        if not newNode in self.neighbors.keys():
            self.neighbors[newNode] = cost
            if self not in newNode.neighbors.keys():
                newNode.addNeighbor(self,cost)

    #removes all the neighboring
    def removeAllNeighbors(self):
        # print('Total ', len(self.neighbors))
        for neighbor in self.neighbors.keys():
            if (self in neighbor.neighbors.keys()):
                # print('Removing')
                del neighbor.neighbors[self]
        # print(len(self.neighbors))
        self.neighbors = dict()
    def __str__(self):
        return 'X: ' + str(self.x) + " Y: " + str(self.y)+'\n'
    def distanceTo(self, node):
        return math.sqrt((self.x-node.x)**2+(self.y-node.y)**2)


class Graph:
    
    # holds all the nodes on the left hand side of the board
    bufferLeft= []

    # holds all the nodes on the right hand side of the board
    bufferRight = []

    # all the chess positions in a1 ... h8
    chessPositions = []

    pathFromStartToEnd = []

    def __init__(self):
        self.g = dict()
        self.nodes = dict()
        return

    # add 
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

    def addToChessPositions(self, node):
        self.chessPositions.append(node)

    def removeNeighbors(self,node):
        self.nodes[node].removeAllNeighbors()

    def a_star(self,startNode, endNode):
        openList = []
        closeList = []
        startNode.g = 0
     
        startNode.f = self.distance(startNode,endNode)
        heappush(openList,(startNode.f,uuid.uuid1(), startNode))
        camefrom = dict()
        # print(openList)
      
        while openList:
            f,i,current = heappop(openList)

            closeList.append(current)
            if current == endNode:
                print("Path found")
                self.reconstructPath(camefrom,current)
                return
            # print(current)
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
                
    def reconstructPath(self,camefrom, current):
        pathList = [current]
        while current in camefrom.keys():
            current = camefrom[current]
            pathList.insert(0,current)
        self.pathFromStartToEnd = pathList
        for path in pathList:
            print(path)


    def isNodeinList(self,node,lst):
        # print('checking ',node, ' in ', lst)
        for f,i,n in lst:
            if node == n:
                return True
        return False      
    def distance(self,node1, node2):
        # print(type(node1), type(node2))
        return math.sqrt((node2.x-node1.x)**2+(node2.y-node1.y)**2)

    def pathCost(self, node1, node2):
        return node1.neighbors[node2]

def main():
    graph = Graph()
    startX = (300-(270/8)*9)/2
 
    for i in range(0,20):
        for j in range(0,17):
  
            newNode = Node(min(max(startX+i*270/16,0),300),j*270/16)
            # print(id(newNode))
            graph.addNode(newNode,(i,j))
            if i == 0:
                graph.addToBuffer(newNode,'R')
            elif i == 19:
                graph.addToBuffer(newNode,'L')
            if (i%2 == 0 and (i != 0 and i != 18)) and (j%2 != 0):
                graph.addToChessPositions(newNode)

    for i in range(0,20):
        for j in range(0,17):
            if (i%2 == 0 and (i != 0 and i != 18)) and (j%2 != 0):
                graph.nodes[(i,j)].piece = True

                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j-1)],math.sqrt(2)) # top left
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j)],1) # top center
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j+1)],math.sqrt(2)) # top right
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j-1)],1) # middle left
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j+1)],1) # middle right
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j-1)],math.sqrt(2)) # bottom left
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j)],1) # bottom center
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j+1)],math.sqrt(2)) # bottom right

                graph.nodes[(i-1,j-1)].addNeighbor(graph.nodes[(i,j-1)],1) # bottom center
                graph.nodes[(i-1,j-1)].addNeighbor(graph.nodes[(i-1,j)],1) # bottom right
                graph.nodes[(i,j-1)].addNeighbor(graph.nodes[(i+1,j-1)],1) # bottom right
                graph.nodes[(i+1,j-1)].addNeighbor(graph.nodes[(i+1,j)],1) # bottom right
                graph.nodes[(i+1,j)].addNeighbor(graph.nodes[(i+1,j+1)],1) # bottom right
                graph.nodes[(i+1,j+1)].addNeighbor(graph.nodes[(i,j+1)],1) # bottom right
                graph.nodes[(i,j+1)].addNeighbor(graph.nodes[(i-1,j+1)],1) # bottom right
                graph.nodes[(i-1,j+1)].addNeighbor(graph.nodes[(i-1,j)],1) # bottom right
                

            if i == 0:
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j)],1)
            if i+1 == 19:
                graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j)],1)
            # if (i% 2 == 1 and (i != 1 and i!= 17 and i!=19)) and (j%2 == 0 and (j !=0 and j != 16)):
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j)]) # top left
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j-1)]) # top center
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j)]) # top right
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j+1)]) # middle left
            # if i == 1 and (j!=0 and j!= 16):
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j-1)]) # top left
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j+1)]) # top center
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i+1,j)]) # top right
            # if i == 17 and (j!=0 and j!= 16):
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j-1)]) # top left
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j+1)]) # top center
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j)]) # top right
            # if i == 17 and (j!=0 and j!= 16):
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j-1)]) # top left
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i,j+1)]) # top center
            #     graph.nodes[(i,j)].addNeighbor(graph.nodes[(i-1,j)]) # top right
                                 
    # print(len(graph.nodes[(10,10)].neighbors))
    # graph.removeNeighbors((14,16))            
    # print(len(graph.nodes[(14,16)].neighbors))                     
    # print(len(graph.nodes[(14,16)].neighbors))  
    # for (i,j), value in graph.nodes.items():
        
    #     if value.piece:
    #         value.removeAllNeighbors()
        
    graph.a_star(graph.nodes[(1,0)],graph.nodes[(7,6)]) 
            


    ui = UI(graph)
    return
if __name__ == "__main__":
    main()