# pylint: disable=missing-docstring,missing-module-docstring,missing-class-docstring,missing-function-docstring

# TODO stretch goals
# Choose ruleset at the start of a game
# Basic AI
#   Could do static eval based on piece counts
#   Might want to cache pieces dict?
# Game rules
# Debug powers (ignore movement rules)
# New piece types
#   Refactor pieces; give each properties rather than hardcoding based on type
#   Walls (for scenarios)
#   New playable pieces (optionally enabled)
# Cache piece counts
# Export move history and/or board history
# CLI arguments to change game options (e.g. board, solo)
# Better error messages
# Docstrings for all functions/classes
# Generalize system to allow for any arbitrary rulesets (e.g. chess)

import sys
import math
import random
import os
from enum import Enum

COLOR = False
try:
    from termcolor import colored
except ImportError:
    COLOR = False

SOLO_BOARD = """
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
"""

P2_BOARD = """
P2 P2 P2 P2 .  P2 P2 P2 P2
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
"""

P2_BOARD_MINI = """
.  .  .  P2 P2 P2 P2
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
P1 P1 P1 P1 .  .  .
"""

P2_BOARD_QUICKSTART = """
.  .  P2 .  .  .  P2 .  .
.  P2 T2 P2 .  P2 T2 P2 .
.  .  P2 .  .  .  P2 .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  P1 .  .  .  P1 .  .
.  P1 T1 P1 .  P1 T1 P1 .
.  .  P1 .  .  .  P1 .  .
"""

P3_BOARD = """
P2 P2 P2 P2 .  P3 P3 P3 P3
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
"""

P4_BOARD = """
P2 P2 P2 P2 .  P4 P4 P4 P4
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P4
P2 .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  .
P1 .  .  .  .  .  .  .  P3
P1 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P3 P3 P3 P3
"""

P4_BOARD_MINIMAL = """
P2 .  .  .  .  P3 P3 P3 P3
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
P1 P1 P1 P1 .  .  .  .  P4
"""

class Ruleset:
    def __init__(self, board_string, width, height, players, dragons):
        assert board_string
        assert width >= 1
        assert height >= 1
        assert players >= 1
        assert dragons >= 0
        self.board_string = board_string
        self.width = width
        self.height = height
        self.players = players
        self.dragons = dragons

    @property
    def owners(self):
        return self.players + 1

    def create_board(self):
        return Board(self.width, self.height, self.board_string, self.dragons)

    def create_game(self):
        return Game(self.create_board(), self.players)

class Rulesets(Enum):
    P2 = Ruleset(P2_BOARD, 9, 9, 2, 7)
    SOLO = Ruleset(SOLO_BOARD, 9, 9, 1, 7)
    P2_DRAGONLESS = Ruleset(P2_BOARD, 9, 9, 2, 0)
    P2_MINI = Ruleset(P2_BOARD_MINI, 7, 7, 2, 7)
    P2_MINI_DRAGONLESS = Ruleset(P2_BOARD_MINI, 7, 7, 2, 0)
    P2_QUICKSTART = Ruleset(P2_BOARD_QUICKSTART, 9, 9, 2, 7)
    P3 = Ruleset(P3_BOARD, 9, 9, 3, 7)
    P4 = Ruleset(P4_BOARD, 9, 9, 4, 7)
    P4_MINIMAL = Ruleset(P4_BOARD_MINIMAL, 9, 9, 4, 7)

DEFAULT_RULESET = Rulesets.P2.value

EMPTY_CELL_SHORT = '.'
EMPTY_CELL_LONG = '. '

DRAGON_OWNER = 0
OWNER_COLORS = ['green', 'red', 'blue', 'yellow', 'magenta', 'cyan', 'white']

MAX_TOWERS = 2
KNIGHTS_PER_TOWER = 1
DRAGONS = 7
MIN_PIECES = 4

TOWER_VICTORY = True

CLEAR = True


def distance(row1, col1, row2, col2):
    # Manhattan distance
    return abs(row2 - row1) + abs(col2 - col1)


