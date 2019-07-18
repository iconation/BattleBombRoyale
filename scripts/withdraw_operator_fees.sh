#!/bin/bash

address=${1}
amount=${2}
txhash=`tbears sendtx <(python ./scripts/withdraw_operator_fees.py ${address} ${amount}) -k ./keystores/gamemaster.icx -c ./config/tbears_cli_config_local.json | grep 0x | cut -d' ' -f 3`
echo "Address ${address} : Withdraw Operator Fees txhash = ${txhash}"
sleep 2
tbears txresult ${txhash}
