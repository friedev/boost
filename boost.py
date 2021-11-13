# Copyright (C) 2020 Aaron Friesen <maugrift@maugrift.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import enum
import math
import os
import random
import sys
import queue

from rulesets import rulesets, DEFAULT_RULESET

COLOR = True
try:
    from termcolor import colored
except ImportError:
    COLOR = False

INFINITY = float('inf')

EMPTY_CELL_SHORT = '.'
EMPTY_CELL_LONG = '. '

DRAGON_OWNER = 0
OWNER_COLORS = ['green', 'red', 'blue', 'yellow', 'magenta', 'cyan', 'white']


def distance(row1, col1, row2, col2):
    # Manhattan distance
    return abs(row2 - row1) + abs(col2 - col1)


def cell_distance(cell1, cell2):
    return distance(cell1.row, cell1.col, cell2.row, cell2.col)


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


class PieceTypes(enum.Enum):
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
            return (self.owner == other.owner and
                    self.piece_type == other.piece_type)
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
        return (self.owner >= 0 and
                self.piece_type in PieceTypes and
                (self.owner == DRAGON_OWNER) ==
                (self.piece_type == PieceTypes.DRAGON))

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


class Path:
    def __init__(self, path, heuristic=0):
        self.path = path
        self.heuristic = heuristic

    @property
    def start(self):
        return self.path[0] if self.path else None

    @property
    def end(self):
        return self.path[-1] if self.path else None

    @property
    def total_heuristic(self):
        return len(self.path) + self.heuristic

    def __lt__(self, other):
        return self.total_heuristic < other.total_heuristic

    def __gt__(self, other):
        return self.total_heuristic > other.total_heuristic

    def __eq__(self, other):
        return self.total_heuristic == other.total_heuristic

    def __len__(self):
        return len(self.path) - 1