def cell_distance(cell1, cell2):
    return distance(cell1.row, cell1.col, cell2.row, cell2.col)


# A generic list-based priority queue implementation
class PriorityQueue:
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    @property
    def is_empty(self):
        return len(self.queue) == 0

    def insert(self, data):
        self.queue.append(data)

    def delete(self):
        if self.is_empty:
            raise IndexError
        best = 0
        for i in range(len(self.queue)):
            if self.queue[i] < self.queue[best]:
                best = i
        item = self.queue[best]
        del self.queue[best]
        return item


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

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

class PieceType:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

class PieceTypes(Enum):
    DRAGON = PieceType('Dragon', 'D')
    PAWN = PieceType('Pawn', 'P')
    KNIGHT = PieceType('Knight', 'K')
    TOWER = PieceType('Tower', 'T')


class Piece:
    def __init__(self, owner, piece_type):
        # assert isinstance(owner, int)
        # assert owner >= 0
        # assert piece_type in PieceTypes
        # assert (owner == DRAGON_OWNER) == (piece_type == PieceTypes.DRAGON)
        self.owner = owner
        self.piece_type = piece_type

    def __str__(self):
        return str(self.piece_type.value.symbol) + str(self.owner)

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.owner == other.owner and self.piece_type == other.piece_type
        return False

    def __hash__(self):
        return hash((self.owner, self.piece_type))

    @property
    def name(self):
        return self.piece_type.value.name

    @property
    def symbol(self):
        return self.piece_type.value.symbol

    @property
    def color(self):
        return OWNER_COLORS[self.owner]

    @property
    def valid(self):
        return self.owner >= 0 and\
                self.piece_type in PieceTypes\
                and (self.owner == DRAGON_OWNER) == (self.piece_type == PieceTypes.DRAGON)

    @staticmethod
    def parse(string):
        for piece_type in PieceTypes:
            if piece_type.value.symbol == string[0]:
                return Piece(int(string[1]), piece_type)
        return None


class Move:
    def __init__(self, start, end=None):
        self.start = start
        self.end = end if end else start

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start == other.start and self.end == other.end
        return False

    @property
    def distance(self):
        return cell_distance(self.start, self.end)


class PathVertex:
    def __init__(self, cell, path, heuristic):
        self.cell = cell
        self.path = path
        self.heuristic = heuristic

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.heuristic == other.heuristic


