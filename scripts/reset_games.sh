#!/bin/bash

txhash=`tbears sendtx <(python ./scripts/reset_games.py) -k ./keystores/gamemaster.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Reset Games txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
