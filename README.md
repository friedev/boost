# Boost

From the original description of Boost:

> Boost is a turn-based abstract strategy board game like checkers, chess, Xiangqi, or Arimaa.
> It was designed to be new and interesting for humans to play while still admitting a simple AI and supporting various homework assignments on algorithms and data structures in the SOFT 260 course at UNL.

Boost was designed and first implemented by [Dr. Brady J. Garvin](https://cse.unl.edu/~bgarvin).
The original implementation was a Progressive Web App made with [React.js](https://reactjs.org/).

This is a Python implementation that closely conforms to the original rules of the game.
It can run interactively in a terminal session, or as a [Discord](https://discord.com) bot.

## Dependencies

- Python 3
- `termcolor` (optional) - for colored output on the terminal
- `discord.py` (optional) - for Discord bot functionality
- RSVG/Chromium/Chrome (optional) - for graphics on Discord

## Installation

To install Boost, clone the repository and run:

```sh
pip install .
```

For graphics on Discord, installing `librsvg` (on Arch-based systems) or `librsvg2-bin` (on Debian-based systems) is recommended.
Alternatively, if Chromium or Chrome is installed and available on your `PATH`, it can be used instead, although browser-based rendering is more resource intensive.

## Usage

### Terminal

To play boost-py from the command line, simply run:

```sh
boost
```

To see a list of game commands, enter `help` in-game.

For more usage information:

```sh
boost --help
```

### Discord Bot

To run boost-py as a Discord bot, you must first create a bot account via the [Discord Developer Portal](https://discord.com/developers/applications).
This is a standard process and you can find documentation for it online.

Then:

- Save your Discord bot token to a file named `token.txt` in the repo directory.
- Run `./bot.sh` (or `./bot.sh&` to run the bot in the background).
- Invite the bot to the server(s) you wish to use it (via the developer portal).

The bot needs the following permissions:

- View Channels
- Send Messages
- Attach Files (optional; required for graphics support)

After inviting the bot to a server, you can view a list of commands by sending `/boost help` in a channel the bot can read and send messages in.

## Troubleshooting

If you're using RSVG and the Discord bot is displaying a board with no pieces, try setting `XLINK` to `True` in `graphics/board_svg.py`.
(Change the line with `XLINK = False` to `XLINK = True`.)

## Contributing

This Boost implementation is being developed by [Aaron Friesen](https://maugrift.com) as a fun side project, so don't expect incredible levels of polish.
However, I am open to issues and pull requests!

If you want to submit a PR, please follow these guidelines:

- Run the game (both CLI and Discord bot if possible) to check for bugs.
  You can utilize the debug rulesets in `boost.py` to check certain hard-to-test cases, such as victory.
- Copy the license notice from `boost.py` into any new Python files you create.
- Run some Python linters on the files you've changed and ensure there are as few lint issues as possible.

If you want to contribute but aren't sure what to work on, you can find some ideas in `TODO.md`.

## License

This Boost implementation is licensed under the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html).
The original implementation was closed source and unlicensed, but this implementation has received written permission from Dr. Garvin to be publicly distributed.

Among other things, the AGPL implies that if you want to fork the repo and run your own derivative Discord bot, you need to disclose the source code of your implementation.
To do this, I recommend adding a command to the bot (similar to the `/boost info` for this bot) that provides a link back to your repository.
