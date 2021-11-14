boards = {
    'solo': '''
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
''',

    'p2': '''
P2 P2 P2 P2 .  P2 P2 P2 P2
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
''',

    'p2_mini': '''
.  .  .  P2 P2 P2 P2
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
.  .  .  .  .  .  .
P1 P1 P1 P1 .  .  .
''',

    'p2_quickstart': '''
.  .  P2 .  .  .  P2 .  .
.  P2 T2 P2 .  P2 T2 P2 .
.  .  P2 .  .  .  P2 .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  P1 .  .  .  P1 .  .
.  P1 T1 P1 .  P1 T1 P1 .
.  .  P1 .  .  .  P1 .  .
''',

    'p3': '''
P2 P2 P2 P2 .  P3 P3 P3 P3
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
P2 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P1 P1 P1 P1
''',

    'p4': '''
P2 P2 P2 P2 .  P4 P4 P4 P4
.  .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  P4
P2 .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  .
P1 .  .  .  .  .  .  .  P3
P1 .  .  .  .  .  .  .  P3
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 .  P3 P3 P3 P3
''',

    'p4_minimal': '''
P2 .  .  .  .  P3 P3 P3 P3
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
P2 .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
.  .  .  .  .  .  .  .  P4
P1 P1 P1 P1 .  .  .  .  P4
''',

    # P1 can win a tower victory with d1c2
    'debug_tower': '''
.  D0 .  .
D0 T1 .  P1
.  D0 .  D0
''',

    # P1 can win a capture victory with a4b3
    'debug_capture_tower': '''
P1 T1
.  .
P2 T2
.  D0
''',

    # P1 can win a capture victory with a3c3
    'debug_capture_pawn': '''
P1 .  .  .
P2 P2 P2 P2
P1 P1 P1 P1
''',

    # P1 can defeat P2, P3, and P4 with b5c3
    # The captures should be processed before P2/P3/P4 win a tower victory!
    'debug_triple_defeat': '''
P1 D0 .  T1 P3
P2 D0 .  D0 P4
D0 T2 .  T3 D0
.  D0 T4 D0 .
.  .  D0 .  .
''',

    # P1 can defeat P2 with a4b3
    # Turn order should skip to P3
    'debug_defeat_order': '''
P1 T1 P3
.  .  .
P2 T2 .
.  D0 T3
''',

    # P2 cannot move
    'debug_no_move': '''
P1 .
.  .
T1 T1
T1 T1
P2 T1
''',
}


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


rulesets = {
    'p2': Ruleset(boards['p2'],
                  width=9,
                  height=9,
                  players=2,
                  dragons=7,
                  max_towers=2,
                  knights_per_tower=1,
                  min_pieces=4,
                  tower_victory=True),

    'solo': Ruleset(boards['solo'],
                    width=9,
                    height=9,
                    players=1,
                    dragons=7,
                    max_towers=2,
                    knights_per_tower=1,
                    min_pieces=4,
                    tower_victory=True),

    'p2_dragonless': Ruleset(boards['p2'],
                             width=9,
                             height=9,
                             players=2,
                             dragons=0,
                             max_towers=2,
                             knights_per_tower=1,
                             min_pieces=4,
                             tower_victory=True),

    'p2_mini': Ruleset(boards['p2_mini'],
                       width=7,
                       height=7,
                       players=2,
                       dragons=7,
                       max_towers=2,
                       knights_per_tower=1,
                       min_pieces=4,
                       tower_victory=True),

    'p2_mini_dragonless': Ruleset(boards['p2_mini'],
                                  width=7,
                                  height=7,
                                  players=2,
                                  dragons=0,
                                  max_towers=2,
                                  knights_per_tower=1,
                                  min_pieces=4,
                                  tower_victory=True),

    'p2_quickstart': Ruleset(boards['p2_quickstart'],
                             width=9,
                             height=9,
                             players=2,
                             dragons=7,
                             max_towers=2,
                             knights_per_tower=1,
                             min_pieces=4,
                             tower_victory=True),

    'p3': Ruleset(boards['p3'],
                  width=9,
                  height=9,
                  players=3,
                  dragons=7,
                  max_towers=2,
                  knights_per_tower=1,
                  min_pieces=4,
                  tower_victory=True),

    'p4': Ruleset(boards['p4'],
                  width=9,
                  height=9,
                  players=4,
                  dragons=7,
                  max_towers=2,
                  knights_per_tower=1,
                  min_pieces=4,
                  tower_victory=True),

    'p4_minimal': Ruleset(boards['p4_minimal'],
                          width=9,
                          height=9,
                          players=4,
                          dragons=7,
                          max_towers=2,
                          knights_per_tower=1,
                          min_pieces=4,
                          tower_victory=True),

    'debug_tower': Ruleset(boards['debug_tower'],
                           width=4,
                           height=3,
                           players=1,
                           dragons=0,
                           max_towers=2,
                           knights_per_tower=1,
                           min_pieces=4,
                           tower_victory=True),

    'debug_capture_tower': Ruleset(boards['debug_capture_tower'],
                                   width=2,
                                   height=4,
                                   players=2,
                                   dragons=0,
                                   max_towers=2,
                                   knights_per_tower=1,
                                   min_pieces=4,
                                   tower_victory=True),

    'debug_capture_pawn': Ruleset(boards['debug_capture_pawn'],
                                  width=4,
                                  height=3,
                                  players=2,
                                  dragons=0,
                                  max_towers=2,
                                  knights_per_tower=1,
                                  min_pieces=4,
                                  tower_victory=True),

    'debug_triple_defeat': Ruleset(boards['debug_triple_defeat'],
                                   width=5,
                                   height=5,
                                   players=4,
                                   dragons=0,
                                   max_towers=2,
                                   knights_per_tower=1,
                                   min_pieces=4,
                                   tower_victory=True),

    'debug_defeat_order': Ruleset(boards['debug_defeat_order'],
                                  width=3,
                                  height=4,
                                  players=3,
                                  dragons=0,
                                  max_towers=2,
                                  knights_per_tower=1,
                                  min_pieces=4,
                                  tower_victory=True),

    'debug_no_move': Ruleset(boards['debug_no_move'],
                             width=2,
                             height=5,
                             players=2,
                             dragons=0,
                             max_towers=5,
                             knights_per_tower=1,
                             min_pieces=4,
                             tower_victory=True),
}


DEFAULT_RULESET = 'p2'
