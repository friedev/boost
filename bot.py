# pylint: disable=missing-docstring,missing-module-docstring,missing-class-docstring,missing-function-docstring,unused-wildcard-import

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

import discord
from boost import *

HELP = '''**Commands:**
- `/boost`: view the current state of the game board
- `/boost new`: start a new game
- `/boost a1b2`: move a piece from A1 to B2 (for example)
- `/boost d2`: build a tower or promote a pawn at D2 (for example)
- `/boost undo`: undo the last move
- `/boost info`: print information about the bot

**Rules:** <https://github.com/Maugrift/boost-py/blob/master/RULES.md>'''

INFO = '''\
**boost-py** is a Python implementation of the Boost board game\
designed by Dr. Brady J. Garvin (<https://cse.unl.edu/~bgarvin/>).
- Author: Aaron Friesen - <https://maugrift.com>
- Source Code: <https://github.com/Maugrift/boost-py>'''

# If true, each Discord user may control multiple groups of pieces in the game
# Playing on another registered player's turn is still forbidden
DUPLICATE_PLAYERS = True
COLOR = False

class GameWrapper:
    def __init__(self, ruleset):
        self.ruleset = ruleset
        self.game = ruleset.create_game()
        self.users = [None] * ruleset.players

    def reset(self):
        self.game = self.ruleset.create_game()
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

    @property
    def message(self):
        return self.board_string + self.player_string

client = discord.Client()
wrappers = {}

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/boost'):
        wrapper = wrappers.get(message.channel.id)
        if not wrapper:
            wrapper = GameWrapper(DEFAULT_RULESET)
            wrappers[message.channel.id] = wrapper

        data = message.content.split()
        if len(data) == 1:
            await message.channel.send(wrapper.message)
            return

        move_input = data[1]
        if move_input == 'new':
            wrapper.reset()
            await message.channel.send(wrapper.message)
            return

        if move_input == 'help':
            await message.channel.send(HELP)
            return

        if move_input == 'info':
            await message.channel.send(INFO)
            return

        user = message.author.mention
        if user not in wrapper.users and None not in wrapper.users:
            await message.channel.send('You are not a player in this game.')
            return

        game = wrapper.game
        winners = set()
        if move_input == 'undo':
            error = game.undo()
            if error:
                await message.channel.send(error)
            else:
                await message.channel.send(wrapper.message)
            return

        if move_input == 'forfeit':
            winners = wrapper.game.forfeit()
        else:
            if (wrapper.current_user and user != wrapper.current_user) or\
                    (not DUPLICATE_PLAYERS and not wrapper.current_user and user in wrapper.users):
                await message.channel.send('It is not your turn to play.')
                return
            if not wrapper.current_user:
                wrapper.set_current_user(user)

            try:
                move = game.board.parse_move(move_input)
            except ValueError:
                await message.channel.send(\
                        'Unrecognized command or move. For a list of commands, run `/boost help`.')
                return
            else:
                error = game.get_move_error(move)
                if error:
                    await message.channel.send(error)
                    return
                winners = game.move(move)

        output = wrapper.board_string
        if winners:
            # TODO ping users when they win (add a game_over method to wrapper)
            output += game_over(list(winners))
            wrapper.reset()
        else:
            output += wrapper.player_string
        await message.channel.send(output)

# Read Discord bot token as first command line argument
if len(sys.argv) < 2:
    print('Please enter your Discord bot token as a command line argument')
    sys.exit(1)
client.run(sys.argv[1])
