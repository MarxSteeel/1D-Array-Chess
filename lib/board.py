import lib.defs as defs
from lib.movegen import MoveGenerator


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

    def sq_attacked(self, sq, side):

        def not_offboard(piece): return piece != defs.squares["offboard"]

        def same_color(piece): return defs.piece_col[piece] == side

        def knight_or_king(direction, check):
            for i in range(8):
                piece = self.pieces[sq + direction[i]]
                if not_offboard(piece) and same_color(piece):
                    is_piece = check[piece] == 1
                    if is_piece:
                        return True
            return False

        def rook_or_bishop(direction, check):
            for i in range(4):
                dir = direction[i]
                atk_sq = sq + dir
                piece = self.pieces[atk_sq]
                while not_offboard(piece):
                    if piece != defs.pieces["empty"]:
                        is_rook = check[piece] == 1
                        if same_color(piece) and is_rook:
                            return True
                        else:
                            break
                    atk_sq += dir
                    piece = self.pieces[atk_sq]

        if side == defs.colors["white"]:
            first_pawn = self.pieces[sq - 11] == defs.pieces["wp"]
            second_pawn = self.pieces[sq - 9] == defs.pieces["wp"]
        else:
            first_pawn = self.pieces[sq + 11] == defs.pieces["bp"]
            second_pawn = self.pieces[sq + 9] == defs.pieces["bp"]
        knight = knight_or_king(defs.knight_dir, defs.piece_knight)
        king = knight_or_king(defs.king_dir, defs.piece_king)
        rook = rook_or_bishop(defs.rook_dir, defs.piece_rook_queen)
        bishop = rook_or_bishop(defs.bishop_dir, defs.piece_bishop_queen)
        return first_pawn or second_pawn or knight or king or rook or bishop

    def print_sq_attacked(self, side):
        print("\n" + "Attacked: " + "\n")
        rank = defs.ranks["8"]
        while rank >= defs.ranks["1"]:
            line = str(rank + 1) + "  "
            file = defs.files["a"]
            for file in range(defs.files["h"] + 1):
                sq = defs.get_square(file, rank)
                piece = "X" if self.sq_attacked(sq, side) else "-"
                line += " " + piece + " "
            print(line)
            rank -= 1

    def generate_moves(self):
        self.move_generator.generate_moves()

    def print_move_list(self):
        i = 1
        for move in self.move_list:
            print("Move " + str(i) + ": " + self._print_move(move))
            i += 1

    def _reset(self):
        self.files, self.ranks = self._init_files_ranks()
        self.move_generator = MoveGenerator(self)
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
        self.ply = 0
        self.move_list = []
        self.move_scores = []
        self.move_list_start = [0]

    def _print_move(self, move):
        file_from = self.files[defs.from_sq(move)]
        rank_from = self.ranks[defs.from_sq(move)]
        file_to = self.files[defs.to_sq(move)]
        rank_to = self.ranks[defs.to_sq(move)]
        fromsq = defs.file_char[file_from] + defs.rank_char[rank_from]
        tosq = defs.file_char[file_to] + defs.rank_char[rank_to]
        move_str = fromsq + tosq
        promoted = defs.promoted(move) != defs.pieces["empty"]
        if promoted:
            piece_char = "q"
            is_knight = defs.piece_knight[piece_char] == 1
            is_rook = defs.piece_rook_queen[piece_char] == 1
            is_bishop = defs.piece_bishop_queen[piece_char] == 1
            if is_knight:
                piece_char = "n"
            elif is_rook and not is_bishop:
                piece_char = "r"
            elif is_bishop and not is_rook:
                piece_char = "b"
            move_str += piece_char
        return move_str

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
