import lib.defs as defs
from lib.board import Board


board = Board()
print(board.files)
print(board.ranks)
print(board.pieces)
board.parse_fen(defs.start_fen)
# print(board.piece_num)
print(not board.sq_attacked(71, defs.colors["black"]))
board.print_sq_attacked(defs.colors["white"])
board.print_board()
print(board.position_key)
print(board.check_board())
board.generate_moves()
print(board.move_list)
board.print_move_list()
board.make_move(board.move_list[0])
board.print_board()
print(board.history[0])
print(board.check_board())
