import lib.defs as defs
from lib.board import Board


board = Board()
print(board.files)
print(board.ranks)
print(board.pieces)
board.parse_fen(defs.start_fen)
print(board.pieces)
print(board.piece_num)
board.print_board()
