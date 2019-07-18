#!/bin/bash

token=${1}
tbears call <(python ./scripts/get_gamestate.py ${token}) -c ./config/tbears_cli_config_local.json