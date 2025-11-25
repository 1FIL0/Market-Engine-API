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
from market_item import MarketItem
from item_bymykel import ItemByMykel
from item_steamweb import ItemSteamweb
import api_bymykel
import api_steamweb

g_readyItems: list[MarketItem] = list()
g_readyItemsCollectionCategoryGradeWear: list[list[list[list[list[MarketItem]]]]] = list() # X_X

def createReadyItems() -> None:
    clearArrays()
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
        combineValuesToReadyItem(readyItem, bymykelItem, steamwebItem)
        insertReadyItem(readyItem)
    pushTradeupValuesToReadyItems()
    saveReadyItems()
    logger.sendMessage("Finished")

def clearArrays() -> None:
    global g_readyItems
    global g_readyItemsCollectionCategoryGradeWear
    g_readyItems.clear()
    g_readyItemsCollectionCategoryGradeWear = [
        [
            [
                [
                    [

                    ] 
                    for _ in range(definitions.consts.WEAR_MAX)
                ]
                for _ in range(definitions.consts.GRADE_MAX)
            ]
            for _ in range(definitions.consts.CATEGORY_MAX)
        ]
        for _ in range(definitions.consts.COLLECTION_MAX)
    ]

def combineValuesToReadyItem(readyItem: MarketItem, bymykelItem: ItemByMykel, steamwebItem: ItemSteamweb) -> None:
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

def pushTradeupValuesToReadyItems() -> None:
    global g_readyItems
    global g_readyItemsCollectionCategoryGradeWear
    for readyItem in g_readyItems:
        tradeupable = False
        # Star/Contraband items cant be traded up
        if readyItem.grade == definitions.consts.GRADE_STAR or readyItem.grade == definitions.consts.GRADE_CONTRABAND:
            tradeupable = False
            continue
        # If collection has no crate and item at collection's max tier, it can't be traded up
        if definitions.collectionToCrate(readyItem.collection) == definitions.consts.CRATE_UNKNOWN and definitions.getMaxCollectionGrade(readyItem.collection) == readyItem.grade:
            tradeupable = False
            continue
        # If crate has no higher rarity than the item, it can't be traded up, aka no covert to star tradeup
        if len(readyItem.crates) > 0 and definitions.getMaxCrateGrade(definitions.crateToInt(readyItem.crates[0])) == readyItem.grade:
            tradeupable = False
            continue

        tradeupable = True
        readyItem.tradeupable = tradeupable
        
def insertReadyItem(readyItem: MarketItem) -> None:
    g_readyItems.append(readyItem)
    # Star / Contraband items aren't in any collections but the outcomes still depend on their crates
    if readyItem.grade == definitions.consts.GRADE_STAR or readyItem.grade == definitions.consts.GRADE_CONTRABAND:
        for crate in readyItem.crates:
            crateCollection = definitions.crateToCollection(crate)
            g_readyItemsCollectionCategoryGradeWear[crateCollection][readyItem.category][readyItem.grade][readyItem.wear]
        return
    
    g_readyItemsCollectionCategoryGradeWear[readyItem.collection][readyItem.category][readyItem.grade][readyItem.wear]

def saveReadyItems() -> None:
    logger.sendMessage("Saving Ready Items")
    finalJsonData: dict[str, Any] = {"DATA": []}
    for readyItem in g_readyItems:
        finalJsonData["DATA"].append(readyItemToJson(readyItem))
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_API_READY_ITEMS), finalJsonData)
    logger.sendMessage("Saved")

def loadReadyItemsFromJson() -> None:
    global g_readyItems
    data = file_handler.loadJson(str(definitions.PATH_DATA_API_READY_ITEMS))
    for entry in data["DATA"]:
        readyItem = MarketItem()
        readyItem.weaponName = entry["Weapon Name"]
        readyItem.skinName = entry["Skin Name"]
        readyItem.fullName = entry["Full Name"]
        readyItem.grade = entry["Grade"]
        readyItem.category = entry["Category"]
        readyItem.wear = entry["Wear"]
        readyItem.marketPrice = entry["Market Price"]
        readyItem.tradeupable = entry["Tradeupable"]
        readyItem.collection = entry["Collection"]
        readyItem.crates = entry["Crates"]
        readyItem.minFloat = entry["Min Float"]
        readyItem.maxFloat = entry["Max Float"]
        readyItem.imageName = entry["Image Name"]
        readyItem.imageUrl = entry["Image URL"]
        readyItem.imageName = entry["Image Name"]
        readyItem.steamMarketUrl = entry["Steam Market URL"]
        g_readyItems.append(readyItem)

def readyItemToJson(readyItem: MarketItem) -> None:
    cratesStringified: list[str] = []
    for crate in readyItem.crates:
        cratesStringified.append(definitions.crateToString(crate))

    jsonData: dict[str, Any] = {
        "Weapon Name": readyItem.weaponName,
        "Skin Name": readyItem.skinName,
        "Full Name": readyItem.fullName,
        "Grade": definitions.gradeToString(readyItem.grade),
        "Category": definitions.categoryToString(readyItem.category),
        "Wear": definitions.wearToString(readyItem.wear),
        "Market Price": readyItem.marketPrice,
        "Tradeupable": readyItem.tradeupable,
        "Collection": definitions.collectionToString(readyItem.collection),
        "Crates": cratesStringified,
        "Min Float": readyItem.minFloat,
        "Max Float": readyItem.maxFloat,
        "Image Name": readyItem.imageName,
        "Image URL": readyItem.imageUrl,
        "Steam Market URL": readyItem.steamMarketUrl
    }
    return jsonData

def getReadyItems() -> list[MarketItem]:
    global g_readyItems
    return g_readyItems