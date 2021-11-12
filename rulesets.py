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
    def __init__(self, board_string, width, height, players, dragons,
                 max_towers, knights_per_tower, min_pieces, tower_victory):
        assert board_string
        assert width >= 1
        assert height >= 1
        assert players >= 1
        assert dragons >= 0
        assert max_towers >= 0
        assert knights_per_tower >= 0
        assert min_pieces > 0
        self.board_string = board_string
        self.width = width
        self.height = height
        self.players = players
        self.dragons = dragons
        self.max_towers = max_towers
        self.knights_per_tower = knights_per_tower
        self.min_pieces = min_pieces
        self.tower_victory = tower_victory

    @property
    def owners(self):
        return self.players + 1


class Rulesets(Enum):
    P2 = Ruleset(P2_BOARD,
                 width=9,
                 height=9,
                 players=2,
                 dragons=7,
                 max_towers=2,
                 knights_per_tower=1,
                 min_pieces=4,
                 tower_victory=True)

    SOLO = Ruleset(SOLO_BOARD,
                   width=9,
                   height=9,
                   players=1,
                   dragons=7,
                   max_towers=2,
                   knights_per_tower=1,
                   min_pieces=4,
                   tower_victory=True)

    P2_DRAGONLESS = Ruleset(P2_BOARD,
                            width=9,
                            height=9,
                            players=2,
                            dragons=0,
                            max_towers=2,
                            knights_per_tower=1,
                            min_pieces=4,
                            tower_victory=True)

    P2_MINI = Ruleset(P2_BOARD_MINI,
                      width=7,
                      height=7,
                      players=2,
                      dragons=7,
                      max_towers=2,
                      knights_per_tower=1,
                      min_pieces=4,
                      tower_victory=True)

    P2_MINI_DRAGONLESS = Ruleset(P2_BOARD_MINI,
                                 width=7,
                                 height=7,
                                 players=2,
                                 dragons=0,
                                 max_towers=2,
                                 knights_per_tower=1,
                                 min_pieces=4,
                                 tower_victory=True)

    P2_QUICKSTART = Ruleset(P2_BOARD_QUICKSTART,
                            width=9,
                            height=9,
                            players=2,
                            dragons=7,
                            max_towers=2,
                            knights_per_tower=1,
                            min_pieces=4,
                            tower_victory=True)

    P3 = Ruleset(P3_BOARD,
                 width=9,
                 height=9,
                 players=3,
                 dragons=7,
                 max_towers=2,
                 knights_per_tower=1,
                 min_pieces=4,
                 tower_victory=True)

    P4 = Ruleset(P4_BOARD,
                 width=9,
                 height=9,
                 players=4,
                 dragons=7,
                 max_towers=2,
                 knights_per_tower=1,
                 min_pieces=4,
                 tower_victory=True)

    P4_MINIMAL = Ruleset(P4_BOARD_MINIMAL,
                         width=9,
                         height=9,
                         players=4,
                         dragons=7,
                         max_towers=2,
                         knights_per_tower=1,
                         min_pieces=4,
                         tower_victory=True)

    DEBUG_TOWER = Ruleset(DEBUG_BOARD_TOWER,
                          width=4,
                          height=3,
                          players=1,
                          dragons=0,
                          max_towers=2,
                          knights_per_tower=1,
                          min_pieces=4,
                          tower_victory=True)

    DEBUG_CAPTURE_TOWER = Ruleset(DEBUG_BOARD_CAPTURE_TOWER,
                                  width=2,
                                  height=4,
                                  players=2,
                                  dragons=0,
                                  max_towers=2,
                                  knights_per_tower=1,
                                  min_pieces=4,
                                  tower_victory=True)

    DEBUG_CAPTURE_PAWN = Ruleset(DEBUG_BOARD_CAPTURE_PAWN,
                                 width=4,
                                 height=3,
                                 players=2,
                                 dragons=0,
                                 max_towers=2,
                                 knights_per_tower=1,
                                 min_pieces=4,
                                 tower_victory=True)

    DEBUG_TRIPLE_DEFEAT = Ruleset(DEBUG_BOARD_TRIPLE_DEFEAT,
                                  width=5,
                                  height=5,
                                  players=4,
                                  dragons=0,
                                  max_towers=2,
                                  knights_per_tower=1,
                                  min_pieces=4,
                                  tower_victory=True)

    DEBUG_DEFEATED = Ruleset(DEBUG_BOARD_DEFEATED,
                             width=3,
                             height=4,
                             players=3,
                             dragons=0,
                             max_towers=2,
                             knights_per_tower=1,
                             min_pieces=4,
                             tower_victory=True)


DEFAULT_RULESET = Rulesets.DEBUG_TRIPLE_DEFEAT.value
