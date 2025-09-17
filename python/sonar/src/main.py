import sys
import path
sys.path.insert(0, path.PATH_SHARE)
import argparse
import validator
import api_bymykel
import api_steamweb
import ready_item_processor
import syncer
import time
import logger

argParser = argparse.ArgumentParser()
argParser.add_argument("--bymykel", action="store_true")
argParser.add_argument("--steamweb", action="store_true")
argParser.add_argument("--process", action="store_true")
argParser.add_argument("--sync")
argParser.add_argument("--interval-sec")
argParser.add_argument("--env")
args, unknownArgs = argParser.parse_known_args()

def main():
    validator.validateFiles()
    while (1):
        envPath = ""
        if args.env:
            envPath = args.env
        if args.bymykel:
            api_bymykel.refreshBymykelItems()
        if args.steamweb:
            api_steamweb.refreshSteamWebApiItems(envPath)
        if args.process:
            ready_item_processor.createReadyItems()
        if args.sync == "server":
            syncer.updateServer(envPath)
        elif args.sync == "local":
            syncer.updateLocal()
        if not args.interval_sec:
            break
        logger.sendMessage(f"Sleeping for {args.interval_sec} seconds")
        time.sleep(int(args.interval_sec))

if __name__ == "__main__":
	main()