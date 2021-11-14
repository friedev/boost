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
import time
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

# Static evaluation scores
PAWN_SCORE = 20
KNIGHT_SCORE = 30
TOWER_SCORE = 80
CONSTRUCTION_CIRCLE_SCORE = 10
DRAGON_CIRCLE_SCORE = 20
DRAGON_CLAIM_SCORE = 5
ACTIVE_PAWN_SCORE = 1
ACTIVE_KNIGHT_SCORE = 2
MOBILE_KNIGHT_SCORE = 1  # Multiplied by boost


def distance(row1, col1, row2, col2):
    # Manhattan distance
    return abs(row2 - row1) + abs(col2 - col1)


def cell_distance(cell1, cell2):
    return distance(cell1.row, cell1.col, cell2.row, cell2.col)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __str__(self):
        # Assumes a 9-row board
        return chr(self.col + ord('a')) + str(9 - self.row)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.row == other.row and self.col == other.col
        return False

    def __hash__(self):
        return hash((self.row, self.col))

    @property
    def neighbors(self):
        return [Cell(self.row - 1, self.col),
                Cell(self.row + 1, self.col),
                Cell(self.row, self.col - 1),
                Cell(self.row, self.col + 1)]


class PieceType:
    def __init__(self, name, symbol, score=0):
        self.name = name
        self.symbol = symbol
        self.score = score


class PieceTypes(enum.Enum):
    DRAGON = PieceType('Dragon', 'D')
    PAWN = PieceType('Pawn', 'P', PAWN_SCORE)
    KNIGHT = PieceType('Knight', 'K', KNIGHT_SCORE)
    TOWER = PieceType('Tower', 'T', TOWER_SCORE)


class Piece:
    def __init__(self, owner, piece_type):
        # assert isinstance(owner, int)
        # assert owner >= 0
        # assert piece_type in PieceTypes
        # assert (owner == DRAGON_OWNER) == (piece_type is PieceTypes.DRAGON)
        self.owner = owner
        self.piece_type = piece_type

    def __str__(self):
        return str(self.piece_type.value.symbol) + str(self.owner)

    def __eq__(self, other):
        if isinstance(other, Piece):
            return (self.owner == other.owner and
                    self.piece_type is other.piece_type)
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
                (self.piece_type is PieceTypes.DRAGON))

    @staticmethod
    def parse(string):
        for piece_type in PieceTypes:
            if piece_type.value.symbol == string[0]:
                return Piece(int(string[1]), piece_type)
        return None


