import serial
import time
import constants
import random
import chess
import chess.pgn
import chess.svg
import pyttsx3
# import opencv
import threading
# import voice
from command import Command
from collections import deque
from stockfish import Stockfish
from game import Game
from graph import Graph, Node
from enum import Enum
from connection import SerialConnection

class GameMode(Enum):
    VS_AI = 1
    DATABASE = 2
    SANDBOX = 3

gameMode = GameMode.DATABASE
NARRATION = False
move_str = ""
def main():
    players = dict()
    
    if gameMode == GameMode.VS_AI:
        game = Game()
        stockfish = Stockfish('./stockfish_15_linux_x64_ssse')
        userMove = ''
        userName = ''
            # ------------------------------------------------
        # move_str = input("Black(0) or White(1)?: ")
        move_str = "1"
        # if userName == '':
        #     userName = input("Your Name: ")
        userName = "Dhwani"
        move = None
        # sayStr = userName + ", You've choosen to play white. You are ready to make your move once you hear the beep sound."
        
        if move_str == '1':

            players['White'] = userName
            players['Black'] = 'Stockfish'
            while True:
                cell1, cell2 = opencv.getUserMoveFromCamera(game.board)
                # print(cell1,cell2)
                move1 = chess.Move.from_uci(cell1+cell2)
                move2 = chess.Move.from_uci(cell2+cell1)
                if move1 in game.board.legal_moves:
                    move = move1
                elif move2 in game.board.legal_moves:
                    move = move2
                else:
                    pass
                    # print("Illegal move", cell1,cell2)
                    # voice.say("Its an illegal move. Try again.")
                if move in game.board.legal_moves:
                    fromPosition = game.graph.chessPositions[chess.SQUARE_NAMES[move.from_square]]
                    toPosition = game.graph.chessPositions[chess.SQUARE_NAMES[move.to_square]]
                    game.updatePiecePosition(fromPosition,toPosition)
                    game.makeMove(move)
                    # movePiecesInBoard(game,move)
                    break
                else:
                    # voice.say("error")
                    pass
        while not game.board.is_game_over():
            stockfish.set_fen_position(game.board.fen())
            move = chess.Move.from_uci(stockfish.get_best_move())
            is_capture = game.board.is_capture(move)

            # print(game.board)
            # if is_capture:
            #     voice.say("This is a capture move")
 
            movePiecesInBoard(game,move,players)

           # game.makeMove(move)
            is_check = game.board.is_check()
            is_checkmate = game.board.is_checkmate()
            # print(is_check, is_checkmate)
            # if is_checkmate: 
            #     voice.say("Checkmate!!")
            # elif is_check:
            #     voice.say("Check!")
            
            fromSquare = chess.SQUARE_NAMES[move.from_square]
            toSquare = chess.SQUARE_NAMES[move.to_square]
 
            while not game.board.is_game_over():
                cell1, cell2 = opencv.getUserMoveFromCamera(game.board)
                move1 = chess.Move.from_uci(cell1+cell2)
                move2 = chess.Move.from_uci(cell2+cell1)
                if move1 in game.board.legal_moves:
                    move = move1
                elif move2 in game.board.legal_moves:
                    move = move2
                else:
                    pass
                is_captureMove = game.board.is_capture(move)
    
                fs = game.graph.chessPositions[chess.SQUARE_NAMES[move.from_square]]
                ts = game.graph.chessPositions[chess.SQUARE_NAMES[move.to_square]]
                if move in game.board.legal_moves:
                    clr = game.board.turn
                    is_qsCastling = game.board.is_queenside_castling(move)
                    is_ksCastling = game.board.is_kingside_castling(move)
                    game.makeMove(move)
                    
                    if is_captureMove:
                        game.updateCaptureMove(fs,ts)
                    elif is_qsCastling:
                        game.updatePiecePosition(fs,ts)
                        game.updateCastling("qs",clr)
                    elif is_ksCastling:
                        game.updatePiecePosition(fs,ts)
                        game.updateCastling("ks",clr)
                    else:
                        game.updatePiecePosition(fs,ts)
                    
                    break
        voice.say("Thanks for playing. Resetting board.")
        game.resetBoard()

    elif gameMode == GameMode.DATABASE:
        pgn = open('Carlsen.pgn')
        while pgn:
            gamePGN = chess.pgn.read_game(pgn)
            game = Game()
            blackPlayer = gamePGN.headers['Black'].split(',')[0]
            whitePlayer = gamePGN.headers['White'].split(',')[0]
            if NARRATION:
                voice.say("Lets look at a game between " + \
                    gamePGN.headers['White'] + " playing white and " + \
                    gamePGN.headers['Black'] + " playing black in " + \
                    gamePGN.headers['Date'] + " at " + gamePGN.headers['Site'])
            moveCount = 0

            player = whitePlayer
            for move in gamePGN.mainline_moves():
                movePiecesInBoard(game,move, gamePGN.headers)
                moveCount += 1
                game.graph.updateGraph(game.board)
            if NARRATION:
                voice.say("That was the final move in the game.")
            game.resetBoard()
            game.probeBoard()
    elif gameMode == GameMode.SANDBOX: 
        game = Game()

        while True:
            txt = input()
            print(txt)
            movePiecesInBoard(game,chess.Move.from_uci(txt),None)
            if txt == '1':
                break;
    
 
