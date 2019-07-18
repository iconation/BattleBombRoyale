#!/bin/bash

txhash=`tbears deploy ./BattleBombRoyale/ -c ./config/tbears_cli_config_deploy.json | grep 0x | cut -d' ' -f 3`
echo "Deploy txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}