class Board:
    def __init__(self, width, height, string='', dragons=0):
        self.board = Board.empty(width, height)
        self.load(string)
        self.place_dragons(dragons)

    @property
    def width(self):
        return len(self.board[0])

    @property
    def height(self):
        return len(self.board)

    @staticmethod
    def empty(width, height):
        return [[None for row in range(height)] for col in range(width)]

    def __str__(self):
        string = ''
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col]:
                    string += str(self.board[row][col])
                else:
                    string += EMPTY_CELL_LONG
                string += ' '
            string += '\n'
        # Slice out trailing newline
        return string[:-1]

    @property
    def cell_width(self):
        return 2 if COLOR or self.owners <= 3 else 3

    @property
    def pretty(self):
        file_labels = '  '
        for col in range(len(self.board[0])):
            file_labels += f'{chr(col + 65)}' + (self.cell_width - 1) * ' '
        string = file_labels + '\n'
        horizontal_border = '─' * (self.cell_width * len(self.board[0]) - 1)
        string += f" ┌{horizontal_border}┐\n"
        for row in range(len(self.board)):
            row_string = f'{len(self.board) - row}'
            string += row_string + '│'
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    if COLOR:
                        string += colored(piece.symbol.upper(), piece.color)
                    else:
                        string += self.format_piece(piece)
                else:
                    if self.cell_width == 2:
                        string += EMPTY_CELL_SHORT
                    else:
                        string += EMPTY_CELL_LONG
                if col < len(self.board[row]) - 1:
                    string += ' '
                else:
                    string += '│'
            string += row_string + '\n'
        string += f" └{horizontal_border}┘\n"
        string += file_labels
        return string

    @property
    def cells(self):
        cells = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                cells.append(Cell(row, col))
        return cells

    @property
    def tower_cells(self):
        cells = []
        for row in range(1, len(self.board) - 1):
            for col in range(1, len(self.board[row]) - 1):
                cells.append(Cell(row, col))
        return cells

    @property
    def pieces(self):
        pieces = {}
        for cell in self.cells:
            piece = self.get_piece(cell)
            if piece:
                if piece in pieces:
                    pieces[piece] += 1
                else:
                    pieces[piece] = 1
        return pieces

    def parse_cell(self, string):
        row_string = string[0]
        col_string = string[1]
        row = self.height - int(col_string)
        col = ord(row_string.upper()) - 65
        return Cell(row, col)

    def format_cell(self, cell):
        return f'{chr(cell.col + 65)}{str(self.height - cell.row)}'

    def parse_move(self, string):
        start = self.parse_cell(string[0:2])
        end = start
        if len(string) == 4:
            end = self.parse_cell(string[2:4])
        return Move(start, end)

    def format_move(self, move):
        return self.format_cell(move.start) + self.format_cell(move.end)

    def format_piece(self, piece):
        if self.owners > 3:
            return str(piece)
        symbol = piece.piece_type.value.symbol
        return symbol.lower() if piece.owner == 1 else symbol.upper()

    def load(self, string):
        row, col = 0, 0
        self.owners = 0
        for line in string.splitlines():
            if row < len(self.board):
                for (piece_type_string, owner_string) in zip(line[0::], line[1::]):
                    if col < len(self.board[row]):
                        piece_string = piece_type_string + owner_string
                        piece = Piece.parse(piece_string)
                        self.board[row][col] = piece
                        if piece:
                            if piece.owner > self.owners:
                                self.owners = piece.owner
                        if piece or piece_string == EMPTY_CELL_LONG:
                            col += 1
            # Ignore blank lines
            if col > 0:
                row += 1
                col = 0
        self.owners += 1

    def place_dragons(self, dragons):
        assert dragons >= 0
        if dragons == 0:
            return
        middle_row = math.floor(self.height / 2)
        middle_col = math.floor(self.width / 2)
        available_cells = []
        for row in range(middle_row):
            col_range = middle_col - 1 if row == middle_row else self.width
            for col in range(col_range):
                if not self.board[row][col]:
                    available_cells.append(Cell(row, col))
        remaining_dragons = dragons
        # To place an odd number of dragons, we have to place one in the middle,
        # since it's the only non-mirrored cell
        dragon = Piece(DRAGON_OWNER, PieceTypes.DRAGON)
        if dragons % 2 != 0:
            if self.board[middle_row][middle_col]:
                raise ValueError(\
                        'Cannot place an odd number of dragons on this board' +\
                        '(center must be unoccupied)')
            self.board[middle_row][middle_col] = dragon
            remaining_dragons -= 1
        while remaining_dragons > 0:
            cell = random.choice(available_cells)
            available_cells.remove(cell)
            mirror_row = self.height - cell.row - 1
            mirror_col = self.width - cell.col - 1
            if not self.board[mirror_row][mirror_col]:
                self.set_piece(cell, dragon)
                self.board[mirror_row][mirror_col] = dragon
                remaining_dragons -= 2

    def in_bounds(self, cell):
        assert cell
        return cell.row >= 0 and\
                cell.row < len(self.board) and\
                cell.col >= 0 and\
                cell.col < len(self.board[cell.row])

    def get_piece(self, cell):
        if not self.in_bounds(cell):
            return None
        return self.board[cell.row][cell.col]

    def set_piece(self, cell, piece):
        if self.in_bounds(cell):
            self.board[cell.row][cell.col] = piece

    def get_boost(self, cell):
        boost = 1
        for neighbor in cell.neighbors:
            if self.get_piece(neighbor):
                boost += 1
        return boost

    def path_exists(self, move):
        # A* with Manhattan distance heuristic (cell_distance)
        boost = self.get_boost(move.start)
        worklist = PriorityQueue()
        worklist.insert(PathVertex(move.start, [], cell_distance(move.start, move.end)))

        while not worklist.is_empty:
            workitem = worklist.delete()

            if len(workitem.path) > boost:
                return False

            if len(workitem.path) == boost and workitem.cell == move.end:
                return True

            for neighbor in workitem.cell.neighbors:
                piece = self.get_piece(neighbor)
                if (not piece or neighbor == move.end) and not neighbor in workitem.path:
                    worklist.insert(PathVertex(neighbor,\
                            workitem.path + [neighbor],\
                            len(workitem.path) + 1 + cell_distance(neighbor, move.end)))

        return False

    def can_move_dragon(self, cell, owner):
        assert owner != DRAGON_OWNER
        assert self.get_piece(cell).piece_type == PieceTypes.DRAGON
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
        owner_towers = self.pieces.get(Piece(owner, PieceTypes.TOWER), 0)
        return owner_towers < MAX_TOWERS

    def can_promote_knight(self, cell, owner):
        piece = self.get_piece(cell)
        if not piece or piece.owner != owner or piece.piece_type != PieceTypes.PAWN:
            return False
        pieces = self.pieces
        knight = Piece(owner, PieceTypes.KNIGHT)
        tower = Piece(owner, PieceTypes.TOWER)
        if knight in pieces and\
                tower in pieces\
                and pieces[knight] >= pieces[tower] * KNIGHTS_PER_TOWER:
            return False
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if neighbor_piece and\
                    neighbor_piece.owner == owner and\
                    neighbor_piece.piece_type == PieceTypes.TOWER:
                return True
        return False

    def get_move_error(self, move, owner):
        piece = self.get_piece(move.start)
        destination = self.get_piece(move.end)
        boost = self.get_boost(move.start)
        error = ''
        if move.start == move.end:
            if self.can_build_tower(move.start, owner):
                return ''
            if self.can_promote_knight(move.start, owner):
                return ''
            return 'You cannot build a tower here nor promote a pawn to a knight here.'
        if not piece:
            error = f'There is no piece at {self.format_cell(move.start)} to move.'
        elif piece.piece_type == PieceTypes.DRAGON and\
                not self.can_move_dragon(move.start, owner):
            error = f'To move the {piece.name} at {self.format_cell(move.start)}, ' +\
                    'you must have an adjacent piece.'
        elif piece.owner != owner and piece.owner != DRAGON_OWNER:
            error = f'You are not the owner of the {piece.name} at {self.format_cell(move.start)}.'
        elif piece.piece_type == PieceTypes.TOWER:
            error = 'Towers cannot move.'
        elif not self.path_exists(move):
            error = f'You must move this piece exactly {boost} cell(s).'
        elif not self.in_bounds(move.end):
            error = f'{self.format_cell(move.end)} is out of bounds.'
        elif destination and piece.piece_type != PieceTypes.KNIGHT:
            error = f'A {piece.name} cannot capture pieces directly.'
        elif destination and destination.owner == owner:
            error = 'You cannot capture your own piece.'
        elif destination and destination.piece_type == PieceTypes.DRAGON:
            error = 'Dragons cannot be captured.'
        return error

    def is_valid(self, move, owner):
        return not self.get_move_error(move, owner)

    def capture(self, cell, owner):
        # Processes captures made by the piece moved to the given cell by the given owner
        piece = self.get_piece(cell)
        assert piece
        assert piece.piece_type == PieceTypes.PAWN or piece.piece_type == PieceTypes.DRAGON
        captures = 0
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if neighbor_piece\
                    and neighbor_piece.owner != owner\
                    and neighbor_piece.owner != DRAGON_OWNER:
                flank = Cell(neighbor.row + (neighbor.row - cell.row),\
                        neighbor.col + (neighbor.col - cell.col))
                flanking_piece = self.get_piece(flank)
                # TODO check capture rules in >2 player game
                # e.g. Can P1 capture a P2 piece that's flanked by a P3 piece?
                #      Or does the P2 piece need to be flanked by a P1 piece or dragon?
                if flanking_piece and flanking_piece.owner != neighbor_piece.owner:
                    self.set_piece(neighbor, None)
                    captures += 1
        return captures

    @property
    def defeated(self):
        defeated = []
        pieces = self.pieces
        for owner in range(self.owners):
            if owner != DRAGON_OWNER:
                owner_total = 0
                for piece_type in PieceTypes:
                    count = pieces.get(Piece(owner, piece_type))
                    if count:
                        owner_total += count
                owner_towers = pieces.get(Piece(owner, PieceTypes.TOWER))
                if (owner_towers and owner_total == owner_towers) or\
                        (not owner_towers and owner_total < MIN_PIECES):
                    defeated.append(owner)
        return defeated

    @property
    def domination_winners(self):
        defeated = self.defeated
        if self.owners - len(defeated) == 2:
            for candidate in range(self.owners):
                if candidate != DRAGON_OWNER and candidate not in defeated:
                    return {candidate}
        return set()

    @property
    def tower_winners(self):
        tower_winners = set()
        for cell in self.tower_cells:
            tower = self.get_piece(cell)
            if tower and tower.piece_type == PieceTypes.TOWER:
                dragons = 0
                for neighbor in cell.neighbors:
                    dragon = self.get_piece(neighbor)
                    if not dragon or dragon.piece_type != PieceTypes.DRAGON:
                        break
                    dragons += 1
                if dragons == 4:
                    tower_winners.add(tower.owner)
        return tower_winners

    def move(self, move, owner):
        if move.start == move.end:
            piece = self.get_piece(move.start)
            if not piece:
                # Build tower
                self.board[move.start.row][move.start.col] = Piece(owner, PieceTypes.TOWER)
            else:
                # Promote knight
                self.board[move.start.row][move.start.col] = Piece(owner, PieceTypes.KNIGHT)
        else:
            piece = self.board[move.start.row][move.start.col]
            self.set_piece(move.start, None)
            self.set_piece(move.end, piece)
            if piece.piece_type == PieceTypes.PAWN or piece.piece_type == PieceTypes.DRAGON:
                captures = self.capture(move.end, owner)
                if captures > 0:
                    winners = self.domination_winners
                    if winners:
                        return winners
                if TOWER_VICTORY and piece.piece_type == PieceTypes.DRAGON:
                    winners = self.tower_winners
                    if winners:
                        return winners
        return set()