def movePiecesInBoard(game, move, headers=None):
        if NARRATION:
            piecesName = dict()
            piecesName['P'] = 'Pawn'
            piecesName['N'] = 'Knight'
            piecesName['B'] = 'Bishop'
            piecesName['R'] = 'Rook'
            piecesName['Q'] = 'Queen'
            piecesName['K'] = 'King'
        
        is_capture = game.board.is_capture(move)
        is_kingside_castling = game.board.is_kingside_castling(move)
        is_queenside_castling = game.board.is_queenside_castling(move)
        thisTurn = game.board.turn
        player = ''
        movingCellName = chess.SQUARE_NAMES[move.from_square]
        movingToCellName = chess.SQUARE_NAMES[move.to_square]
        if headers:
            if thisTurn == chess.BLACK:
                player = headers['Black'].split(',')[0]
            else:
                player = headers['White'].split(',')[0]
        else:
            player = move_str
        if NARRATION:
            thingToSay = ''
            if is_capture:
                movingPieceName = piecesName[str.upper((game.board.piece_at(move.from_square)).symbol())]
                movingToPieceName = piecesName[str.upper((game.board.piece_at(move.to_square)).symbol())]
                thingToSay = player + "'s" + movingPieceName + " at " + movingCellName + " captures " + movingToPieceName + " at " + movingToCellName
            elif is_kingside_castling:
                thingToSay = player + " castles kingside"
            elif is_queenside_castling:
                thingToSay = player + " castles queenside"
            else:
                movingPieceName = piecesName[str.upper((game.board.piece_at(move.from_square)).symbol())]
                if movingPieceName == "Pawn":
                    thingToSay = player + " advances " + movingCellName +" pawn to " + movingToCellName
                else:
                    thingToSay = player + " moves " + movingPieceName + " to " + movingToCellName
            threading.Thread(target=voice.say, args=(thingToSay,)).start()
        

        fromSquare = chess.SQUARE_NAMES[move.from_square]
        toSquare = chess.SQUARE_NAMES[move.to_square]
        game.makeMove(move)

        if is_capture:
            game.captureMove(game.graph.chessPositions[fromSquare], game.graph.chessPositions[toSquare])
        else:
            game.movePieceFromTo(game.graph.chessPositions[fromSquare],game.graph.chessPositions[toSquare])
        if is_kingside_castling:
            if thisTurn == chess.BLACK:
                game.movePieceFromTo(game.graph.chessPositions['h8'], game.graph.chessPositions['f8'])
            elif thisTurn == chess.WHITE:
                game.movePieceFromTo(game.graph.chessPositions['h1'], game.graph.chessPositions['f1'])
        if is_queenside_castling:
            if thisTurn == chess.BLACK:
                game.movePieceFromTo(game.graph.chessPositions['a8'], game.graph.chessPositions['d8'])
            elif thisTurn == chess.WHITE:
                game.movePieceFromTo(game.graph.chessPositions['a1'], game.graph.chessPositions['d1'])
    
if __name__ == "__main__":
    main()