import json
import sys

if __name__ == '__main__':
    call = json.loads(open("./calls/quit_game.json", "rb").read())
    call["params"]["to"] = open("./config/score_address.txt", "r").read()
    print(json.dumps(call))
