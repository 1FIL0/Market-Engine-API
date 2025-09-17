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
from item import MarketItem
import response
import json
import env
import shared_args

gSteamWebApiItems: list[MarketItem] = list()

def loadSteamWebApiItems():
    global gSteamWebApiItems
    gSteamWebApiItems.clear()
    logger.sendMessage("Loading Steam Web Api Items")
    data = file_handler.loadJson(str(definitions.PATH_DATA_API_STEAM_WEB_API_ITEMS))
    if not data:
        logger.warnMessage("No Steam Web Api Items found. Could not load, run --steamweb if you need to create ready files")
        return
    for entry in data:
        steamWebItem = MarketItem()
        loadValuesToItem(steamWebItem, entry)
        gSteamWebApiItems.append(steamWebItem)
    logger.sendMessage("Done")

def loadValuesToItem(item: MarketItem, entry: dict[Any, Any]):
    item.fullName = entry["groupname"]
    item_utils.pushSplitItemName(item.fullName, item)

    wearStr: str = entry["wear"]
    if wearStr:
        if wearStr == "fn": item.wear = definitions.consts.WEAR_FACTORY_NEW
        elif wearStr == "mw": item.wear = definitions.consts.WEAR_MINIMAL_WEAR
        elif wearStr == "ft": item.wear = definitions.consts.WEAR_FIELD_TESTED
        elif wearStr == "ww": item.wear = definitions.consts.WEAR_WELL_WORN
        elif wearStr == "bs": item.wear = definitions.consts.WEAR_BATTLE_SCARRED

    categoryStr: str = entry["quality"]
    if categoryStr:
        if categoryStr.startswith("Norm"): item.category = definitions.consts.CATEGORY_NORMAL
        elif categoryStr.startswith("Stat"): item.category = definitions.consts.CATEGORY_STAT_TRAK
        elif categoryStr.startswith("Souv"): item.category = definitions.consts.CATEGORY_SOUVENIR

    gradeStr: str = entry["rarity"]
    if gradeStr:
        if gradeStr.startswith("Consumer"): item.grade = definitions.consts.GRADE_CONSUMER
        if gradeStr.startswith("Industrial"): item.grade = definitions.consts.GRADE_INDUSTRIAL
        if gradeStr.startswith("Mil"): item.grade = definitions.consts.GRADE_MILSPEC
        if gradeStr.startswith("Restricted"): item.grade = definitions.consts.GRADE_RESTRICTED
        if gradeStr.startswith("Classified"): item.grade = definitions.consts.GRADE_CLASSIFIED
        if gradeStr.startswith("Covert"): item.grade = definitions.consts.GRADE_COVERT
        if gradeStr.startswith("Contraband"): item.grade = definitions.consts.GRADE_CONTRABAND

    price: float = 0.0
    if entry["pricemedian7d"] and not price: price = entry["pricemedian7d"]
    if entry["pricemedian"] and not price: price = entry["pricemedian"]
    if not price: price = entry["pricelatest"]
    item.marketPrice = price
    item.imageUrl = entry["itemimage"]
    item.permID = int(entry["id"], 16)
    url = entry["steamurl"]
    if url.startswith("https://steamcommunity.com"):
        item.steamMarketUrl = entry["steamurl"]
    else:
        logger.warnMessage(f"NON STEAM MARKET URL DETECTED: {url}")

def refreshSteamWebApiItems(envPath: str):
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

def getItems():
    global gSteamWebApiItems
    return gSteamWebApiItems