class Board:
    def __init__(self, ruleset, color=COLOR, board=None, forfeited=set()):
        self.ruleset = ruleset
        self.color = color
        self.board = Board.empty(ruleset.width, ruleset.height)
        if board:
            self.board = board
        else:
            self.load(ruleset.board_string)
            self.place_dragons(ruleset.dragons)
        self.forfeited = forfeited

    @property
    def width(self):
        return len(self.board[0])

    @property
    def height(self):
        return len(self.board)

    @staticmethod
    def empty(width, height):
        return [[None for col in range(width)] for row in range(height)]

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
        # Slice off trailing newline
        return string[:-1]

    @property
    def cell_width(self):
        return 2 if self.color or self.owners <= 3 else 3

    @property
    def pretty(self):
        file_labels = '  '
        for col in range(len(self.board[0])):
            file_labels += f'{chr(col + 65)}' + (self.cell_width - 1) * ' '
        string = file_labels + '\n'
        horizontal_border = '─' * (self.cell_width * len(self.board[0]) - 1)
        string += f' ┌{horizontal_border}┐\n'
        for row in range(len(self.board)):
            row_string = f'{len(self.board) - row}'
            string += row_string + '│'
            for col in range(len(self.board[row])):
                piece = self.board[row][col]
                if piece:
                    if self.color:
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
        string += f' └{horizontal_border}┘\n'
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
    def piece_counts(self):
        pieces = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.get_piece(Cell(row, col))
                if piece is not None:
                    if piece in pieces:
                        pieces[piece] += 1
                    else:
                        pieces[piece] = 1
        return pieces

    @property
    def pieces(self):
        pieces = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.get_piece(Cell(row, col))
                if piece is not None:
                    pieces.append(piece)
        return pieces

    def get_owner_pieces(self, owner):
        owner_pieces = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.get_piece(Cell(row, col))
                if piece is not None and piece.owner == owner:
                    owner_pieces.append(piece)
        return owner_pieces

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
                for (piece_type_string, owner_string) in\
                        zip(line[0::], line[1::]):
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
        # To place an odd number of dragons, we have to place one in the
        # middle, since it's the only non-mirrored cell
        dragon = Piece(DRAGON_OWNER, PieceTypes.DRAGON)
        if dragons % 2 != 0:
            if self.board[middle_row][middle_col]:
                raise ValueError(
                        'Cannot place an odd number of dragons on this '
                        'board (center must be unoccupied)')
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
        return (cell.row >= 0 and
                cell.row < len(self.board) and
                cell.col >= 0 and
                cell.col < len(self.board[cell.row]))

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

    def find_path(self, source, destination, distance=None):
        # A* with Manhattan distance heuristic (cell_distance)
        worklist = queue.PriorityQueue()
        worklist.put(Path([source], cell_distance(source, destination)))

        while not worklist.empty():
            path = worklist.get()

            if distance is not None and len(path) > distance:
                return None

            if (path.end == destination and
                    (distance is None or len(path) == distance)):
                return path

            for neighbor in path.end.neighbors:
                if self.in_bounds(neighbor):
                    piece = self.get_piece(neighbor)
                    if ((piece is None or neighbor == destination) and
                            neighbor not in path.path):
                        worklist.put(Path(path.path + [neighbor],
                                          len(path) + 1 +
                                          cell_distance(neighbor,
                                                        destination)))
        return None

    def path_exists(self, move):
        return self.find_path(move.start,
                              move.end,
                              self.get_boost(move.start)) is not None

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

        owner_towers = self.piece_counts.get(Piece(owner, PieceTypes.TOWER), 0)
        return owner_towers < self.max_towers

    def can_promote_knight(self, cell, owner):
        piece = self.get_piece(cell)
        if (not piece or
                piece.owner != owner or
                piece.piece_type != PieceTypes.PAWN):
            return False

        piece_counts = self.piece_counts
        knight = Piece(owner, PieceTypes.KNIGHT)
        tower = Piece(owner, PieceTypes.TOWER)
        if (knight in piece_counts and
                tower in piece_counts and
                piece_counts[knight] >= piece_counts[tower] *
                self.knights_per_tower):
            return False

        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if (neighbor_piece and
                    neighbor_piece.owner == owner and
                    neighbor_piece.piece_type == PieceTypes.TOWER):
                return True

        return False

    def get_move_error(self, move, owner):
        if move.start == move.end:
            if self.can_build_tower(move.start, owner):
                return ''
            if self.can_promote_knight(move.start, owner):
                return ''
            return 'You cannot build a tower here nor promote a pawn to a '\
                   'knight here.'

        piece = self.get_piece(move.start)
        destination = self.get_piece(move.end)
        boost = self.get_boost(move.start)
        if not piece:
            return f'There is no piece at {self.format_cell(move.start)} '\
                    'to move.'
        elif (piece.piece_type == PieceTypes.DRAGON and
                not self.can_move_dragon(move.start, owner)):
            return f'To move the {piece.name} at '\
                   f'{self.format_cell(move.start)}, '\
                   'you must have an adjacent piece.'
        elif piece.owner != owner and piece.owner != DRAGON_OWNER:
            return f'You are not the owner of the {piece.name} at '\
                   f'{self.format_cell(move.start)}.'
        elif piece.piece_type == PieceTypes.TOWER:
            return 'Towers cannot move.'
        elif not self.path_exists(move):
            return f'You must move this piece exactly {boost} cell(s).'
        elif not self.in_bounds(move.end):
            return f'{self.format_cell(move.end)} is out of bounds.'
        elif destination and piece.piece_type != PieceTypes.KNIGHT:
            return f'A {piece.name} cannot capture pieces directly.'
        elif destination and destination.owner == owner:
            return 'You cannot capture your own piece.'
        elif destination and destination.piece_type == PieceTypes.DRAGON:
            return 'Dragons cannot be captured.'
        return ''

    def is_valid(self, move, owner):
        return not self.get_move_error(move, owner)

    def capture(self, cell, owner):
        # Processes captures made by the piece moved to the given cell by the
        # given owner
        piece = self.get_piece(cell)
        assert piece
        assert (piece.piece_type == PieceTypes.PAWN or
                piece.piece_type == PieceTypes.DRAGON)
        captures = 0
        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if (neighbor_piece and
                    neighbor_piece.owner != owner and
                    neighbor_piece.owner != DRAGON_OWNER):
                flank = Cell(neighbor.row + (neighbor.row - cell.row),
                             neighbor.col + (neighbor.col - cell.col))
                flanking_piece = self.get_piece(flank)
                if (flanking_piece and
                        (flanking_piece.owner == owner or
                         flanking_piece.owner == DRAGON_OWNER)):
                    self.set_piece(neighbor, None)
                    captures += 1
        return captures

    @property
    def defeated(self):
        defeated = set()
        piece_counts = self.piece_counts
        for owner in range(self.owners):
            if owner != DRAGON_OWNER:
                owner_total = 0
                for piece_type in PieceTypes:
                    count = piece_counts.get(Piece(owner, piece_type))
                    if count:
                        owner_total += count
                owner_towers = piece_counts.get(Piece(owner, PieceTypes.TOWER))
                tower_victory_possible = (self.ruleset.tower_victory and
                                          owner_towers and
                                          owner_total > owner_towers)
                if (owner_total < self.ruleset.min_pieces and
                        not tower_victory_possible):
                    defeated.add(owner)
        return defeated | self.forfeited

    @property
    def capture_winner(self):
        defeated = self.defeated
        # 2 corresponds to the dragon owner + one remaining player
        if self.owners - len(defeated) == 2:
            for candidate in range(self.owners):
                if candidate != DRAGON_OWNER and candidate not in defeated:
                    return candidate
        return None

    @property
    def tower_winner(self):
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
                    return tower.owner
        return None

    def move(self, move, owner):
        if move.start == move.end:
            piece = self.get_piece(move.start)
            if not piece:
                # Build tower
                self.board[move.start.row][move.start.col] =\
                        Piece(owner, PieceTypes.TOWER)
            else:
                # Promote knight
                self.board[move.start.row][move.start.col] =\
                        Piece(owner, PieceTypes.KNIGHT)
        else:
            # Move piece
            piece = self.board[move.start.row][move.start.col]
            target = self.board[move.end.row][move.end.col]
            self.set_piece(move.start, None)
            self.set_piece(move.end, piece)

            captures = 0
            # Check for direct knight capture
            if piece.piece_type == PieceTypes.KNIGHT and target:
                captures = 1
            # Check for pawn or dragon capture
            elif (piece.piece_type == PieceTypes.PAWN or
                    piece.piece_type == PieceTypes.DRAGON):
                captures = self.capture(move.end, owner)

            # Check for capture victory if any pieces were captured
            if captures > 0:
                winner = self.capture_winner
                if winner:
                    return winner

            # Check for tower victory if a dragon was moved
            # Must be checked after captures in case a player captured a tower
            # by moving a fourth dragon next to it
            if (self.ruleset.tower_victory and
                    piece.piece_type == PieceTypes.DRAGON):
                winner = self.tower_winner
                if winner:
                    return winner
        return None


