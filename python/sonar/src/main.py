#* Market Engine API
#* Copyright (C) 2025 OneFil (1FIL0) https://github.com/1FIL0
#*
#* This program is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* This program is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with this program.  If not, see <http://www.gnu.org/licenses/>.
#* See LICENCE file.

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

def main() -> None:
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