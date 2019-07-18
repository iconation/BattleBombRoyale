#!/bin/bash

curdir="$(cd "$(dirname "$0")"; pwd -P)"
rootdir="$(cd ${curdir}; cd ../../; pwd -P)"

cd ${rootdir}
deploy=BattleBombRoyale_$(cat ./VERSION)
rm -rf ${deploy}

cp -r BattleBombRoyale ${deploy}/
cd ${deploy}

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf tests

python ${curdir}/generate_package_json.py

cd ${rootdir}
zip -r ./releases/${deploy}.zip ${deploy}/
rm -rf ${deploy}
