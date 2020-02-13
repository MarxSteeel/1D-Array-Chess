import lib.defs as defs


class MoveMaker(object):
    def __init__(self, board):
        self.board = board

    def clear_piece(self, sq):
        board = self.board
        piece = board.pieces[sq]
        color = defs.piece_col[piece]
        t_piece_num = -1
        board.hash_piece(sq, piece)
        board.pieces[sq] = defs.pieces["empty"]
        board.material[color] -= defs.piece_val[piece]
        for i in range(board.piece_num[piece]):
            if board.p_list[defs.piece_index(piece, i)] == sq:
                t_piece_num = i
                break
        board.piece_num[piece] -= 1
        board.p_list[defs.piece_index(piece, t_piece_num)] == \
            board.p_list[defs.piece_index(piece, board.piece_num[piece])]

    def add_piece(self, sq, piece):
        board = self.board
        color = defs.piece_col[piece]
        board.hash_piece(sq, piece)
        board.pieces[sq] = piece
        board.material[color] += defs.piece_val[piece]
        board.p_list[defs.piece_index(piece, board.piece_num[piece])] = sq
        board.piece_num[piece] += 1

    def move_piece(self, fromsq, to):
        board = self.board
        piece = board.pieces[fromsq]
        board.hash_piece(fromsq, piece)
        board.pieces[fromsq] = defs.pieces["empty"]
        board.hash_piece(to, piece)
        board.pieces[to] = piece
        for i in range(board.piece_num[piece]):
            if board.p_list[defs.piece_index(piece, i)] == fromsq:
                board.p_list[defs.piece_index(piece, i)] = to
                break

    def make_move(self, move):
        board = self.board
        fromsq = defs.from_sq(move)
        to = defs.to_sq(move)
        side = board.side
        history = board.history[board.history_ply]
        history["position_key"] = board.position_key
        en_passant = (move & defs.move_flag_ep) != 0
        castle = (move & defs.move_flag_castle) != 0
        if en_passant:
            white = side == defs.colors["white"]
            self.clear_piece(to - 10) if white else self.clear_piece(to + 10)
        elif castle:
            if to == defs.squares["c1"]:
                self.move_piece(defs.squares["a1"], defs.squares["d1"])
            elif to == defs.squares["c8"]:
                self.move_piece(defs.squares["a8"], defs.squares["d8"])
            elif to == defs.squares["g1"]:
                self.move_piece(defs.squares["h1"], defs.squares["f1"])
            elif to == defs.squares["g8"]:
                self.move_piece(defs.squares["h8"], defs.squares["f8"])
        if board.en_passant != defs.squares["no_sq"]:
            board.hash_ep()
        board.hash_castle()
        history["move"] = move
        history["fifty_move"] = board.fifty_move
        history["en_passant"] = board.en_passant
        history["castle_perm"] = board.castle_permit
        board.castle_permit &= defs.castle_permission[fromsq]
        board.castle_permit &= defs.castle_permission[to]
        board.en_passant = defs.squares["no_sq"]
        board.hash_castle()
        captured = defs.captured(move)
        board.fifty_move += 1
        if captured != defs.pieces["empty"]:
            self.clear_piece(to)
            board.fifty_move = 0
        board.history_ply += 1
        board.ply += 1
        is_pawn = defs.piece_pawn[board.pieces[fromsq]] == 1
        if is_pawn:
            board.fifty_move = 0
            double_move = (move & defs.move_flag_ps) != 0
            if double_move:
                white = side == defs.colors["white"]
                if white:
                    board.en_passant = fromsq + 10
                else:
                    board.en_passant = fromsq - 10
                board.hash_ep()
        self.move_piece(fromsq, to)
        promoted_piece = defs.promoted(move)
        if promoted_piece != defs.pieces["empty"]:
            self.clear_piece(to)
            self.add_piece(to, promoted_piece)
        board.side ^= 1
        board.hash_side()
        king = defs.piece_index(defs.kings[side], 0)
        king_in_check = board.sq_attacked(board.p_list[king], board.side)
        if king_in_check:
            self.take_move()
            return False
        return True

    def take_move(self):
        board = self.board
        board.history_ply -= 1
        board.ply -= 1
        history = board.history[board.history_ply]
        move = history["move"]
        fromsq = defs.from_sq(move)
        to = defs.to_sq(move)
        if board.en_passant != defs.squares["no_sq"]:
            board.hash_ep()
        board.hash_castle()
        board.castle_permit = history["castle_perm"]
        board.en_passant = history["en_passant"]
        board.fifty_move = history["fifty_move"]
        if board.en_passant != defs.squares["no_sq"]:
            board.hash_ep()
        board.hash_castle()
        board.side ^= 1
        board.hash_side()
        en_passant = (move & defs.move_flag_ep) != 0
        castle = (move & defs.move_flag_castle) != 0
        if en_passant:
            white = board.side == defs.colors["white"]
            if white:
                self.add_piece(to - 10, defs.pieces["bp"])
            else:
                self.add_piece(to + 10, defs.pieces["wp"])
        elif castle:
            if to == defs.squares["c1"]:
                self.move_piece(defs.squares["d1"], defs.squares["a1"])
            elif to == defs.squares["c8"]:
                self.move_piece(defs.squares["d8"], defs.squares["a8"])
            elif to == defs.squares["g1"]:
                self.move_piece(defs.squares["f1"], defs.squares["h1"])
            elif to == defs.squares["g8"]:
                self.move_piece(defs.squares["f8"], defs.squares["h8"])
        self.move_piece(to, fromsq)
        captured = defs.captured(move)
        if captured != defs.pieces["empty"]:
            self.add_piece(to, captured)
        promoted = defs.promoted(move)
        if promoted != defs.pieces["empty"]:
            self.clear_piece(fromsq)
            white = defs.piece_col[promoted] == defs.colors["white"]
            piece = defs.pieces["wp"] if white else defs.pieces["bp"]
            self.add_piece(fromsq, piece)
