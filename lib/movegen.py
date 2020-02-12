import lib.defs as defs


class MoveGenerator(object):
    def __init__(self, board):
        self.board = board

    def move(self, fromsq, to, captured, promoted, flag):
        return fromsq | (to << 7) | (captured << 14) | (promoted << 20) | flag

    def add_capture_move(self, move):
        board = self.board
        board.move_list.append(move)
        board.move_scores.append(0)
        board.move_list_start[-1] += 1

    def add_quiet_move(self, move):
        board = self.board
        board.move_list.append(move)
        board.move_scores.append(0)
        board.move_list_start[-1] += 1

    def add_en_passant_move(self, move):
        board = self.board
        board.move_list.append(move)
        board.move_scores.append(0)
        board.move_list_start[-1] += 1

    def add_white_pawn_capture(self, fromsq, to, cap):
        if self.board.ranks[fromsq] == defs.ranks["7"]:
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["wq"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["wr"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["wb"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["wn"], 0))
        else:
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["empty"], 0))

    def add_white_pawn_move(self, fromsq, to):
        if self.board.ranks[fromsq] == defs.ranks["7"]:
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["wq"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["wr"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["wb"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["wn"], 0))
        else:
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["empty"], 0))

    def add_black_pawn_capture(self, fromsq, to, cap):
        if self.board.ranks[fromsq] == defs.ranks["2"]:
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["bq"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["br"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["bb"], 0))
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["bn"], 0))
        else:
            self.add_capture_move(self.move(fromsq, to, cap,
                                            defs.pieces["empty"], 0))

    def add_black_pawn_move(self, fromsq, to):
        if self.board.ranks[fromsq] == defs.ranks["2"]:
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["bq"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["br"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["bb"], 0))
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["bn"], 0))
        else:
            self.add_quiet_move(self.move(fromsq, to, defs.pieces["empty"],
                                          defs.pieces["empty"], 0))

    def generate_moves(self):
        board = self.board
        board.move_list_start.append(board.move_list_start[board.ply])
        empty = defs.pieces["empty"]
        if board.side == defs.colors["white"]:
            color = {"piece": defs.pieces["wp"], "sp": 10, "dp": 20,
                     "cl": 9, "cr": 11, "rank": defs.ranks["2"],
                     "other": defs.colors["black"],
                     "pawn_move": self.add_white_pawn_move,
                     "pawn_cap": self.add_white_pawn_capture,
                     "castle": [defs.castlebit["wkca"], defs.castlebit["wqca"]],
                     "squares": ["b1", "c1", "d1", "e1", "f1", "g1"],
                     "side": defs.colors["white"],
                     "non_slide": defs.white_non_slide,
                     "slide": defs.white_slide}
        elif board.side == defs.colors["black"]:
            color = {"piece": defs.pieces["bp"], "sp": -10, "dp": -20,
                     "cl": -9, "cr": -11, "rank": defs.ranks["7"],
                     "other": defs.colors["white"],
                     "pawn_move": self.add_black_pawn_move,
                     "pawn_cap": self.add_black_pawn_capture,
                     "castle": [defs.castlebit["bkca"], defs.castlebit["bqca"]],
                     "squares": ["b8", "c8", "d8", "e8", "f8", "g8"],
                     "side": defs.colors["black"],
                     "non_slide": defs.black_non_slide,
                     "slide": defs.black_slide}
        # Pawn movements
        piece_type = color["piece"]
        for piece_num in range(board.piece_num[piece_type]):
            sq = board.p_list[defs.piece_index(piece_type, piece_num)]
            simple_pawn = board.pieces[sq + color["sp"]] == empty
            if simple_pawn:
                # Simple pawn move
                color["pawn_move"](sq, sq + color["sp"])
                double_pawn = board.pieces[sq + color["dp"]] == empty
                second_rank = board.ranks[sq] == color["rank"]
                if second_rank and double_pawn:
                    # Double pawn move
                    move = self.move(sq, sq + color["dp"],
                                     defs.pieces["empty"],
                                     defs.pieces["empty"],
                                     defs.move_flag_ps)
                    self.add_quiet_move(move)
            piece = board.pieces[sq + color["cl"]]
            not_offboard = piece != defs.squares["offboard"]
            if not_offboard:
                other_color = defs.piece_col[piece] == color["other"]
                if other_color:
                    # Pawn capture left
                    color["pawn_cap"](sq, sq + color["cl"], piece)
            piece = board.pieces[sq + color["cr"]]
            not_offboard = piece != defs.squares["offboard"]
            if not_offboard:
                other_color = defs.piece_col[piece] == color["other"]
                if other_color:
                    # Pawn capture right
                    color["pawn_cap"](sq, sq + color["cr"], piece)
            if board.en_passant != defs.squares["no_sq"]:
                if (sq + color["cl"]) == board.en_passant:
                    # En_passant left
                    move = self.move(sq, sq + color["cl"],
                                     defs.pieces["empty"],
                                     defs.pieces["empty"], defs.move_flag_ep)
                    self.add_en_passant_move(move)
                if (sq + color["cr"]) == board.en_passant:
                    # En_passant right
                    move = self.move(sq, sq + color["cr"],
                                     defs.pieces["empty"],
                                     defs.pieces["empty"], defs.move_flag_ep)
                    self.add_en_passant_move(move)
        # Castling
        square_b = defs.squares[color["squares"][0]]
        square_c = defs.squares[color["squares"][1]]
        square_d = defs.squares[color["squares"][2]]
        square_e = defs.squares[color["squares"][3]]
        square_f = defs.squares[color["squares"][4]]
        square_g = defs.squares[color["squares"][5]]
        if (board.castle_permit & color["castle"][0]) != 0:
            squares_empty = board.pieces[square_f] == empty and \
                board.pieces[square_g] == empty
            if squares_empty:
                not_in_check = not board.sq_attacked(square_f, color["side"])\
                    and not board.sq_attacked(square_e, color["side"])
                if not_in_check:
                    # Quiet castle move
                    move = self.move(square_e, square_g, defs.pieces["empty"],
                                     defs.pieces["empty"],
                                     defs.move_flag_castle)
                    self.add_quiet_move(move)
        if (board.castle_permit & color["castle"][1]) != 0:
            squares_empty = board.pieces[square_b] == empty and \
                board.pieces[square_c] == empty and \
                board.pieces[square_d] == empty
            if squares_empty:
                not_in_check = not board.sq_attacked(square_d, color["side"])\
                    and not board.sq_attacked(square_e, color["side"])
                if not_in_check:
                    # Quiet castle move
                    move = self.move(square_e, square_c, defs.pieces["empty"],
                                     defs.pieces["empty"],
                                     defs.move_flag_castle)
                    self.add_quiet_move(move)
        # Non slide movements
        for piece in color["non_slide"]:
            for piece_num in range(board.piece_num[piece]):
                sq = board.p_list[defs.piece_index(piece, piece_num)]
                for i in range(defs.dir_num[piece]):
                    direction = defs.piece_dir[piece][i]
                    atk_sq = sq + direction
                    offboard = board.pieces[atk_sq] == defs.squares["offboard"]
                    empty = board.pieces[atk_sq] == defs.pieces["empty"]
                    if offboard:
                        continue
                    if not empty:
                        same_color = defs.piece_col[board.pieces[atk_sq]] \
                                     == board.side
                        if not same_color:
                            # Capture
                            captured = board.pieces[atk_sq]
                            move = self.move(sq, atk_sq, captured,
                                             defs.pieces["empty"], 0)
                            self.add_capture_move(move)
                    else:
                        # Quiet move
                        move = self.move(sq, atk_sq, defs.pieces["empty"],
                                         defs.pieces["empty"], 0)
                        self.add_quiet_move(move)
        for piece in color["slide"]:
            for piece_num in range(board.piece_num[piece]):
                sq = board.p_list[defs.piece_index(piece, piece_num)]
                for i in range(defs.dir_num[piece]):
                    direction = defs.piece_dir[piece][i]
                    atk_sq = sq + direction
                    offboard = board.pieces[atk_sq] == defs.squares["offboard"]
                    empty = board.pieces[atk_sq] == defs.pieces["empty"]
                    while not offboard:
                        if not empty:
                            same_color = defs.piece_col[board.pieces[atk_sq]] \
                                         == board.side
                            if not same_color:
                                # Capture
                                captured = board.pieces[atk_sq]
                                move = self.move(sq, atk_sq, captured,
                                                 defs.pieces["empty"], 0)
                                self.add_capture_move(move)
                            break
                        # Quiet move
                        move = self.move(sq, atk_sq, defs.pieces["empty"],
                                         defs.pieces["empty"], 0)
                        self.add_quiet_move(move)
                        atk_sq += direction