class Move:
    def __init__(self, start, end=None):
        self.start = start
        self.end = end if end is not None else start

    def __str__(self):
        return str(self.start) + str(self.end)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start == other.start and self.end == other.end
        return False

    def __hash__(self):
        return hash((self.start, self.end))

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
    def __init__(self, ruleset, color=COLOR, board=None):
        self.ruleset = ruleset
        self.color = color
        self.board = Board.empty(ruleset.width, ruleset.height)
        if board:
            # Deep copy
            self.owners = 0
            for row in range(len(self.board)):
                for col in range(len(self.board[row])):
                    if board[row][col] is not None:
                        self.board[row][col] = board[row][col]
                        self.owners = max(self.owners, board[row][col].owner)
            # Account for the dragon owner
            self.owners += 1
        else:
            self.load(ruleset.board_string)
            self.place_dragons(ruleset.dragons)
        self.forfeited = set()
        self.piece_counts_cache = None

    @property
    def width(self):
        return len(self.board[0])

    @property
    def height(self):
        return len(self.board)

    @staticmethod
    def empty(width, height):
        return [[None for col in range(width)] for row in range(height)]

    def copy(self):
        new_board = Board(self.ruleset, self.color, self.board)
        new_board.forfeited = self.forfeited
        return new_board

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
        if self.piece_counts_cache is not None:
            return self.piece_counts_cache

        piece_counts = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.get_piece(Cell(row, col))
                if piece is not None:
                    if piece in piece_counts:
                        piece_counts[piece] += 1
                    else:
                        piece_counts[piece] = 1
        self.piece_counts_cache = piece_counts
        return piece_counts

    def get_owned_pieces(self, owners):
        if not isinstance(owners, list):
            owners = [owners]
        owner_pieces = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.get_piece(Cell(row, col))
                if piece is not None and piece.owner in owners:
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

        # Account for the dragon owner
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

    def on_border(self, cell):
        assert cell
        return (cell.row == 0 and
                cell.row == len(self.board) - 1 and
                cell.col == 0 and
                cell.col == len(self.board[cell.row]) - 1)

    def inside_border(self, cell):
        assert cell
        return (cell.row > 0 and
                cell.row < len(self.board) - 1 and
                cell.col > 0 and
                cell.col < len(self.board[cell.row]) - 1)

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
                    # Directly access piece to avoid a redundant bounds check
                    piece = self.board[neighbor.row][neighbor.col]
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
        assert self.get_piece(cell).piece_type is PieceTypes.DRAGON
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
        return owner_towers < self.ruleset.max_towers

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
                self.ruleset.knights_per_tower):
            return False

        for neighbor in cell.neighbors:
            neighbor_piece = self.get_piece(neighbor)
            if (neighbor_piece and
                    neighbor_piece.owner == owner and
                    neighbor_piece.piece_type is PieceTypes.TOWER):
                return True

        return False

    def get_move_error(self, move, owner, skip_pathfinding=False):
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
        elif (piece.piece_type is PieceTypes.DRAGON and
                not self.can_move_dragon(move.start, owner)):
            return f'To move the {piece.name} at '\
                   f'{self.format_cell(move.start)}, '\
                   'you must have an adjacent piece.'
        elif piece.owner != owner and piece.owner != DRAGON_OWNER:
            return f'You are not the owner of the {piece.name} at '\
                   f'{self.format_cell(move.start)}.'
        elif piece.piece_type is PieceTypes.TOWER:
            return 'Towers cannot move.'
        elif not skip_pathfinding and not self.path_exists(move):
            return f'You must move this piece exactly {boost} cell(s).'
        elif not self.in_bounds(move.end):
            return f'{self.format_cell(move.end)} is out of bounds.'
        elif destination and piece.piece_type != PieceTypes.KNIGHT:
            return f'A {piece.name} cannot capture pieces directly.'
        elif destination and destination.owner == owner:
            return 'You cannot capture your own piece.'
        elif destination and destination.piece_type is PieceTypes.DRAGON:
            return 'Dragons cannot be captured.'
        return ''

    def is_valid(self, move, owner, skip_pathfinding=False):
        return not self.get_move_error(move, owner, skip_pathfinding)

    def capture(self, cell, owner):
        # Processes captures made by the piece moved to the given cell by the
        # given owner
        piece = self.get_piece(cell)
        assert piece
        assert (piece.piece_type is PieceTypes.PAWN or
                piece.piece_type is PieceTypes.DRAGON)
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
            if tower and tower.piece_type is PieceTypes.TOWER:
                dragons = 0
                for neighbor in cell.neighbors:
                    dragon = self.get_piece(neighbor)
                    if not dragon or dragon.piece_type != PieceTypes.DRAGON:
                        break
                    dragons += 1
                if dragons == 4:
                    return tower.owner
        return None

    @property
    def winner(self):
        capture_winner = self.capture_winner
        if capture_winner is not None:
            return capture_winner
        if self.ruleset.tower_victory:
            return self.tower_winner
        return None

    def move(self, move, owner, apply=True):
        if not apply:
            new_board = self.copy()
            new_board.move(move, owner, apply=True)
            return new_board

        # Clear cached piece counts since the board may change
        self.piece_counts_cache = None

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
            if piece.piece_type is PieceTypes.KNIGHT and target:
                captures = 1
            # Check for pawn or dragon capture
            elif (piece.piece_type is PieceTypes.PAWN or
                    piece.piece_type is PieceTypes.DRAGON):
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
                    piece.piece_type is PieceTypes.DRAGON):
                winner = self.tower_winner
                if winner:
                    return winner
        return None

    def get_piece_moves(self, cell, owner=None):
        # Ensure that a piece is present and movable
        piece = self.get_piece(cell)
        if piece is None or piece.piece_type is PieceTypes.TOWER:
            return set()

        # Ensure that the owner can actually move this piece
        if owner is None:
            owner = piece.owner
        elif (owner != piece.owner and
                not (piece.owner == DRAGON_OWNER and
                     self.can_move_dragon(cell, owner))):
            return set()

        # Breadth-first search to find all possible moves
        boost = self.get_boost(cell)
        moves = set()
        worklist = queue.Queue()
        worklist.put(Path([cell]))

        while not worklist.empty():
            path = worklist.get()

            if len(path) == boost:
                move = Move(path.start, path.end)
                if self.is_valid(move, owner, skip_pathfinding=True):
                    moves.add(move)

            if len(path) > boost:
                return moves

            for neighbor in path.end.neighbors:
                if self.in_bounds(neighbor):
                    # Directly access piece to avoid a redundant bounds check
                    piece = self.board[neighbor.row][neighbor.col]
                    if ((piece is None or len(path) + 1 == boost) and
                            neighbor not in path.path):
                        worklist.put(Path(path.path + [neighbor]))
        return moves

    def get_owner_moves(self, owner):
        # Use sets to prevent duplicates, but also for a pseudo-random ordering
        construction_moves = set()
        promotion_moves = set()
        normal_moves = set()
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                cell = Cell(row, col)
                normal_moves |= self.get_piece_moves(cell, owner)
                if self.can_build_tower(cell, owner):
                    construction_moves.add(Move(cell))
                elif self.can_promote_knight(cell, owner):
                    promotion_moves.add(Move(cell))

        # Consider moves that create towers and knights first, as they are
        # likely to yield higher scores (best-first search)
        return list(construction_moves) +\
            list(promotion_moves) +\
            list(normal_moves)

    def evaluate(self, owner):
        score = 0
        tower_count = 0
        max_dragon_circle = 0
        max_construction_circle = 0
        dragon_claim_score = 0
        owner_pieces = [0] * self.owners
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                cell = Cell(row, col)
                piece = self.board[row][col]
                if piece:
                    # Owned piece valuation
                    if piece.owner == owner:
                        score += piece.piece_type.value.score

                        # Dragon circle scoring
                        if piece.piece_type is PieceTypes.TOWER:
                            tower_count += 1
                            dragon_circle = 0
                            for neighbor in cell.neighbors:
                                neighbor_piece =\
                                        self.board[neighbor.row][neighbor.col]
                                if (neighbor_piece and
                                        neighbor_piece.piece_type ==
                                        PieceTypes.DRAGON):
                                    dragon_circle += 1
                            if dragon_circle == 4:
                                return INFINITY
                            max_dragon_circle = max(dragon_circle,
                                                    max_dragon_circle)
                        else:
                            # Piece activity and mobility scoring
                            if piece.piece_type is PieceTypes.KNIGHT:
                                boost = self.get_boost(cell)
                                if 1 < boost < 5:
                                    score += MOBILE_KNIGHT_SCORE * boost
                                if self.inside_border(cell):
                                    score += ACTIVE_KNIGHT_SCORE
                            elif self.inside_border(cell):
                                score += ACTIVE_PAWN_SCORE

                    # Dragon claim scoring
                    elif piece.piece_type is PieceTypes.DRAGON:
                        for neighbor in cell.neighbors:
                            # Unsafe check; need to use get_piece
                            neighbor_piece = self.get_piece(neighbor)
                            claimants = set()
                            if (neighbor_piece and
                                    neighbor_piece.piece_type !=
                                    PieceTypes.DRAGON):
                                claimants.add(neighbor_piece.owner)
                            for claimant in claimants:
                                if claimant == owner:
                                    dragon_claim_score += DRAGON_CLAIM_SCORE
                                else:
                                    dragon_claim_score -= DRAGON_CLAIM_SCORE

                    # Opponent piece valuation
                    else:
                        score -= piece.piece_type.value.score
                        owner_pieces[piece.owner] += 1

                # Construction circle scoring
                elif self.inside_border(cell):
                    # Don't count the first piece, since that's a given
                    construction_circle = -1
                    for neighbor in cell.neighbors:
                        neighbor_piece = self.board[neighbor.row][neighbor.col]
                        if neighbor_piece:
                            if neighbor_piece.owner == owner:
                                construction_circle += 1
                            else:
                                construction_circle -= 1
                    max_construction_circle = max(construction_circle,
                                                  max_construction_circle)

        # Check for capture victory
        if self.owners > 2:
            is_winner = True
            for other in range(1, self.owners):
                if (other != owner and
                        owner_pieces[other] >= self.ruleset.min_pieces):
                    is_winner = False
                    break
            if is_winner:
                return INFINITY

        # No capture victory, return normal evaluation
        score += max_dragon_circle * DRAGON_CIRCLE_SCORE
        if tower_count < self.ruleset.max_towers:
            score += max_construction_circle *\
                     CONSTRUCTION_CIRCLE_SCORE
        if tower_count > 0:
            score += dragon_claim_score
        return score


