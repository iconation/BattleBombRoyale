#!/bin/bash

# Deploy and cleanup
./scripts/update_score.sh
./scripts/reset_games.sh

# J1 : Create a game
./scripts/create_game.sh 1
./scripts/get_all_gamestates.sh

# J2 : Join the game
