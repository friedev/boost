#!/bin/sh
# Runs the Discord bot using the token stored in token.txt
python3 -m boost-game.bot "$(cat token.txt)"