class Game:
    def __init__(self, ruleset, color=COLOR, ai_depth=4):
        self.ruleset = ruleset
        self.board = Board(ruleset, color)
        self.players = ruleset.players
        self.ai_depth = ai_depth
        self.turn = 1
        self.history = [str(self.board)]

    def get_next_turn(self, turn=None):
        if turn is None:
            turn = self.turn
        return turn + 1 if turn < self.players else 1

    def next_turn(self):
        defeated = self.board.defeated
        if len(defeated) == self.players:
            raise ValueError('Every player in the game is defeated')

        self.turn = self.get_next_turn()
        while self.turn in defeated:
            self.turn = self.get_next_turn()

    def get_prev_turn(self, turn=None):
        if turn is None:
            turn = self.turn
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

    def get_best_move(self):
        # Choose a completely random move at AI depth 0
        if self.ai_depth == 0:
            return random.choice(self.board.get_owner_moves(self.turn))

        self.recursions = 0
        start_time = time.time()

        # Minimax with alpha-beta pruning
        move, score = self.maxi(self.board, self.turn, self.turn,
                                -INFINITY, INFINITY, self.ai_depth)

        if VERBOSE:
            end_time = time.time()
            print('Time Elapsed:', end_time - start_time)

        return move

    def maxi(self, board, owner, turn, alpha, beta, depth):
        entry = self.recursions == 0
        self.recursions += 1

        if depth == 0:
            return None, board.evaluate(owner)

        best_move = None
        best_next_move = None
        best_immediate = -INFINITY
        move_number = 1
        all_moves = board.get_owner_moves(turn)
        for move in all_moves:
            if entry and VERBOSE:
                print('Considering move',
                      f'{move_number:2d}/{len(all_moves):2d}:  {move} ',
                      end='')
                prev_best = best_move
                sys.stdout.flush()
                move_number += 1

            # If a move exists, the player must make a move
            if best_move is None:
                best_move = move

            new_board = board.move(move, turn, apply=False)
            immediate_score = new_board.evaluate(owner)

            if entry:
                # Exit early if we can win with this move right now
                if immediate_score == INFINITY:
                    return move, immediate_score

            next_turn = self.get_next_turn(turn)
            if self.players == 2:
                # Use minimax in a 2-player game
                next_move, score = self.mini(new_board, owner, next_turn,
                                             alpha, beta, depth - 1)
            else:
                # Use max^n in a non-2-player game
                next_move, score = self.maxi(new_board, owner, next_turn,
                                             alpha, beta, depth - 1)

            if not entry and score >= beta:
                # Fail-soft beta cutoff
                return move, score

            if (score > alpha or
                    (score == alpha and immediate_score > best_immediate)):
                best_move = move
                best_next_move = next_move
                alpha = score
                best_immediate = immediate_score

            if entry and VERBOSE:
                print(f'(score: {score}, immediate: {immediate_score})')
                new = ' (NEW):' if prev_best != best_move else ':      '
                print(f'Current best move{new} {best_move}',
                      f'(alpha: {alpha}, immediate: {best_immediate})')

        if entry and VERBOSE:
            print('Chosen Move:', best_move)
            print('Next Move:', best_next_move)
            print('Current Score:', best_immediate)
            print('Potential Score:', alpha)
            print('Recursions:', self.recursions)

        return best_move, alpha

    def mini(self, board, owner, turn, alpha, beta, depth):
        self.recursions += 1

        if depth == 0:
            return None, -board.evaluate(owner)

        best_move = None
        best_next_move = None
        best_immediate = INFINITY
        for move in board.get_owner_moves(turn):
            # If a move exists, the player must make a move
            if best_move is None:
                best_move = move

            new_board = board.move(move, turn, apply=False)
            immediate_score = -new_board.evaluate(owner)

            next_turn = self.get_next_turn(turn)
            next_move, score = self.maxi(new_board, owner, next_turn,
                                         alpha, beta, depth - 1)

            if score <= alpha:
                # Fail-soft alpha cutoff
                return next_move, score

            if (score < beta or
                    (score == beta and immediate_score < best_immediate)):
                best_move = move
                best_next_move = next_move
                beta = score
                best_immediate = immediate_score

        return best_next_move, beta


