from graph import Graph, Node
from command import Command
from commandQueue import CommandQueue
from connection import SerialConnection
import copy
import chess
# import voice
from ui import UI

class ChessPiece:
    def __init__(self, homeNode, currentNode):
        self.homeNode = homeNode
        self.currentNode = currentNode
        self.pieceType = None
        self.pieceColor = None
    def __str__(self):
        return 'home: ' + str(self.homeNode) +  '\ncurrent: ' + str(self.currentNode)
class Game:
    def __init__(self):
        self.pieces = []
        self.piecePosition = dict()
        self.board = chess.Board()
        self.graph = Graph(self.board)
        self.turn = 'Black'
        self.moved = []

        self.ui = UI(self.graph)
        self.initializePiecePosition()
        self.ser = SerialConnection(250000)

        self.cmd_Home = Command('G28 XY')
        # self.cmd_Pickup = Command('M280 P0 S106')

        self.cmd_Pickup = Command('M280 P0 S70')
        self.cmd_DropOff = Command('M280 P0 S0')
        self.cmd_Wait = Command('M400')
        self.cmd_Smooth = Command('M204 T150')
        self.cmd_Not_Smooth = Command('M204 T9000')
        self.setUpBoard()


    def setAcceleration(self, acc):
        cmd = Command('M204 T'+str(acc))
        cmd.execute()
        self.cmd_Wait.execute()
    def setDefaultAcceleration(self):
        pass
    def moveCapturePieceToBuffer(self):
        if self.graph.whiteCaptureNode.piece:
            tempNode = self.saveNode()
            self.movePieceFromTo(self.graph.whiteCaptureNode,tempNode)
        if self.graph.blackCaptureNode.piece:
            tempNode = self.saveNode()
            self.movePieceFromTo(self.graph.blackCaptureNode,tempNode)

    def setUpBoard(self):
        self.cmd_Home.execute(1)
        self.cmd_Not_Smooth.execute()
        Command("M220 S100").execute()

    def setSmoothMove(self,par):
        com2 = None
        if par:
            com2 = Command('M204 T 3000')
        else:
            com2 = Command('M204 T 9000')
        com2.execute()
    def makeMove(self, move):
        self.moveCapturePieceToBuffer()
        self.board.push(move)
        self.graph.updateGraph(self.board)
    def captureMove(self, origin, destination):
        tempNode = self.saveNode()
        self.movePieceFromTo(destination, tempNode)
        self.moveToOrigin(origin)
        self.movePieceFromTo(origin,destination)

    def updateCastling(self,side, clr):
        if clr == chess.BLACK:
            if side == "qs":
                self.movePieceFromTo(self.graph.chessPositions['a8'],self.graph.chessPositions['d8'])
            elif side == "ks":
                self.movePieceFromTo(self.graph.chessPositions['h8'],self.graph.chessPositions['f8'])
        else:
            if side == "qs":
                self.movePieceFromTo(self.graph.chessPositions['a1'],self.graph.chessPositions['d1'])
            elif side == "ks":
                self.movePieceFromTo(self.graph.chessPositions['h1'],self.graph.chessPositions['f1'])
            
    def saveNode(self):
        tempNode = None
        if self.board.turn == chess.BLACK:
            if not self.graph.isBufferLeftFull():
                tempNode = self.graph.bufferLeft.pop(0)
                self.graph.activeBufferLeft.append(tempNode)
            else:
                tempNode = self.graph.bufferRight.pop()
                self.graph.activeBufferRight.append(tempNode)

        else :
            if not self.graph.isBufferRightFull():
                tempNode = self.graph.bufferRight.pop()
                self.graph.activeBufferRight.append(tempNode)
            else:
                tempNode = self.graph.activeBufferLeft.pop(0)
                self.graph.activeBufferLeft.append(tempNode)
        return tempNode

    def home(self):
        self.cmd_DropOff.execute()
        self.cmd_Home.execute()
        
    def moveToOrigin(self,node):
        self.setSmoothMove(False)
        # self.setSmoothMove(False)
        self.cmd_DropOff.execute()
        self.cmd_Wait.execute()
        move = Command('G1', node.x, node.y)
        move.execute()
        self.setSmoothMove(True)

    def updatePiecePosition(self, fromPosition, toPosition):
        if  toPosition.isEmpty():
            tempP = ChessPiece(fromPosition.piece.homeNode, toPosition)
            tempP.pieceType = fromPosition.piece.pieceType
            tempP.pieceColor = fromPosition.piece.pieceColor
            
            toPosition.piece = tempP
            
        fromPosition.piece = None
    def updateCaptureMove(self,fromPosition, toPosition):
        if self.board.turn == chess.BLACK:
            self.updatePiecePosition(toPosition, self.graph.blackCaptureNode)
        else:
            self.updatePiecePosition(toPosition, self.graph.whiteCaptureNode)
        self.updatePiecePosition(fromPosition,toPosition)

    def movePieceFromTo(self, fromPosition, toPosition):
        self.updatePiecePosition(fromPosition,toPosition)
        self.cmd_DropOff.execute()
        self.graph.origin=fromPosition
        self.graph.destination=toPosition
        nodes = self.graph.a_star(fromPosition, toPosition)
        if not nodes:
            return
        cmdQueue = CommandQueue()
        self.moveToOrigin(fromPosition)
        cmdQueue.push(cmdQueue.cmd_wait)
        cmdQueue.push(cmdQueue.cmd_pickup)

        self.graph.updateGraph(self.board)  

        for i in range(0, len(nodes)-1):
            allViableNodes = []
            for key,nextNode in self.graph.chessPositions.items():
                if nextNode.piece != None:
                    allViableNodes.append(nextNode)
            
            node = nodes[i+1]
            threshold = 17
            
            if not allViableNodes:
                break
            shortestNode = None
            distanceH = 1000000
            for nextNode in allViableNodes:
                distance = ((node.x - nextNode.x)**2 + (node.y - nextNode.y)**2)**(1/2)
                if distance == 0:
                    continue
                if distance < distanceH:
                    shortestNode = nextNode
                    distanceH = distance

            speed = str(50 + (distanceH/16)*150)
            cmdQueue.push(Command('M220 S' + speed))
            self.ui.update()
            
            cmdQueue.push(Command('G1',nodes[i].x,nodes[i].y))
            
            if len(nodes) >= 4:
                if i == 0:
                    cmdQueue.push(self.cmd_Not_Smooth)
                if i == len(nodes)-2:
                    cmdQueue.push(self.cmd_Smooth)
            cmdQueue.push(Command('G1',nodes[i+1].x,nodes[i+1].y))

        cmdQueue.push(cmdQueue.cmd_wait)
        cmdQueue.push(cmdQueue.cmd_dropoff)
        cmdQueue.executeAll()
    def recordPiecePosition(self):
        pass
    def resetBoard(self):
        for i in range(0,19):
            for j in range(0,17):
                if i == 0:
                    self.graph.nodes[(i,j)].addNeighbor(self.graph.nodes[(i+1,j)],1)
                if i+1 == 19:
                    self.graph.nodes[(i,j)].addNeighbor(self.graph.nodes[(i-1,j)],1)
        bufferNodes = []

        for key, node in self.graph.nodes.items():
            if not node.isEmpty():
                node1 = node.piece.homeNode
                if (node != node1):
                        if not node1.isEmpty():
                            bufferNode = self.graph.findClosetEmptyNode(node1)
                            self.movePieceFromTo(node1, bufferNode)
                            bufferNodes.append(bufferNode)
                        self.movePieceFromTo(node, node1)
        for node in bufferNodes:
            if not node.isEmpty():
                node1 = node.piece.homeNode
                if (node != node1):
                    self.movePieceFromTo(node,node1)

    def initializePiecePosition(self):
        pieceIndex = 0
        for i in range (0,64):
            if self.board.piece_at(i) != None:
                pieceC = ChessPiece(self.graph.chessPositions[chess.SQUARE_NAMES[i]],self.graph.chessPositions[chess.SQUARE_NAMES[i]])
                myPiece = self.board.piece_at(i)
                if myPiece.color == chess.WHITE:
                    pieceC.pieceColor = "W"
                else:
                    pieceC.pieceColor = "B"
                if myPiece.piece_type == chess.KING:
                    pieceC.pieceType = "K"
                elif myPiece.piece_type == chess.QUEEN:
                    pieceC.pieceType = "Q"
                elif myPiece.piece_type == chess.ROOK:
                    pieceC.pieceType = "R"
                elif myPiece.piece_type == chess.BISHOP:
                    pieceC.pieceType = "B"
                elif myPiece.piece_type == chess.KNIGHT:
                    pieceC.pieceType = "N"
                elif myPiece.piece_type == chess.PAWN:
                    pieceC.pieceType = "P"
                
                self.graph.chessPositions[chess.SQUARE_NAMES[i]].piece = pieceC
                self.pieces.append(pieceC)
            else:
                self.graph.initialUnOccupiedCells.append(self.graph.chessPositions[chess.SQUARE_NAMES[i]])


    def setPiecePosition(self,pieceName, node):
        self.piecePosition[pieceName] = node

    def probeBoard(self):
        currentNode = self.graph.chessPositions['a8']
        allViableNodes = []
        for key,node in self.graph.nodes.items():
            if node.piece != None:
                allViableNodes.append(node)
        doneList = []
        while True:
            if not allViableNodes:
                break

            shortestNode = None
            distanceH = 1000000
            for nextNode in allViableNodes:
                if nextNode in doneList:
                    continue
                distance = ((currentNode.x - nextNode.x)**2 + (currentNode.y - nextNode.y)**2)**(1/2)
                if distance < distanceH:
                    shortestNode = nextNode
                    distanceH = distance
            allViableNodes.pop(allViableNodes.index(shortestNode))
            currentNode = shortestNode
            self.moveToOrigin(currentNode)
            self.cmd_Wait.execute()
            self.cmd_Pickup.execute()
            self.cmd_Wait.execute()
            self.cmd_DropOff.execute()
            doneList.append(currentNode)