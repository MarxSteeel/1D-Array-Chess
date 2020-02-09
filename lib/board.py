import lib.defs as defs


class Board(object):
    def __init__(self):
        self._reset()
        self.side = defs.colors["white"]

    def print_board(self):
        print("\n" + "Board: " + "\n")
        rank = defs.ranks["8"]
        while rank >= defs.ranks["1"]:
            line = str(rank + 1) + "  "
            file = defs.files["a"]
            for file in range(defs.files["h"] + 1):
                sq = defs.get_square(file, rank)
                piece = self.pieces[sq]
                if (file + rank) % 2 == 0 or (file + rank) == 0:
                    background = defs.background["black"]
                else:
                    background = defs.background["grey"]
                if piece != 0:
                    line += background + " " + defs.symbols[piece] + " " + \
                                       defs.background["black"]
                else:
                    line += background + "   " + defs.background["black"]
            print(line)
            rank -= 1
        print("   " + " a " + " b " + " c " + " d " +
                      " e " + " f " + " g " + " h ")

    def parse_fen(self, fen):
        self._reset()
        fen_list = fen.split("/")[0:-1] + fen.split("/")[-1].split(" ")
        fen_pieces = fen_list[0:8]
        fen_others = {"color": fen_list[8], "castle": fen_list[9],
                      "en_passant": fen_list[10], "halfmove": fen_list[11],
                      "fullmove": fen_list[12]}
        rank = defs.ranks["8"]
        for i in range(len(fen_pieces)):
            line = fen_pieces[i]
            file = defs.files["a"]
            j = 0
            while j < len(line):
                spot = line[j]
                if spot.isdigit():
                    j += int(spot)
                    file += int(spot)
                elif spot in defs.fen_dict:
                    piece = defs.fen_dict[spot]
                    sq64 = rank * 8 + file
                    sq120 = defs.sq120(sq64)
                    self.pieces[sq120] = piece
                    j += 1
                    file += 1
                else:
                    print("FEN Error")
                    return
            rank -= 1
        if fen_others["color"] == "w":
            self.side = defs.colors["white"]
        else:
            self.side = defs.colors["black"]
        if "K" in fen_others["castle"]:
            self.castle_permit |= defs.castlebit["wkca"]
        if "Q" in fen_others["castle"]:
            self.castle_permit |= defs.castlebit["wqca"]
        if "k" in fen_others["castle"]:
            self.castle_permit |= defs.castlebit["bkca"]
        if "q" in fen_others["castle"]:
            self.castle_permit |= defs.castlebit["bqca"]
        if fen_others["en_passant"] != "-":
            file = defs.files[fen_others["en_passant"][0]]
            rank = defs.ranks[fen_others["en_passant"][1]]
            self.en_passant = defs.get_square(file, rank)
        self.position_key = self._generate_position_key()
        self._update_material()

    def _reset(self):
        self.files, self.ranks = self._init_files_ranks()
        self.pieces = [defs.squares["offboard"]] * defs.brd_sq_num
        for i in range(64):
            self.pieces[defs.sq120(i)] = defs.pieces["empty"]
        self.p_list = [defs.pieces["empty"]] * 14 * 10
        self.piece_num = [0] * 13
        self.side = defs.colors["both"]
        self.fifty_move = 0
        self.his_ply = 0
        self.ply = 0
        self.en_passant = defs.squares["no_sq"]
        self.castle_permit = 0
        self.material = [0, 0]
        self.position_key = self._generate_position_key()

    def _init_files_ranks(self):
        files_board = []
        ranks_board = []
        for i in range(defs.brd_sq_num):
            files_board.append(defs.squares["offboard"])
            ranks_board.append(defs.squares["offboard"])
        rank = defs.ranks["1"]
        for rank in range(defs.ranks["8"] + 1):
            file = defs.files["a"]
            for file in range(defs.files["h"] + 1):
                sq = defs.get_square(file, rank)
                files_board[sq] = file
                ranks_board[sq] = rank
        return [files_board, ranks_board]

    def _generate_position_key(self):
        final_key = 0
        for sq in range(defs.brd_sq_num):
            piece = self.pieces[sq]
            empty = defs.pieces["empty"]
            offboard = defs.squares["offboard"]
            if piece != empty and piece != offboard:
                final_key ^= defs.piece_keys[(piece * 120) + sq]
        if self.side == defs.colors["white"]:
            final_key ^= defs.side_key
        if self.en_passant != defs.squares["no_sq"]:
            final_key ^= defs.piece_keys[self.en_passant]
        final_key ^= defs.castle_keys[self.castle_permit]
        return final_key

    def _update_material(self):
        for i in range(defs.brd_sq_num):
            piece = self.pieces[i]
            empty = defs.pieces["empty"]
            offboard = defs.squares["offboard"]
            if piece != empty and piece != offboard:
                color = defs.piece_col[piece]
                self.material[color] += defs.piece_val[piece]
                self.p_list[defs.piece_index(piece, self.piece_num[piece])] = i
                self.piece_num[piece] += 1