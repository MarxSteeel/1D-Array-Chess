import random

background = {"grey": '\033[48;5;242m', "black": '\033[48;5;0m'}

pieces = {"empty": 0, "wp": 1, "wn": 2, "wb": 3,
                      "wr": 4, "wq": 5, "wk": 6,
                      "bp": 7, "bn": 8, "bb": 9,
                      "br": 10, "bq": 11, "bk": 12}

brd_sq_num = 120

files = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5,
                         "g": 6, "h": 7, "none": 8}

ranks = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4,
                 "6": 5, "7": 6, "8": 7, "none": 8}

colors = {"white": 0, "black": 1, "both": 2}

castlebit = {"wkca": 1, "wqca": 2, "bkca": 4, "bqca": 8}

squares = {"a1": 21, "b1": 22, "c1": 23, "d1": 24,
                     "e1": 25, "f1": 26, "g1": 27, "h1": 28,
                     "a8": 91, "b8": 92, "c8": 93, "d8": 94,
                     "e8": 95, "f8": 96, "g8": 97, "h8": 98,
                     "no_sq": 99, "offboard": 100}

fen_dict = {"P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6,
            "p": 7, "n": 8, "b": 9, "r": 10, "q": 11, "k": 12}

symbols = {1: "♟", 2: "♞", 3: "♝", 4: "♜", 5: "♛", 6: "♚",
           7: "♙", 8: "♘", 9: "♗", 10: "♖", 11: "♕", 12: "♔"}

start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

pce_char = ".PNBRQKpnbrqk"
side_char = "wb-"
rank_char = "12345678"
file_char = "abcdefgh"

max_game_moves = 2048
max_position_moves = 256
max_depth = 64

piece_val = [0, 100, 325, 325, 550, 1000, 50000,
             100, 325, 325, 550, 1000, 50000]
piece_big = [0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1]
piece_maj = [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1]
piece_min = [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0]
piece_col = [colors["both"], colors["white"], colors["white"], colors["white"],
             colors["white"], colors["white"], colors["white"],
             colors["black"], colors["black"], colors["black"],
             colors["black"], colors["black"], colors["black"]]

piece_pawn = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
piece_knight = [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
piece_king = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
piece_rook_queen = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0]
piece_bishop_queen = [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0]
piece_slides = [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0]

knight_dir = [-8, -19, -21, -12, 8, 19, 21, 12]
rook_dir = [-1, -10, 1, 10]
bishop_dir = [-9, -11, 9, 11]
king_dir = [-1, -10, 1, 10, -9, -11, 9, 11]
dir_num = [0, 0, 8, 4, 4, 8, 8, 0, 8, 4, 4, 8, 8]
piece_dir = [0, 0, knight_dir, bishop_dir, rook_dir, king_dir, king_dir,
             0, knight_dir, bishop_dir, rook_dir, king_dir, king_dir]

white_non_slide = [pieces["wn"], pieces["wk"]]
black_non_slide = [pieces["bn"], pieces["bk"]]
white_slide = [pieces["wb"], pieces["wr"], pieces["wq"]]
black_slide = [pieces["bb"], pieces["br"], pieces["bq"]]


def get_square(file, rank): return (file + 21) + rank * 10


def piece_index(piece, piece_num): return piece * 10 + piece_num


def rand_32():
    return ((random.randrange(256) << 23) | (random.randrange(256) << 16) |
            (random.randrange(256) << 8) | random.randrange(256))


def init_hash_keys():
    piece_keys = []
    for i in range(14*120):
        piece_keys.append(rand_32())
    side_key = rand_32()
    castle_keys = []
    for i in range(16):
        castle_keys.append(rand_32())
    return [piece_keys, side_key, castle_keys]


piece_keys, side_key, castle_keys = init_hash_keys()


def init_sq_120to64():
    sq_120to64 = []
    sq_64to120 = []
    sq64 = 0
    for i in range(brd_sq_num):
        sq_120to64.append(65)
    for i in range(64):
        sq_64to120.append(120)
    for rank in range(ranks["8"] + 1):
        for file in range(files["h"] + 1):
            sq = get_square(file, rank)
            sq_64to120[sq64] = sq
            sq_120to64[sq] = sq64
            sq64 += 1
    return [sq_120to64, sq_64to120]


sq_120to64, sq_64to120 = init_sq_120to64()

move_flag_ep = 0x40000
move_flag_ps = 0x80000
move_flag_castle = 0x1000000
move_flag_captured = 0x7C000
move_flag_prom = 0xF00000


def sq64(sq120): return sq_120to64[sq120]


def sq120(sq64): return sq_64to120[sq64]


def from_sq(move): return move & 0x7F


def to_sq(move): return (move >> 7) & 0x7F


def captured(move): return (move >> 14) & 0xF


def promoted(move): return (move >> 20) & 0xF
