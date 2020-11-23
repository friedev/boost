# boost-py

boost-py is a Python implementation of the Boost board game designed by [Dr. Brady J. Garvin](https://cse.unl.edu/~bgarvin). It can be run interactively on the terminal, or as a [Discord](https://discord.com) bot.

## Dependencies

- Python 3
- `termcolor` (optional) - for colored output on the terminal
- `discord.py` (optional) - for Discord bot functionality

## Installation

To get boost-py, simply clone the repository and then install the dependencies with `pip`.

## Usage

To play boost-py from the command line, `cd` into the repo and run `python3 boost.py`.

To run boost-py as a Discord bot, you have two options:

- Run `python3 bot.py [token]`, where `[token]` is your Discord bot token.
- Save your Discord bot token to a file named `token.txt` in repo directory. Then, run `./bot.sh` (or `./bot.sh&` to run it in the background).

## Contributing

boost-py is being developed by [Maugrift](https://maugrift.com) as a fun side project, so don't expect incredible levels of polish. However, I am open to issues and pull requests! If you want to submit a PR, make sure to run `pylint3` on all of the source files you've changed and ensure there are as few lint issues as possible. Of course, also make sure you run the game (both CLI and Discord bot if possible) to check for bugs.

If you're not sure what to work on, you can find a temporary list of tasks in a comment in `boost.py`.

## License

boost-py is licensed under the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html). Among other things, this means that if you want to fork the repo and run your own Discord bot based on boost-py, you need to disclose the source code of the bot. To do this, I recommend adding a command to the bot (similar to the `/boost info` for this bot) that provides a link back to your repository.
