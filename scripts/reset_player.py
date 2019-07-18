import json
import sys

if __name__ == '__main__':
    call = json.loads(open("./calls/reset_player.json", "rb").read())
    call["params"]["to"] = open("./config/score_address.txt", "r").read()
    call["params"]["data"]["params"]["address"] = sys.argv[1]
    print(json.dumps(call))
