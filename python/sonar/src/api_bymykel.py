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
import requests
import logger
import file_handler
import definitions
from item_bymykel import ItemByMykel
import item_utils
import json
import response

gByMykelApiItems: list[ItemByMykel] = list()

def loadByMykelItems() -> None:
    global gByMykelApiItems
    gByMykelApiItems.clear()
    logger.sendMessage("Loading ByMykel Items")
    data = file_handler.loadJson(str(definitions.PATH_DATA_API_BYMYKEL_CSGO_API_ITEMS))
    if not data:
        logger.warnMessage("No ByMykel CSGO Api Items found. Could not load, run --bymykel if you need to create ready files")
        return
    for dataItem in data:
        byMykelItem = ItemByMykel()

        # Remove star symbol on knives/gloves
        fullName = dataItem["name"]
        if "\u2605" in fullName:
            fullName = fullName.replace("\u2605", "").strip()

        item_utils.pushSplitItemName(fullName, byMykelItem)
        byMykelItem.fullName = fullName

        # Sometimes skins have it's weapon name only, like vanilla knives
        if (byMykelItem.weaponName == byMykelItem.skinName):
            byMykelItem.fullName = f"{byMykelItem.weaponName} | {byMykelItem.skinName}"

        if "collections" in dataItem and isinstance(dataItem["collections"], list) and dataItem["collections"]:
            for collection in dataItem["collections"]:
                byMykelItem.collection = definitions.collectionToInt(collection["name"])
                
        if "crates" in dataItem and isinstance(dataItem["crates"], list) and dataItem["crates"]:
            for crateEntry in dataItem["crates"]:
                crateName = crateEntry["name"]
                crate = definitions.crateToInt(crateName)
                # Sometimes has random souvenir crates, skip them as they're unrecognized by Market Engine
                if crate == definitions.consts.CRATE_UNKNOWN:
                    continue
                byMykelItem.crates.append(crateName)

        byMykelItem.category = definitions.consts.CATEGORY_NORMAL
        if "stattrak" in dataItem and dataItem["stattrak"]:
            byMykelItem.category = definitions.consts.CATEGORY_STAT_TRAK
        if "souvenir" in dataItem and dataItem["souvenir"]:
            byMykelItem.category = definitions.consts.CATEGORY_SOUVENIR

        # Some special skins have null float ranges. such as vanilla knives
        byMykelItem.minFloat = dataItem["min_float"]
        byMykelItem.maxFloat = dataItem["max_float"]
        gByMykelApiItems.append(byMykelItem)
    logger.sendMessage("Done")

def refreshBymykelItems() -> None:
    logger.sendMessage("Getting ByMykel CSGO Api items")
    res = requests.get("https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json")
    response.sendFastResponseMessage(res)
    if res.status_code != 200: return res
    file_handler.writeFile(str(definitions.PATH_DATA_API_BYMYKEL_CSGO_API_ITEMS), json.dumps(res.json()))
    logger.sendMessage("Finished")
    loadByMykelItems()
    return res

def getItems() -> list[ItemByMykel]:
    global gByMykelApiItems
    return gByMykelApiItems