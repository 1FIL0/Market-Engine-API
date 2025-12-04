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

from pathlib import Path
import sys
import os
from typing import Any
import path
import item_utils
sys.path.insert(0, path.PATH_SHARE)
import requests
import logger
import file_handler
import definitions
from item_steamweb import ItemSteamweb
import response
import json
import env
import shared_args
import re

LOAD_SUCCESS = 0
LOAD_INVALID_ITEM = -1

g_steamWebApiItems: list[ItemSteamweb] = list()

def loadSteamWebApiItems() -> None:
    global g_steamWebApiItems
    g_steamWebApiItems.clear()
    logger.sendMessage("Loading Steam Web Api Items")
    data = file_handler.loadJson(str(definitions.PATH_DATA_API_STEAM_WEB_API_ITEMS))
    if not data:
        logger.warnMessage("No Steam Web Api Items found. Could not load, run --steamweb if you need to create ready files")
        return
    for entry in data:
        steamWebItem = ItemSteamweb()
        if loadValuesToItem(steamWebItem, entry) == LOAD_INVALID_ITEM: continue
        g_steamWebApiItems.append(steamWebItem)
    logger.sendMessage("Done")

def loadValuesToItem(item: ItemSteamweb, entry: dict[Any, Any]) -> int:
    itemMarketName = entry["marketname"]
    tagType = entry["tag1"]

    validTypeFound = False
    for weaponName in definitions.weapons:
        if weaponName.lower() + " |" in itemMarketName.lower():
            validTypeFound = True
            break
    if not validTypeFound: return LOAD_INVALID_ITEM


    item.fullName = itemMarketName
    item.fullName = re.sub(r"StatTrak", "", item.fullName, flags=re.IGNORECASE)
    item.fullName = re.sub(r"Souvenir", "", item.fullName, flags=re.IGNORECASE)
    item.fullName = re.sub(r"\u2605", "", item.fullName)
    item.fullName = re.sub(r"\u2122", "", item.fullName)
    item.fullName = re.sub(r"\(.*?\)", "", item.fullName)
    item.fullName = item.fullName.strip()

    item_utils.pushSplitItemName(item.fullName, item)
    item.fullName.replace("  ", " ")
    item.permID = int(entry["id"], 16)

    wearStr: str = entry["wear"]
    if not wearStr:
        logger.errorMessage(f"{itemMarketName} has no wear")

    if wearStr:
        if wearStr == "fn": item.wear = definitions.consts.WEAR_FACTORY_NEW
        elif wearStr == "mw": item.wear = definitions.consts.WEAR_MINIMAL_WEAR
        elif wearStr == "ft": item.wear = definitions.consts.WEAR_FIELD_TESTED
        elif wearStr == "ww": item.wear = definitions.consts.WEAR_WELL_WORN
        elif wearStr == "bs": item.wear = definitions.consts.WEAR_BATTLE_SCARRED
        elif wearStr == "np": item.wear = definitions.consts.WEAR_NO_WEAR

    categoryStr: str = entry["quality"]
    if not categoryStr:
        logger.errorMessage(f"{itemMarketName} has no category")

    if categoryStr:
        if categoryStr.startswith("Norm"): item.category = definitions.consts.CATEGORY_NORMAL
        elif categoryStr.startswith("Stat"): item.category = definitions.consts.CATEGORY_STAT_TRAK
        elif categoryStr.startswith("Souv"): item.category = definitions.consts.CATEGORY_SOUVENIR

    gradeStr: str = entry["rarity"]
    if not gradeStr:
        logger.errorMessage(f"{itemMarketName} has no rarity")

    if gradeStr:
        if gradeStr.startswith("Consumer"): item.grade = definitions.consts.GRADE_CONSUMER
        if gradeStr.startswith("Industrial"): item.grade = definitions.consts.GRADE_INDUSTRIAL
        if gradeStr.startswith("Mil"): item.grade = definitions.consts.GRADE_MILSPEC
        if gradeStr.startswith("Restricted"): item.grade = definitions.consts.GRADE_RESTRICTED
        if gradeStr.startswith("Classified"): item.grade = definitions.consts.GRADE_CLASSIFIED
        if gradeStr.startswith("Covert"): item.grade = definitions.consts.GRADE_COVERT
        if gradeStr.startswith("Contraband"): item.grade = definitions.consts.GRADE_CONTRABAND

    # KNIFE / GLOVES HAVE CUSTOM SPECIAL RARITY (STAR)
    if tagType == "Knife" or tagType == "Gloves":
        item.grade = definitions.consts.GRADE_STAR

    price: float = 0.0
    if entry["pricemedian7d"] and not price: price = entry["pricemedian7d"]
    if entry["pricemedian"] and not price: price = entry["pricemedian"]
    if entry["pricelatest"] and not price: price = entry["pricelatest"]
    if not price: 
        logger.warnMessage(f"SteamWebAPI price is null for {item.fullName}")
        price = 0.0
    item.marketPrice = price
    item.imageUrl = entry["itemimage"]
    url = entry["steamurl"]
    if url.startswith("https://steamcommunity.com"):
        item.steamMarketUrl = entry["steamurl"]
    else:
        logger.warnMessage(f"NON STEAM MARKET URL DETECTED: {url}")

    return LOAD_SUCCESS

def refreshSteamWebApiItems(envPath: str) -> requests.Response:
    if not envPath:
        envPath: Path = Path(__file__).resolve().parents[3] / ".env"
    env.loadEnv(envPath)
    logger.sendMessage("Fetching Steam Web API Items")
    steamWebAPIKey = os.getenv("STEAM_WEB_API_KEY")
    
    res = requests.get(f"https://www.steamwebapi.com/steam/api/items?key={steamWebAPIKey}&game=cs2")
    response.sendFastResponseMessage(res)
    if res.status_code != 200: return res
    file_handler.writeFile(str(definitions.PATH_DATA_API_STEAM_WEB_API_ITEMS), json.dumps(res.json()))
    logger.sendMessage("Finished")
    loadSteamWebApiItems()
    return res

def getItems() -> list[ItemSteamweb]:
    global g_steamWebApiItems
    return g_steamWebApiItems