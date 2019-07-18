#!/bin/bash

address=${1}
tbears call <(python ./scripts/get_player_room.py ${address}) -c ./config/tbears_cli_config_local.json
