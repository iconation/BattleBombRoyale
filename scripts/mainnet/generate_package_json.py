import json

version = open("../VERSION", "r").read()

package = {
    "version": version, 
    "main_file": "main", 
    "main_score": "BattleBombRoyale"
}

open("./package.json", "w+").write(json.dumps(package))
