# Boost Rules

Boost is a turn-based abstract strategy board game designed by [Dr. Brady J. Garvin](https://cse.unl.edu/~bgarvin).
These rules have been adapted from the rules tutorial provided in the original implementation of the game and are included here for convenience.

## Board

Boost is normally played on a 9 x 9 grid.
The columns of the grid, known as **files**, are lettered `a` to `i` from west to east.
The rows of the grid, known as **ranks**, are numbered `1` to `9` from south to north.

Pieces are placed in cells on the grid, known as **points**.
Points are named by file and rank.
For example, the point in the southwest corner is called `a1` because it is where file `a` and rank `1` intersect (marked with a `*` below).

```
9 . . . . . . . . .
8 . . . . . . . . .
7 . . . . . . . . .
6 . . . . . . . . .
5 . . . . . . . . .
4 . . . . . . . . .
3 . . . . . . . . .
2 . . . . . . . . .
1 * . . . . . . . .
  a b c d e f g h i
```

## Pieces

There are three types of player-controlled Boost pieces: **pawns**, **knights**, and **towers**.
There are also **dragons**, pieces that do not belong to any player.

Pawns are textually represented with the symbol `P`, knights with `K`, towers with `T`, and dragons with `D`.

Each player controls their own set of pieces.
If color is enabled, all the pieces controlled by a given player share the same color.
If color is not enabled, then Player 1's pieces are represented with lowercase characters, while Player 2's pieces are represented with uppercase characters.
(Dragons are always uppercase, although they are not controlled by Player 2.)

## Setup

In a two-player game, each side begins with 8 pawns.
The first player's pawns go on the first rank, and the second player's pawns go on the ninth rank.
Pawns go on every file except for the `e` file.

```
P P P P . P P P P
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
p p p p . p p p p
```

In a standard game, 7 dragons are added to the board in a random symmetric pattern.
An example of such an arrangement is shown below.

```
P P P P . P P P P
. D . . . . . . .
. . . D . . . . .
. . . . . . . . D
. . . . D . . . .
D . . . . . . . .
. . . . . D . . .
. . . . . . . D .
p p p p . p p p p
```

## Movement

Only one piece may move each turn.
Boost pieces move by taking **steps** along the grid lines.
Each step moves the piece one point east, north, west, or south.

The number of steps a piece takes on a turn depends on its type and its neighbors.
Towers always have zero steps, so they cannot move.
Pawns and knights get one step for themselves, plus one additional step for each piece they are next to, even if that piece belongs to an opponent.
The additional steps are called **boosts**.
When a piece moves, it must always take all of its steps.

In the following examples, the second board shows the result of a possible move from the first board.

```
. . . . . .    . . . . . .
. p . . . . => . . p . . .
. . . . . .    . . . . . .
```

```
. t . . . .    . t . . . .
K p . . . . => K . . . . p
. D . . . .    . D . . . .
```

A piece may not step onto a point occupied by another piece.
Also, a piece may not occupy the same point twice in one turn.

Moves such as the following are perfectly valid.
(The path taken by the pawn is marked with `*` signs.)

```
. t .    . t .
K p . => K * *
. . .    . p *
```

## Construction

If an empty point is surrounded by a player's pieces, and that player has fewer than 2 towers, then that player can spend their turn to place a tower on the empty point.
This is called **building** the tower.

```
. P .    . P .
P . P => P T P
. P .    . P .
```

## Promotion

If a player's pawn is next to one of their towers, and that player has fewer knights than towers, then that player can spend their turn to replace the pawn with a knight.
This is called **promoting** or **knighting** the pawn.

```
. P .    . K .
P T P => P T P
. P .    . P .
```

Because a player can never have more than two towers, they can never have more than two knights.
But even though towers can be captured (as explained next), knights are never demoted to pawns.
So a player can have more knights than towers.

## Capturing

Knights can **capture** pieces by ending their move on an opponent's piece, removing the opponent's piece from the board.
Dragons may not be captured.

```
. P .    . k .
. . . => . . .
p k .    p . .
```

Pawns can capture pieces as well, but not directly.
After a player finishes moving a pawn, if an opponent's piece is adjacent to that pawn on one side and adjacent to another of the player's pieces on the opposite side, it is removed from the board.
This is also known as **flanking** the opponent's piece with the pawn.

```
. p .    . p .
. P . => . . .
p . .    . p .
```

A pawn can capture multiple pieces in the same turn.

```
. p .    . p .
. P .    . . .
p . . => . p .
. P .    . . .
. p .    . p .
```

Pawns only capture after they move.
They cannot capture at other times.

```
. p .    . p .
P . . => . P .
. p .    . p .
```

When a player is moving a pawn, dragons can also be used for the purpose of flanking, instead of another of the player's pieces.

```
. p .    . p .
. P . => . . .
p . .    . p .
```

## Dragons

A player can move any dragon that is adjacent to one of their pieces.
They cannot move other dragons.

```
. . .    . D .
. . . => . . .
p D .    p . .
```

Dragons have the same rules for capturing as pawns.
For instance, you can move a dragon and capture a piece by flanking it with another dragon or another one of your pieces.

```
. . D    . . D
p . P => p . .
D . .    . . D
```

## Passing

A player is **immobilized** if they cannot move, build, or promote any piece.
An immobilized player must skip their turn.
This is called **passing**.

A player who is not immobilized may not skip their turn.

## Defeat

A player is **defeated** if they do not have any towers and they do not have enough pieces to build a tower.
A player is also defeated if their only pieces are towers.
A defeated player must skip their turn.

In this implementation, a player is allowed to voluntarily **forfeit**, causing them to become defeated regardless of the pieces they possess.

## Repetition

A **position** is an arrangement of the pieces on the board.

If players could keep moving to the same positions, then the game could last forever.
Thus, a player may not make a move that would result in a position from earlier in the game unless they have no other choice.

## Winning

A player wins when they have a tower with four adjacent dragons.
Such a victory may be referred to as a **tower victory**.

```
. D .
D T D
. D .
```

A player also wins when all of their opponents are defeated.
If there are three or fewer dragons in the game, then this is the only way to win.
Such a victory may be referred to as a **capture victory**.

# Variants

## Dragonless

This is an official variant in which no dragons are placed on the board.
As such, the only way to win is by defeating your opponent.
The normal rules for defeat apply to this variant.
This variant can be easily combined with other variants.

## 3+ Players

The rules of Boost can be easily extended to support more than two players.

If color is not enabled and the textual format is used for a game with more than two players, then the player number is appended to the piece's symbol.
For instance, `K4` would represent a knight owned by Player 4.

Using this notation, the official setup for a 3-player game is as follows.

```
P3 P3 P3 P3 .  P2 P2 P2 P2
.  .  .  .  .  .  .  .  .
P3 .  .  .  .  .  .  .  P2
P3 .  .  .  .  .  .  .  P2
P3 .  .  .  .  .  .  .  P2
P3 .  .  .  .  .  .  .  P2
.  .  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .  .
P1 P1 P1 P1 . P1  P1 P1 P1
```

Additional unofficial setups for 3+ player games are included, and their textual representations can be found in `rulesets.py`.

The turn order starts with Player 1, then continues to Player 2, Player 3, and so on until reaching the last player.
Then it loops back to Player 1's turn and repeats.
A defeated player must skip their turn, but their pieces are not removed.

In this variant, you cannot flank an opponent's piece with a different opponent's piece.

```
.  P3 .     .  P3 .
.  P2 .  => .  P2 .
P1 .  .     .  P1 .
```
