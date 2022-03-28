# boost-py

boost-py is a Python implementation of the Boost board game designed by [Dr. Brady J. Garvin](https://cse.unl.edu/~bgarvin).
It can be run interactively on the terminal, or as a [Discord](https://discord.com) bot.

## Dependencies

- Python 3
- `termcolor` (optional) - for colored output on the terminal
- `discord.py` (optional) - for Discord bot functionality
- RSVG/Chromium/Chrome (optional) - for graphics on Discord

## Installation

To get boost-py, simply clone the repository and install the Python dependencies with `pip`.

For graphics, `librsvg` (on Arch-based systems) or `librsvg2-bin` (on Debian-based systems) is recommended.
Alternatively, if Chromium or Chrome is installed and available on your PATH, it can be used instead.
(Be warned that browser-based rendering is somewhat more resource intensive.)

## Usage

### Terminal

To play boost-py from the command line:

```sh
python -m boost-game
```

To see a list of game commands, enter `help` in-game.

For more usage information:

```sh
python -m boost-game
```

### Discord Bot

To run boost-py as a Discord bot, you have two options:

1. Run `python3 bot.py token`, where `token` is your Discord bot token.
2. Save your Discord bot token to a file named `token.txt` in repo directory.
   Then, run `./bot.sh` (or `./bot.sh&` to run it in the background).

Then, invite the bot to the server(s) you wish to use it in.
The bot needs the following permissions:

- View Channels
- Send Messages
- Attach Files (optional; required for graphics support)

After inviting the bot to a server, you can view a list of bot commands by sending `/boost help` in a channel the bot can read and send messages in.

## Troubleshooting

If you're using RSVG and the Discord bot is displaying a board with no pieces, try setting `XLINK` to `True` in `graphics/board_svg.py`.
(Change the line with `XLINK = False` to `XLINK = True`.)

## Contributing

boost-py is being developed by [Aaron Friesen](https://maugrift.com) as a fun side project, so don't expect incredible levels of polish.
However, I am open to issues and pull requests!

If you want to submit a PR, please follow these guidelines:

- Run the game (both CLI and Discord bot if possible) to check for bugs.
  You can utilize the debug rulesets in `boost.py` to check certain hard-to-test cases, such as victory.
- Copy the license notice from `boost.py` into any new Python files you create.
- Run some Python linters on the files you've changed and ensure there are as few lint issues as possible.

If you want to contribute but aren't sure what to work on, you can find some ideas in `TODO.md`.

## License

boost-py is licensed under the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html).
Among other things, this means that if you want to fork the repo and run your own Discord bot based on boost-py, you need to disclose the source code of the bot.
To do this, I recommend adding a command to the bot (similar to the `/boost info` for this bot) that provides a link back to your repository.