def main(game):
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
        if move_input == 'help':
            error = '\n'\
                'a1b2: move a piece from A1 to B2 (for example)\n'\
                'd2: build a tower or promote a pawn at D2 (for example)\n'\
                'undo: undo the last move\n'\
                'ai: let an AI move for the current player\n'\
                'forfeit: forfeit the current game without exiting\n'\
                'exit: exit the current game\n'
        elif move_input == 'undo':
            error = game.undo()
        elif move_input == 'ai':
            print('AI is thinking...')
            best_move = game.get_best_move()
            if best_move is not None:
                winner = game.move(best_move)
            else:
                game.next_turn()
        elif move_input == 'forfeit':
            winner = game.forfeit()
        elif move_input == 'exit':
            sys.exit(0)
        else:
            try:
                move = game.board.parse_move(move_input)
            except (ValueError, IndexError):
                error = '\n'\
                    'Moves should be given in chess notation.\n'\
                    'e.g. "a1b2" to move from A1 to B2.\n'
            else:
                error = game.get_move_error(move)
                if not error:
                    winner = game.move(move)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Python implementation '
                                     'of the Boost board game; CLI mode')
    parser.add_argument('-r', '--ruleset',
                        default=DEFAULT_RULESET,
                        choices=rulesets.keys(),
                        help='which ruleset to use')
    parser.add_argument('-c', '--color',
                        dest='color',
                        action='store_true',
                        help='force colored output')
    parser.add_argument('-C', '--no-color',
                        dest='color',
                        action='store_false',
                        help='disable colored output')
    parser.add_argument('-p', '--preserve',
                        dest='clear',
                        action='store_false',
                        help="don't clear the screen between moves")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='display logging information for debugging; '
                             'enables preserve')
    parser.add_argument('-a', '--ai',
                        type=int,
                        default=4,
                        help='AI strength, as measured by the minimax depth; '
                             'use 0 for completely random AI moves')
    parser.set_defaults(color=COLOR)
    parser.set_defaults(clear=True)
    args = parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose
    if VERBOSE:
        args.clear = False

    if args.color and not COLOR:
        print('Color is not supported on this system', file=sys.stderr)
        print('Install termcolor via pip for color support', file=sys.stderr)
        sys.exit(1)

    if args.ai < 0:
        print(f'AI minimax depth must be non-negative (was {args.ai})')
        sys.exit(1)

    game = Game(rulesets[args.ruleset], args.color, args.ai)
    main(game)
