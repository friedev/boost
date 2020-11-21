import discord
from boost import *

client = discord.Client()

HELP = '''**Commands:**
- `/boost`: view the current state of the game board
- `/boost new`: start a new game
- `/boost a1b2`: move a piece from A1 to B2 (for example)
- `/boost undo`: undo the last move
'''

COLOR = False
game = Game(Board(DEFAULT_BOARD), Owner.BOTTOM)

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
            await message.channel.send(f"```{game.board.pretty}```**{game.turn.value} Player's Move** (e.g. `/boost a1b2`)")
            return

        move_input = data[1]
        if move_input == 'new':
            game.reset()
            await message.channel.send(f"```{game.board.pretty}```**{game.turn.value} Player's Move** (e.g. `/boost a1b2`)")
            return

        if move_input == 'help':
            await message.channel.send(HELP)
            return

        winners = set()
        if move_input == 'undo':
            if len(game.board.history) > 1:
                game.undo()
            else:
                await message.channel.send('There are no previous moves to undo.')
        else:
            try:
                move = Move(move_input)
            except ValueError:
                await message.channel.send('Unrecognized command or move. For a list of commands, run `/boost help`.')
                return
            else:
                error = game.board.get_move_error(move, game.turn)
                if error:
                    await message.channel.send(error)
                    return
                winners = game.board.move(move, game.turn)
                if not winners and not SOLO:
                    game.next_turn()
        output = f"```{game.board.pretty}```"
        if winners:
            output += game_over(list(winners))
            game.reset()
        else:
            output += f"**{game.turn.value} Player's Move** (e.g. `/boost a1b2`)"
        await message.channel.send(output)

client.run('Nzc5NDE5MTM1MjU5ODM2NDU3.X7gQog.Ctt_1h81-6K41hTA5GoPGuIObCA')