class Game:
    def __init__(self, board, players, turn=1):
        self.board = board
        self.players = players
        self.turn = turn
        self.history = [str(board)]

    def next_turn(self):
        self.turn = self.turn + 1 if self.turn < self.players else 1

    def prev_turn(self):
        self.turn = self.turn - 1 if self.turn > 1 else self.players

    def get_move_error(self, move):
        return self.board.get_move_error(move, self.turn)

    def move(self, move):
        winners = self.board.move(move, self.turn)
        self.next_turn()
        self.history.append(str(self.board))
        return winners

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.board.load(self.history[-1])
            self.prev_turn()
            return ''
        return 'There are no previous moves to undo.'


def game_over(winners):
    assert winners
    winner_string = f'Player {winners[0]}'
    for winner in winners[1:]:
        winner_string += f' and Player {winner}'
    return f'{winner_string} won the game!'


def main():
    game = DEFAULT_RULESET.create_game()
    error = ''
    winners = set()
    while True:
        if CLEAR:
            os.system('clear')
        print(game.board.pretty)
        if winners:
            print(game_over(list(winners)))
            input('Press enter to exit.')
            sys.exit(0)
        print(error)
        error = ''
        try:
            move_input = input(f"Player {game.turn}'s Move: ")
        except KeyboardInterrupt:
            # Don't print a traceback on KeyboardInterrupt
            print()
            sys.exit(0)
        if move_input == 'exit':
            sys.exit(0)
        elif move_input == 'undo':
            error = game.undo()
        else:
            try:
                move = game.board.parse_move(move_input)
            except (ValueError, IndexError):
                error = 'Bad move format. Moves should be given in chess notation.\n'\
                        + 'e.g. "a1b2" to move from A1 to B2.'
            else:
                error = game.get_move_error(move)
                if not error:
                    winners = game.move(move)


if __name__ == '__main__':
    main()
