#!/bin/bash

player=${1}
looted_address=${2}
txhash=`tbears sendtx <(python ./scripts/loot_player.py ${looted_address}) -k ./keystores/j${player}.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Player ${player} : Loot Player txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
