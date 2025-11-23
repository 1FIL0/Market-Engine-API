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
from typing import Any
import path
sys.path.insert(0, path.PATH_SHARE)
import logger
import file_handler
import definitions
from item import MarketItem
import api_bymykel
import api_steamweb

gReadyItems: list[MarketItem] = list()

def createReadyItems():
    global gReadyItems
    gReadyItems.clear()
    api_bymykel.loadByMykelItems()
    api_steamweb.loadSteamWebApiItems()
    bymykelItems = api_bymykel.getItems()
    steamWebApiItems = api_steamweb.getItems()
    if not bymykelItems or not steamWebApiItems: return

    logger.sendMessage("Creating ready items for deployment")
    bymykelDict = {(bymykelItem.weaponName, bymykelItem.skinName): bymykelItem for bymykelItem in bymykelItems}

    for steamwebItem in steamWebApiItems:
        key = (steamwebItem.weaponName, steamwebItem.skinName)
        if not key in bymykelDict:
            continue
        bymykelItem = bymykelDict[key]
        readyItem = MarketItem()
        if loadValuesToReadyItem(readyItem, bymykelItem, steamwebItem) != 0:
            continue
        gReadyItems.append(readyItem)
    saveReadyItems()
    logger.sendMessage("Finished")

def loadValuesToReadyItem(readyItem: MarketItem, bymykelItem: MarketItem, steamwebItem: MarketItem):
    readyItem.tempID = len(gReadyItems)
    readyItem.permID = steamwebItem.permID
    readyItem.weaponName = bymykelItem.weaponName
    readyItem.skinName = bymykelItem.skinName
    readyItem.fullName = f"{readyItem.weaponName} {readyItem.skinName}"
    readyItem.minFloat = bymykelItem.minFloat
    readyItem.maxFloat = bymykelItem.maxFloat
    readyItem.collection = bymykelItem.collection
    readyItem.crates = bymykelItem.crates
    readyItem.category = steamwebItem.category
    readyItem.grade = steamwebItem.grade
    readyItem.wear = steamwebItem.wear
    readyItem.marketPrice = steamwebItem.marketPrice
    readyItem.imageUrl = steamwebItem.imageUrl
    readyItem.imageName = f"{readyItem.weaponName}.{readyItem.skinName}.{definitions.categoryToString(readyItem.category)}.{definitions.wearToString(readyItem.wear)}.ico"
    readyItem.steamMarketUrl = steamwebItem.steamMarketUrl
    gradeInt = readyItem.grade
    maxCollectionGrade = definitions.getMaxCollectionGrade(readyItem.collection)
    if (gradeInt == maxCollectionGrade):
        readyItem.tradeupable = False
    else:
        readyItem.tradeupable = True
    if gradeInt > maxCollectionGrade:
        logger.warnMessage(f"{readyItem.weaponName} {readyItem.skinName} has a higher grade than collection")
    return 0

def saveReadyItems():
    logger.sendMessage("Saving Ready Items")
    finalJsonData: dict[str, Any] = {"DATA": []}
    for readyItem in gReadyItems:
        finalJsonData["DATA"].append(readyItemToJson(readyItem))
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_API_READY_ITEMS), finalJsonData)
    logger.sendMessage("Saved")

def loadReadyItemsFromJson():
    global gReadyItems
    data = file_handler.loadJson(str(definitions.PATH_DATA_API_READY_ITEMS))
    for entry in data["DATA"]:
        readyItem = MarketItem()
        readyItem.tempID = entry["Temp ID"]
        readyItem.permID = entry["Perm ID"]
        readyItem.weaponName = entry["Weapon Name"]
        readyItem.skinName = entry["Skin Name"]
        readyItem.fullName = entry["Full Name"]
        readyItem.grade = entry["Grade"]
        readyItem.category = entry["Category"]
        readyItem.wear = entry["Wear"]
        readyItem.marketPrice = entry["Market Price"]
        readyItem.tradeupable = entry["Tradeupable"]
        readyItem.collection = entry["Collection"]
        readyItem.minFloat = entry["Min Float"]
        readyItem.maxFloat = entry["Max Float"]
        readyItem.imageName = entry["Image Name"]
        readyItem.imageUrl = entry["Image URL"]
        readyItem.imageName = entry["Image Name"]
        readyItem.steamMarketUrl = entry["Steam Market URL"]
        gReadyItems.append(readyItem)

def readyItemToJson(readyItem: MarketItem):
    jsonData: dict[str, Any] = {
        "Temp ID": readyItem.tempID,
        "Perm ID": readyItem.permID,
        "Weapon Name": readyItem.weaponName,
        "Skin Name": readyItem.skinName,
        "Full Name": readyItem.fullName,
        "Grade": definitions.gradeToString(readyItem.grade),
        "Category": definitions.categoryToString(readyItem.category),
        "Wear": definitions.wearToString(readyItem.wear),
        "Market Price": readyItem.marketPrice,
        "Tradeupable": readyItem.tradeupable,
        "Collection": definitions.collectionToString(readyItem.collection),
        "Min Float": readyItem.minFloat,
        "Max Float": readyItem.maxFloat,
        "Image Name": readyItem.imageName,
        "Image URL": readyItem.imageUrl,
        "Steam Market URL": readyItem.steamMarketUrl
    }
    return jsonData

def getReadyItems():
    global gReadyItems
    return gReadyItems