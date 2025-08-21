import sys
import path
import skin_refresher
sys.path.insert(0, path.PATH_SHARE)
import argparse
import validator
import api_bymykel
import api_steamweb
import ready_item_processor
import syncer

argParser = argparse.ArgumentParser()
argParser.add_argument("--bymykel", action="store_true")
argParser.add_argument("--steamweb", action="store_true")
argParser.add_argument("--steamweb-key")
argParser.add_argument("--assets", action="store_true")
argParser.add_argument("--process", action="store_true")
argParser.add_argument("--sync")
argParser.add_argument("--interval")
args, unknownArgs = argParser.parse_known_args()

def main():
    validator.validateFiles()
    if args.bymykel:
        api_bymykel.refreshBymykelItems()
    if args.steamweb:
        steamwebKey = ""
        if args.steamweb_key: steamwebKey = args.steamweb_key
        api_steamweb.refreshSteamWebApiItems(steamwebKey)
    if args.process:
        ready_item_processor.createReadyItems()
    if args.assets:
        skin_refresher.refreshSkinImagesFromReadyItems()
    if args.sync == "server":
        syncer.updateServer()
    elif args.sync == "local":
        syncer.updateLocal()

if __name__ == "__main__":
	main()