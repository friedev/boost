"""
Boost Discord bot.
"""

import sys

import discord

from .boost import Game
from .rulesets import rulesets, DEFAULT_RULESET
from .graphics import render_for_discord, RendererNotFoundError

HELP = """\
**Commands:**
- `/boost`: view the current state of the game board
- `/boost new`: start a new game
- `/boost a1b2`: move a piece from A1 to B2 (for example)
- `/boost d2`: build a tower or promote a pawn at D2 (for example)
- `/boost undo`: undo the last move
- `/boost forfeit`: forfeit the current game
- `/boost info`: print information about the bot

**Rules:** <https://github.com/Maugrift/boost/blob/master/RULES.md>"""

INFO = """\
This bot uses a Python implementation of the Boost board game\
designed by Dr. Brady J. Garvin (<https://cse.unl.edu/~bgarvin/>).
- Author: Aaron Friesen - <https://maugrift.com>
- Source Code: <https://github.com/Maugrift/boost>"""

# If true, each Discord user may control multiple groups of pieces in the game
# Playing on another registered player's turn is still forbidden
DUPLICATE_PLAYERS = True
COLOR = False
BOARD_IMAGE_SIZE = 1024
BOARD_IMAGE_BACKGROUND_RGBA = "dededeff"


class GameWrapper:
    def __init__(self, ruleset):
        self.ruleset = ruleset
        self.game = Game(ruleset)
        self.users = [None] * ruleset.players

    def reset(self):
        self.game = Game(self.ruleset)
        self.users = [None] * self.ruleset.players

    @property
    def current_user(self):
        return self.users[self.game.turn - 1]

    def set_current_user(self, user):
        self.users[self.game.turn - 1] = user

    @property
    def board_string(self):
        return f"```{self.game.board.pretty}```"

    @property
    def player_string(self):
        if self.current_user:
            return f"**{self.current_user}'s Turn**"
        return f"**Player {self.game.turn}'s Turn** (e.g. `/boost a1b2`)"

    def _build_message(self, text):
        try:
            image = render_for_discord(
                self.game.board,
                "board.png",
                BOARD_IMAGE_SIZE,
                BOARD_IMAGE_SIZE,
                BOARD_IMAGE_BACKGROUND_RGBA,
            )
            return {
                "file": image,
                "content": text,
            }
        except RendererNotFoundError:
            return {
                "content": self.board_string + text,
            }

    @property
    def message(self):
        return self._build_message(self.player_string)

    def game_over(self, winner):
        winner_string = self.users[winner - 1]
        if not winner_string:
            winner_string = f"Player {winner}"
        result = self._build_message(f"{winner_string} won the game!")
        self.reset()
        return result


client = discord.Client()
wrappers = {}


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("/boost"):
        wrapper = wrappers.get(message.channel.id)
        if not wrapper:
            wrapper = GameWrapper(rulesets[DEFAULT_RULESET])
            wrappers[message.channel.id] = wrapper

        data = message.content.split()
        if len(data) == 1:
            await message.channel.send(**wrapper.message)
            return

        move_input = data[1]
        if move_input == "new":
            wrapper.reset()
            await message.channel.send(**wrapper.message)
            return

        if move_input == "help":
            await message.channel.send(HELP)
            return

        if move_input == "info":
            await message.channel.send(INFO)
            return

        user = message.author.mention
        if user not in wrapper.users and None not in wrapper.users:
            await message.channel.send("You are not a player in this game.")
            return

        game = wrapper.game
        winner = None
        if move_input == "undo":
            error = game.undo()
            if error:
                await message.channel.send(error)
            else:
                await message.channel.send(**wrapper.message)
            return

        if move_input == "forfeit":
            winner = wrapper.game.forfeit()
        else:
            if (wrapper.current_user and user != wrapper.current_user) or (
                not DUPLICATE_PLAYERS
                and not wrapper.current_user
                and user in wrapper.users
            ):
                await message.channel.send("It is not your turn to play.")
                return
            if not wrapper.current_user:
                wrapper.set_current_user(user)

            try:
                move = game.board.parse_move(move_input)
            except ValueError:
                await message.channel.send(
                    "Unrecognized command or move. For a list of commands, "
                    "run `/boost help`."
                )
                return
            else:
                error = game.get_move_error(move)
                if error:
                    await message.channel.send(error)
                    return
                winner = game.move(move)

        if winner:
            await message.channel.send(**wrapper.game_over(winner))
        else:
            await message.channel.send(**wrapper.message)


# Read Discord bot token as first command line argument
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please enter your Discord bot token as a command line argument")
        sys.exit(1)
    client.run(sys.argv[1])
