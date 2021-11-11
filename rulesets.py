from enum import Enum

SOLO_BOARD = '''
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
'''

P2_BOARD = '''
P2 P2 P2 P2 .  P2 P2 P2 P2
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
'''

P2_BOARD_MINI = '''
.  .  .  P2 P2 P2 P2
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
P1 P1 P1 P1 .  .  .
'''

P2_BOARD_QUICKSTART = '''
.  .  P2 .  .  .  P2 .  .
.  P2 T2 P2 .  P2 T2 P2 .
.  .  P2 .  .  .  P2 .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  P1 .  .  .  P1 .  .
.  P1 T1 P1 .  P1 T1 P1 .
.  .  P1 .  .  .  P1 .  .
'''

P3_BOARD = '''
P2 P2 P2 P2 .  P3 P3 P3 P3
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
'''

P4_BOARD = '''
P2 P2 P2 P2 .  P4 P4 P4 P4
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P4
P2 .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  .
P1 .  .  .  .  .  .  .  P3
P1 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P3 P3 P3 P3
'''

P4_BOARD_MINIMAL = '''
P2 .  .  .  .  P3 P3 P3 P3
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
P1 P1 P1 P1 .  .  .  .  P4
'''

# P1 can win a tower victory with d1c2
DEBUG_BOARD_TOWER = '''
.  D0 .  .
D0 T1 .  P1
.  D0 .  D0
'''

# P1 can win a capture victory with a4b3
DEBUG_BOARD_CAPTURE_TOWER = '''
P1 T1
.  .
P2 T2
.  D0
'''

# P1 can win a capture victory with a3c3
DEBUG_BOARD_CAPTURE_PAWN = '''
P1 .  .  .
P2 P2 P2 P2
P1 P1 P1 P1
'''

# P1 can defeat P2, P3, and P4 with b5c3
# The captures should be processed before P2/P3/P4 win a tower victory!
DEBUG_BOARD_TRIPLE_DEFEAT = '''
P1 D0 .  T1 P3
P2 D0 .  D0 P4
D0 T2 .  T3 D0
.  D0 T4 D0 .
.  .  D0 .  .
'''

# P1 can defeat P2 with a4b3
# Turn order should skip to P3
DEBUG_BOARD_DEFEATED = '''
P1 T1 P3
.  .  .
P2 T2 .
.  D0 T3
'''


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
    DEBUG_TOWER = Ruleset(DEBUG_BOARD_TOWER, 4, 3, 1, 0)
    DEBUG_CAPTURE_TOWER = Ruleset(DEBUG_BOARD_CAPTURE_TOWER, 2, 4, 2, 0)
    DEBUG_CAPTURE_PAWN = Ruleset(DEBUG_BOARD_CAPTURE_PAWN, 4, 3, 2, 0)
    DEBUG_TRIPLE_DEFEAT = Ruleset(DEBUG_BOARD_TRIPLE_DEFEAT, 5, 5, 4, 0)
    DEBUG_DEFEATED = Ruleset(DEBUG_BOARD_DEFEATED, 3, 4, 3, 0)


DEFAULT_RULESET = Rulesets.P2.value
