#!/bin/sh
# Runs the Discord bot using the token read from a file (default: token.txt)
if [ "$1" ]; then
	token_path="$(realpath "$1")"
else
	token_path=token.txt
fi
cd "$(dirname "$0")" || exit 1
python3 -m boost_game.bot "$(cat "$token_path")"
