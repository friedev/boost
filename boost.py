# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

# TODO core features
# Basic pathfinding to ensure valid movement (A*)
# Capturing
# Victory conditions
# Dragons (symmetric placement)
#   Random choice from worklist
#   Place on one half of the map
#   Mirror each placement

# TODO stretch goals
# Other game modes
#   Don't assume default board parameters
# More players
#   Need to make turn order fancier
#   Support alliances?
# Basic AI
#   Could do static eval based on piece counts
#   Might want to cache pieces dict?
# New piece types
#   Walls (for scenarios)
#   New playable pieces (optionally enabled)
# Tactical puzzles
# Consider adding color:
# https://stackoverflow.com/questions/37340049/how-do-i-print-colored-output-to-the-terminal-in-python

import sys
from enum import Enum


DEFAULT_BOARD = """
P P P P . P P P P
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
p p p p . p p p p
"""

DEFAULT_WIDTH = 9
DEFAULT_HEIGHT = 9
MAX_TOWERS = 2

SOLO = False


def distance(row1, col1, row2, col2):
    # Manhattan distance
    return abs(row2 - row1) + abs(col2 - col1)


def cell_distance(cell1, cell2):
    return distance(cell1.row, cell1.col, cell2.row, cell2.col)


class Cell:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            self.col = ord(args[0][0].upper()) - 65
            self.row = DEFAULT_HEIGHT - int(args[0][1])
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            self.row = args[0]
            self.col = args[1]
        else:
            raise ValueError(f'Invalid arguments: {args}')

    def __str__(self):
        return f'{chr(self.col + 65)}{str(DEFAULT_HEIGHT - self.row)}'

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.row == other.row and self.col == other.col
        return False

    @property
    def neighbors(self):
        return [Cell(self.row - 1, self.col),
                Cell(self.row + 1, self.col),
                Cell(self.row, self.col - 1),
                Cell(self.row, self.col + 1)]


class PieceType(Enum):
    DRAGON = 'Dragon'
    PAWN = 'Pawn'
    KNIGHT = 'Knight'
    TOWER = 'Tower'


class Owner(Enum):
    DRAGON = 'Dragon'
    TOP = 'Top'
    BOTTOM = 'Bottom'


class Piece:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 1:
            piece_type = args[0].lower()
            if piece_type == 'd':
                self.owner = Owner.DRAGON
                self.piece_type = PieceType.DRAGON
            else:
                self.owner = Owner.TOP if args[0].isupper() else Owner.BOTTOM
                if piece_type == 'p':
                    self.piece_type = PieceType.PAWN
                elif piece_type == 'k':
                    self.piece_type = PieceType.PAWN
                elif piece_type == 't':
                    self.piece_type = PieceType.PAWN
                else:
                    raise ValueError(f'Invalid piece type: {piece_type}')
        elif len(args) == 2 and isinstance(args[0], Owner) and isinstance(args[1], PieceType):
            self.owner = args[0]
            self.piece_type = args[1]
        else:
            raise ValueError(f'Invalid arguments: {args}')

    def __str__(self):
        if self.piece_type == PieceType.DRAGON:
            return 'D'
        if self.piece_type == PieceType.PAWN:
            return 'P' if self.owner == Owner.TOP else 'p'
        if self.piece_type == PieceType.KNIGHT:
            return 'K' if self.owner == Owner.TOP else 'k'
        if self.piece_type == PieceType.TOWER:
            return 'T' if self.owner == Owner.TOP else 't'
        # If the piece type is not valid, throw a ValueError
        raise ValueError(f'Invalid piece type: {self.piece_type}')

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.owner == other.owner and self.piece_type == other.piece_type
        return False

    def __hash__(self):
        return hash((self.owner, self.piece_type))

    @property
    def name(self):
        return self.piece_type.value


class Move:
    def __init__(self, *args):
        # TODO better input sanitization/parsing/recovery
        # ew dry violation
        if len(args) == 4 and\
                isinstance(args[0], int) and\
                isinstance(args[1], int) and\
                isinstance(args[2], int) and\
                isinstance(args[3], int):
            self.start = Cell(args[0], args[1])
            self.end = Cell(args[2], args[3])
        elif len(args) == 2 and isinstance(args[0], Cell) and isinstance(args[1], Cell):
            self.start = args[0]
            self.end = args[1]
        elif len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 4:
            self.start = Cell(args[0][:2])
            self.end = Cell(args[0][2:])
        elif len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 2:
            self.start = Cell(args[0])
            self.end = Cell(args[0])
        else:
            raise ValueError(f'Invalid arguments: {args}')

    def __str__(self):
        return str(self.start) + str(self.end)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start == other.start and self.end == other.end
        return False

    @property
    def distance(self):
        return cell_distance(self.start, self.end)