class Game:
    def __init__(self, ruleset, color=COLOR):
        self.ruleset = ruleset
        self.board = Board(ruleset, color)
        self.players = ruleset.players
        self.turn = 1
        self.history = [str(self.board)]

    def get_next_turn(self):
        return self.turn + 1 if self.turn < self.players else 1

    def next_turn(self):
        defeated = self.board.defeated
        if len(defeated) == self.players:
            raise ValueError('Every player in the game is defeated')

        self.turn = self.get_next_turn()
        while self.turn in defeated:
            self.turn = self.get_next_turn()

    def get_prev_turn(self):
        return self.turn - 1 if self.turn > 1 else self.players

    def prev_turn(self):
        defeated = self.board.defeated
        if len(defeated) == self.players:
            raise ValueError('Every player in the game is defeated')

        self.turn = self.get_prev_turn()
        while self.turn in defeated:
            self.turn = self.get_prev_turn()

    def get_move_error(self, move):
        return self.board.get_move_error(move, self.turn)

    def move(self, move):
        winner = self.board.move(move, self.turn)
        self.next_turn()
        self.history.append(str(self.board))
        return winner

    def undo(self):
        if len(self.history) > 1:
            self.prev_turn()
            self.history.pop()
            self.board.load(self.history[-1])
            return ''
        return 'There are no previous moves to undo.'

    def forfeit(self):
        self.board.forfeited.add(self.turn)
        self.next_turn()
        return self.board.capture_winner


def main():
    parser = argparse.ArgumentParser(description='A Python implementation '
                                     'of the Boost board game; CLI mode')
    parser.add_argument('-r', '--ruleset',
                        default=DEFAULT_RULESET,
                        choices=rulesets.keys(),
                        help='which ruleset to use')
    parser.add_argument('-c', '--color', dest='color', action='store_true')
    parser.add_argument('-C', '--no-color', dest='color', action='store_false')
    parser.add_argument('-e', '--clear', dest='clear', action='store_true')
    parser.add_argument('-E', '--no-clear', dest='clear', action='store_false')
    parser.set_defaults(color=COLOR)
    parser.set_defaults(clear=True)
    args = parser.parse_args()

    if args.color and not COLOR:
        print('Color is not supported on this system', file=sys.stderr)
        print('Install termcolor via pip for color support', file=sys.stderr)
        sys.exit(1)

    color = args.color
    game = Game(rulesets[args.ruleset], color)
    error = ''
    winner = None
    while True:
        if args.clear:
            os.system('clear')
        else:
            print()
        print(game.board.pretty)
        if winner:
            print(f'Player {winner} won the game!')
            input('Press enter to exit.')
            sys.exit(0)
        print(error)
        error = ''
        try:
            move_input = input(f"Player {game.turn}'s Move: ")
        except (KeyboardInterrupt, EOFError):
            # Don't print a traceback on user-generated exit signals
            print()
            sys.exit(0)
        if move_input == 'exit':
            sys.exit(0)
        elif move_input == 'undo':
            error = game.undo()
        elif move_input == 'forfeit':
            winner = game.forfeit()
        else:
            try:
                move = game.board.parse_move(move_input)
            except (ValueError, IndexError):
                error = 'Bad move format. Moves should be given in chess '\
                        'notation.\ne.g. "a1b2" to move from A1 to B2.'
            else:
                error = game.get_move_error(move)
                if not error:
                    winner = game.move(move)


if __name__ == '__main__':
    main()
