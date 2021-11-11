# TODO

- Runtime configuration and persistence
	- Choose ruleset via Discord and CLI arguments
	- Save/load game state to/from file
	- Track player stats on Discord
- Show information about previous move
	- Location of previously moved piece before move
	- Location of captured pieces
- Full rules compliance
	- Skip player's turn if they have no possible moves
	- Prevent moves that would lead to a previous board state
- AI
	- Static evaluation score based on piece counts
	- Iterate over all possible moves and choose the one with maximum score
- Maintainability
	- Debug powers (ignore movement rules)
	- Unit tests (unittest package or just a test() method)
	- Optional logging
- Documentation
	- Better error messages
	- Docstrings for all functions/classes
- Performance
	- Cache piece counts
	- Cache defeated players
	- Cache winner?
- New piece types
	- Give each piece properties rather than hardcoding based on type
	- Walls (for variants)
	- New playable pieces (for variants)
- Arbitrary game sizes
	- >9 players
	- >9 ranks
	- >26 files
	- Symmetric placement of dragons for >2 players
- Refactor to support any arbitrary rulesets (e.g. chess)
- Better icon?