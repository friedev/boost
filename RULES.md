# Boost Rules

Boost is a turn-based abstract strategy board game designed by [Dr. Brady J. Garvin](https://cse.unl.edu/~bgarvin). These rules have been adapted from the rules tutorial provided in the original implementation of the game and are included here for convenience.

## Board

Boost is normally played on a 9 x 9 grid. The columns of the grid, known as **files**, are lettered `a` to `i` from west to east. The rows of the grid, known as **ranks**, are numbered `1` to `9` from south to north.

Pieces are placed in cells on the grid, known as **points**. Points are named by file and rank. For example, the point in the southwest corner is called `a1` because it is where file `a` and rank `1` intersect.

## Pieces

There are three types of player-controlled Boost pieces: **pawns**, **knights**, and **towers**. There are also **dragons**, pieces that do not belong to any player.

In boost-py, pawns are represented with the symbol `P`, knights with `K`, towers with `T`, and dragons with `D`.

Each player controls their own set of pieces. If color is enabled, all the pieces controlled by a given player share the same color.

If color is not enabled in a standard two-player game, then Player 1's pieces are represented with lowercase characters, while Player 2's pieces are represented with uppercase characters. (Dragons are always uppercase, although they are not controlled by Player 2.)

If color is not enabled in a game with more than two players, then the player number is appended to the piece's symbol. For instance, `K4` would represent a knight owned by Player 4.

## Setup

In a two-player game, each side begins with 8 pawns. The first player's pawns go on the first rank, and the second player's pawns go on the ninth rank. Pawns go on every file except for the `e` file.

In a standard game, 7 dragons are added to the board in a random symmetric pattern. However, players may choose to play a dragonless game instead.

## Movement

Only one piece may move each turn. Boost pieces move by taking **steps** along the gridlines. Each step moves the piece one point east, north, west, or south.

The number of steps a piece takes on a turn depends on its type and its neighbors. Towers always have zero steps, so they cannot move. Pawns and knights get one step for themselves, plus one additional step for each piece they are next to, even if that piece belongs to an opponent. The additional steps are called **boosts**. When a piece moves, it must always take all of its steps.

A piece may not step onto a point occupied by another piece. Also, a piece may not occupy the same point more than once over the course of a move.

## Construction

If an empty point is surrounded by a player's pieces, and that player has fewer than 2 towers, then that player can spend their turn to place a tower on the empty point. This is called **building** the tower.

## Promotion

If a player's pawn is next to one of their towers, and that player has fewer knights than towers, then that player can spend their turn to replace the pawn with a knight. This is called **promoting** or **knighting** the pawn.

Because a player can never have more than two towers, they can never have more than two knights. But even though towers can be captured (as explained next), knights are never demoted to pawns. So a player can have more knights than towers.

## Capturing

Knights can **capture** pieces by ending their move on an opponent's piece, removing the opponent's piece from the board. Dragons may not be captured.

Pawns can capture pieces as well, but not directly. After a player finishes moving a pawn, if an opponent's piece is adjacent to that pawn on one side and adjacent to another of the player's pieces on the opposite side, it is removed from the board. This is also known as **flanking** the opponent's piece with the pawn.

A pawn can capture multiple pieces in the same turn. Pawns only capture after they move. They cannot capture at other times.

When a player is moving a pawn, dragons can also be used for the purpose of flanking, instead of another of the player's pieces.

## Dragons

A player can move any dragon that is adjacent to one of their pieces. They cannot move other dragons.

Dragons have the same rules for capturing as pawns. For instance, you can move a dragon and capture a piece by flanking it with another dragon.

## Passing

A player is **immobilized** if they cannot move, build, or promote any piece. An immobilized player must skip their turn. This is called **passing**.

A player who is not immobilized may not skip their turn.

## Defeat

A player is **defeated** if they do not have any towers and they do not have enough pieces to build a tower. A player is also defeated if their only pieces are towers. A defeated player must skip their turn.

In boost-py, a player is allowed to voluntarily **forfeit**, causing them to become defeated regardless of the pieces they possess.

## Repetition

A **position** is an arrangement of the pieces on the board.

If players could keep moving to the same positions, then the game could last forever. Thus, a player may not make a move that would result in a position from earlier in the game unless they have no other choice.

## Winning

A player wins when they have a tower with four adjacent dragons. In boost-py, such a victory is called a **tower victory**.

A player also wins when all of their opponents are defeated. If there are three or fewer dragons in the game, then this is the only way to win. In boost-py, such a victory is called a **capture victory**.
