#!/bin/bash

address=${1}
txhash=`tbears sendtx <(python ./scripts/reset_player.py ${address}) -k ./keystores/gamemaster.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Reset Player txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