class Board:
    def __init__(self, *args):
        self.board = Board.empty()
        if len(args) == 1 and isinstance(args[0], str):
            self.load(args[0])

    @staticmethod
    def empty():
        return [[None for row in range(DEFAULT_HEIGHT)] for col in range(DEFAULT_WIDTH)]

    def clear(self):
        self.board = Board.empty()

    def __str__(self):
        string = ''
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col]:
                    string += self.board[row][col].name
                else:
                    string += '.'
                string += ' '
            string += '\n'
        # Slice out trailing newline
        return string[:-1]

    @property
    def labeled(self):
        string = ''
        for row in range(len(self.board)):
            string += f"{len(self.board) - row} "
            for col in range(len(self.board[row])):
                if self.board[row][col]:
                    string += str(self.board[row][col])
                else:
                    string += '.'
                string += ' '
            string += '\n'
        string += "  "
        for col in range(len(self.board[0])):
            string += f"{chr(col + 65)} "
        return string

    def load(self, string):
        row, col = 0, 0
        for line in string.splitlines():
            for char in line:
                if char != ' ':
                    if char == '.':
                        self.board[row][col] = None
                    else:
                        self.board[row][col] = Piece(char)
                    col += 1
            # Ignore blank lines
            if col > 0:
                row += 1
                col = 0

    def in_bounds(self, cell):
        return cell.row >= 0 and\
                cell.row < len(self.board) and\
                cell.col >= 0 and\
                cell.col < len(self.board[cell.row])

    def get_piece(self, cell):
        if not self.in_bounds(cell):
            return None
        return self.board[cell.row][cell.col]

    def count_all_pieces(self):
        pieces = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    if piece in pieces:
                        pieces[piece] += 1
                    else:
                        pieces[piece] = 1
        return pieces

    def count_pieces(self, owner, piece_type):
        count = 0
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece and\
                        (not owner or piece.owner == owner) and\
                        (not piece_type or piece.piece_type == piece_type):
                    count += 1
        return count

    def get_boost(self, cell):
        boost = 1
        for neighbor in cell.neighbors:
            if self.get_piece(neighbor):
                boost += 1
        return boost

    def path_exists(self, move):
        # TODO implement some sort of graph search
        # Later, for listing possible moves in GUI, add find_all_paths(cell, distance)
        boost = self.get_boost(move.start)
        return True

    def can_move_dragon(self, cell, owner):
        assert owner != Owner.DRAGON
        assert self.get_piece(cell).piece_type == PieceType.DRAGON
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if neighbor_piece and neighbor_piece.owner == owner:
                return True
        return False

    def can_build_tower(self, cell, owner):
        if self.get_piece(cell):
            return False
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if not neighbor_piece or neighbor_piece.owner != owner:
                return False
        return self.count_pieces(owner, PieceType.TOWER) < MAX_TOWERS

    def can_promote_knight(self, cell, owner):
        piece = self.get_piece(cell)
        if not piece or piece.owner != owner or piece.piece_type != PieceType.PAWN:
            return False
        pieces = self.count_all_pieces()
        knight = Piece(owner, PieceType.KNIGHT)
        tower = Piece(owner, PieceType.TOWER)
        if knight in pieces and tower in pieces and pieces[knight] >= pieces[tower]:
            return False
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if neighbor_piece and\
                    neighbor_piece.owner == owner and\
                    neighbor_piece.piece_type == PieceType.TOWER:
                return True
        return False

    def get_move_error(self, move, owner):
        piece = self.get_piece(move.start)
        destination = self.get_piece(move.end)
        boost = self.get_boost(move.start)
        error = None
        if move.start == move.end:
            if self.can_build_tower(move.start, owner):
                return None
            if self.can_promote_knight(move.start, owner):
                return None
            return 'You cannot build a tower here nor promote a pawn to a knight here.'
        if not piece:
            error = f'There is no piece at {move.start} to move.'
        elif piece.piece_type == PieceType.DRAGON and not self.can_move_dragon(move.start, owner):
            error = f'To move the {piece.name} at {move.start}, you must have an adjacent piece.'
        elif piece.owner != owner:
            error = f'You are not the owner of the {piece.name} at {move.start}.'
        elif piece.piece_type == PieceType.TOWER:
            error = 'Towers cannot move.'
        elif move.distance != boost:
            error = f'You must move this piece exactly {boost} cell(s).'
        elif not self.in_bounds(move.end):
            error = f'{move.end} is out of bounds.'
        elif destination and piece.piece_type != PieceType.KNIGHT:
            error = f'A {piece.name} cannot capture pieces directly.'
        elif destination and destination.owner == owner:
            error = 'You cannot capture your own piece.'
        elif destination and destination.piece_type == PieceType.DRAGON:
            error = 'Dragons cannot be captured.'
        return error

    def is_valid(self, move, owner):
        return not self.get_move_error(move, owner)

    def move(self, move, owner):
        # TODO maybe do some validation?
        # Don't necessarily want to call get_move_error again but it could be done
        if move.start == move.end:
            piece = self.get_piece(move.start)
            if not piece:
                # Build tower
                self.board[move.start.row][move.start.col] = Piece(owner, PieceType.TOWER)
            else:
                # Promote knight
                self.board[move.start.row][move.start.col] = Piece(owner, PieceType.KNIGHT)
        piece = self.board[move.start.row][move.start.col]
        self.board[move.start.row][move.start.col] = None
        self.board[move.end.row][move.end.col] = piece
        # TODO if pawn or dragon, check for captures


def main():
    board = Board(DEFAULT_BOARD)
    turn = Owner.BOTTOM
    error = None
    while True:
        print(board.labeled)
        if error:
            print(error)
            error = None
        move_input = input(f"{turn.value} Player's Move: ")
        if move_input == 'exit':
            sys.exit(0)
        try:
            move = Move(move_input)
        except ValueError:
            error = 'Bad move format. Moves should be given in chess notation.\n'\
                    + 'e.g. "a1b2" to move from A1 to B2.'
        else:
            error = board.get_move_error(move, turn)
            if not error:
                board.move(move, turn)
                if not SOLO:
                    turn = Owner.TOP if turn == Owner.BOTTOM else Owner.BOTTOM
        print()


if __name__ == '__main__':
    main()
