# pylint: disable=missing-docstring,missing-module-docstring,missing-class-docstring,missing-function-docstring,unused-wildcard-import

import discord
from boost import *

client = discord.Client()

class GameWrapper:
    def __init__(self, ruleset):
        self.ruleset = ruleset
        self.game = ruleset.create_game()

    def reset(self):
        self.game = self.ruleset.create_game()

    @property
    def message(self):
        return f"```{self.game.board.pretty}```" +\
                f"**Player {self.game.turn}'s Move** (e.g. `/boost a1b2`)"

HELP = '''**Commands:**
- `/boost`: view the current state of the game board
- `/boost new`: start a new game
- `/boost a1b2`: move a piece from A1 to B2 (for example)
- `/boost d2`: build a tower or promote a pawn at D2 (for example)
- `/boost undo`: undo the last move
'''

COLOR = False
wrapper = GameWrapper(DEFAULT_RULESET)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('/boost'):
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

        game = wrapper.game
        winners = set()
        if move_input == 'undo':
            error = game.undo()
            if error:
                await message.channel.send(error)
        else:
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
        output = f"```{game.board.pretty}```"
        if winners:
            output += game_over(list(winners))
            game.reset()
        else:
            output += f"**Player {game.turn}'s Move** (e.g. `/boost a1b2`)"
        await message.channel.send(output)

# Read Discord bot token as first command line argument
if len(sys.argv) < 2:
    print('Please enter your Discord bot token as a command line argument')
    sys.exit(1)
client.run(sys.argv[1])
