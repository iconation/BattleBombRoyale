#!/bin/bash

player=${1}
token=${2}
txhash=`tbears sendtx <(python ./scripts/join_game.py ${token}) -k ./keystores/j${player}.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Player ${player} : Join Game txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
