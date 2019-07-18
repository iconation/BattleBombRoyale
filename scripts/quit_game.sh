#!/bin/bash

player=${1}
txhash=`tbears sendtx <(python ./scripts/quit_game.py) -k ./keystores/j${player}.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Player ${player} : Quit Game txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
