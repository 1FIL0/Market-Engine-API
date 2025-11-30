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
from master_item import MasterItem
from item_bymykel import ItemByMykel
from item_steamweb import ItemSteamweb
import api_bymykel
import api_steamweb

g_marketItems: list[MarketItem] = list()
g_masterItems: list[MarketItem] = list()
g_masterItemsCollectionCategoryGrade: list[list[list[list[MarketItem]]]] = list()

def createPreparedItems() -> None:
    clearArrays()
    api_bymykel.loadByMykelItems()
    api_steamweb.loadSteamWebApiItems()
    createMarketMasterItems()

def clearArrays() -> None:
    global g_marketItems
    global g_masterItems
    global g_masterItemsCollectionCategoryGrade
    g_marketItems.clear()
    g_masterItems.clear()
    g_masterItemsCollectionCategoryGrade = [
        [
            [
                [

                ]
                for _ in range(definitions.consts.GRADE_MAX)
            ]
            for _ in range(definitions.consts.CATEGORY_MAX)
        ]
        for _ in range(definitions.consts.COLLECTION_MAX)
    ]

def createMarketMasterItems() -> None:
    logger.sendMessage("Creating Master / Market Items")
    bymykelItems = api_bymykel.getItems()
    steamWebApiItems = api_steamweb.getItems()
    if not bymykelItems or not steamWebApiItems: return
    bymykelDict = {(bymykelItem.weaponName, bymykelItem.skinName): bymykelItem for bymykelItem in bymykelItems}
    
    currentMasterName = ""
    currentMasterCategory = -1
    currentMasterPushedCategories = []

    for steamwebItem in steamWebApiItems:
        # Skip these skins
        if steamwebItem.category == definitions.consts.CATEGORY_SOUVENIR: continue
        
        key = (steamwebItem.weaponName, steamwebItem.skinName)
        if not key in bymykelDict:
            continue
        bymykelItem = bymykelDict[key]

        # MASTER ITEMS - Important for steamwebapi items array to be sorted 
        if steamwebItem.fullName != currentMasterName:
            currentMasterName = ""
            currentMasterCategory = -1
            currentMasterPushedCategories = []
        if (steamwebItem.fullName != currentMasterName) or (steamwebItem.category != currentMasterCategory and steamwebItem.category not in currentMasterPushedCategories):
            currentMasterName = bymykelItem.fullName
            currentMasterCategory = steamwebItem.category
            currentMasterPushedCategories.append(steamwebItem.category)
            masterItem = MasterItem()
            combineValuesToMasterItem(masterItem, bymykelItem, steamwebItem)
            insertMasterItem(masterItem)
            
        # MARKET ITEMS
        marketItem = MarketItem()
        combineValuesToMarketItem(marketItem, bymykelItem, steamwebItem)
        insertMarketItem(marketItem)
    sortMasterItems()
    sortMarketItems()
    saveMasterItems()
    saveMarketItems()
    logger.sendMessage("Finished")

def combineValuesToMasterItem(masterItem: MasterItem, bymykelItem: ItemByMykel, steamwebItem: ItemSteamweb):
    masterItem.permID = steamwebItem.permID
    masterItem.weaponName = bymykelItem.weaponName
    masterItem.skinName = bymykelItem.skinName
    masterItem.fullName = f"{masterItem.weaponName} {masterItem.skinName}"
    masterItem.category = steamwebItem.category
    masterItem.minFloat = bymykelItem.minFloat
    masterItem.maxFloat = bymykelItem.maxFloat
    masterItem.collection = bymykelItem.collection
    masterItem.crates = bymykelItem.crates
    masterItem.grade = steamwebItem.grade
    masterItem.imageUrl = steamwebItem.imageUrl
    masterItem.imageName = f"{masterItem.weaponName}.{masterItem.skinName}.{definitions.categoryToString(masterItem.category)}.{0}.ico"
    masterItem.steamMarketUrl = steamwebItem.steamMarketUrl

def combineValuesToMarketItem(marketItem: MarketItem, bymykelItem: ItemByMykel, steamwebItem: ItemSteamweb) -> None:
    marketItem.permID = steamwebItem.permID
    marketItem.weaponName = bymykelItem.weaponName
    marketItem.skinName = bymykelItem.skinName
    marketItem.fullName = f"{marketItem.weaponName} {marketItem.skinName}"
    marketItem.category = steamwebItem.category
    marketItem.grade = steamwebItem.grade
    marketItem.wear = steamwebItem.wear
    marketItem.marketPrice = steamwebItem.marketPrice
    marketItem.imageUrl = steamwebItem.imageUrl
    marketItem.imageName = f"{marketItem.weaponName}.{marketItem.skinName}.{definitions.categoryToString(marketItem.category)}.{definitions.wearToString(marketItem.wear)}.ico"
    marketItem.steamMarketUrl = steamwebItem.steamMarketUrl

def insertMasterItem(masterItem: MasterItem):
    global g_masterItems
    global g_masterItemsCollectionCategoryGrade
    g_masterItems.append(masterItem)
    # Star / Contraband items aren't in any collections but the outcomes still depend on their crates
    if masterItem.grade == definitions.consts.GRADE_STAR or masterItem.grade == definitions.consts.GRADE_CONTRABAND:
        for crate in masterItem.crates:
            crateCollection = definitions.crateToCollection(crate)
            g_masterItemsCollectionCategoryGrade[crateCollection][masterItem.category][masterItem.grade].append(masterItem)
        return
    
    g_masterItemsCollectionCategoryGrade[masterItem.collection][masterItem.category][masterItem.grade].append(masterItem)

def insertMarketItem(marketItem: MarketItem) -> None:
    global g_marketItems
    g_marketItems.append(marketItem)

def sortMasterItems() -> None:
    global g_masterItems
    global g_masterItemsCollectionCategoryGrade
    g_masterItems.sort(key=lambda item: (item.collection, item.grade, item.fullName, item.category))
    currentID = 0
    for masterItem in g_masterItems:
        masterItem.tempAccessID = currentID
        currentID += 1
        pushMasterItemTradeupableStatus(masterItem)
        pushMasterItemOutputs(masterItem)

def sortMarketItems() -> None:
    global g_marketItems
    g_marketItems.sort(key=lambda item: (item.grade, item.fullName, item.category, item.wear))
    currentID = 0
    for marketItem in g_marketItems:
        marketItem.tempAccessID = currentID
        currentID += 1
        for masterItem in g_masterItems:
            if masterItem.fullName == marketItem.fullName and masterItem.category == marketItem.category:
                marketItem.masterItemPermID = masterItem.permID

def pushMasterItemTradeupableStatus(masterItem: MasterItem) -> None:
    tradeupable = False
    # Star/Contraband items cant be traded up
    if masterItem.grade == definitions.consts.GRADE_STAR or masterItem.grade == definitions.consts.GRADE_CONTRABAND:
        tradeupable = False
        return
    # If collection has no crate and item at collection's max tier, it can't be traded up
    if definitions.collectionToCrate(masterItem.collection) == definitions.consts.CRATE_UNKNOWN and definitions.getMaxCollectionGrade(masterItem.collection) == masterItem.grade:
        tradeupable = False
        return
    # If crate has no higher rarity than the item, it can't be traded up, aka no covert to star tradeup
    if len(masterItem.crates) > 0 and definitions.getMaxCrateGrade(definitions.crateToInt(masterItem.crates[0])) == masterItem.grade:
        tradeupable = False
        return
    tradeupable = True
    masterItem.tradeupable = tradeupable
        
def pushMasterItemOutputs(masterItem: MasterItem) -> None:
    global g_masterItemsCollectionCategoryGrade
    if not masterItem.tradeupable: return
    masterCollectionItems = g_masterItemsCollectionCategoryGrade[masterItem.collection][masterItem.category][masterItem.grade + 1]
    for masterCollectionItem in masterCollectionItems:
        masterItem.possibleOutputs.append(masterCollectionItem)

def saveMasterItems() -> None:
    global g_masterItems
    logger.sendMessage("Saving Master Items")
    finalJsonData: dict[str, Any] = {"DATA": []}
    for masterItem in g_masterItems:
        finalJsonData["DATA"].append(masterItemToJson(masterItem))
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_API_MASTER_ITEMS), finalJsonData)
    logger.sendMessage("Saved")

def saveMarketItems() -> None:
    global g_marketItems
    logger.sendMessage("Saving Market Items")
    finalJsonData: dict[str, Any] = {"DATA": []}
    for marketItem in g_marketItems:
        finalJsonData["DATA"].append(marketItemToJson(marketItem))
    file_handler.replaceJsonDataAtomic(str(definitions.PATH_DATA_API_MARKET_ITEMS), finalJsonData)
    logger.sendMessage("Saved")

def masterItemToJson(masterItem: MasterItem) -> None:
    cratesStringified: list[str] = []
    for crate in masterItem.crates:
        cratesStringified.append(definitions.crateToString(crate))
    outputsDict = []
    for output in masterItem.possibleOutputs:
        outputItemEntry = {
            "Temp Access ID": output.tempAccessID,
            "Perm ID": output.permID,
            "Full Name": output.fullName,
        }
        outputsDict.append(outputItemEntry)

    jsonData: dict[str, Any] = {
        "Temp Access ID": masterItem.tempAccessID,
        "Perm ID": masterItem.permID,
        "Weapon Name": masterItem.weaponName,
        "Skin Name": masterItem.skinName,
        "Full Name": masterItem.fullName,
        "Grade": definitions.gradeToString(masterItem.grade),
        "Category": definitions.categoryToString(masterItem.category),
        "Tradeupable": masterItem.tradeupable,
        "Collection": definitions.collectionToString(masterItem.collection),
        "Crates": cratesStringified,
        "Min Float": masterItem.minFloat,
        "Max Float": masterItem.maxFloat,
        "Possible Outputs": outputsDict,
        "Image Name": masterItem.imageName,
        "Image URL": masterItem.imageUrl,
        "Steam Market URL": masterItem.steamMarketUrl
    }
    return jsonData

def marketItemToJson(marketItem: MarketItem) -> None:
    jsonData: dict[str, Any] = {
        "Temp Access ID": marketItem.tempAccessID,
        "Perm ID": marketItem.permID,
        "Master Item Perm ID": marketItem.masterItemPermID,
        "Weapon Name": marketItem.weaponName,
        "Skin Name": marketItem.skinName,
        "Full Name": marketItem.fullName,
        "Grade": definitions.gradeToString(marketItem.grade),
        "Category": definitions.categoryToString(marketItem.category),
        "Wear": definitions.wearToString(marketItem.wear),
        "Market Price": marketItem.marketPrice,
        "Image Name": marketItem.imageName,
        "Image URL": marketItem.imageUrl,
        "Steam Market URL": marketItem.steamMarketUrl
    }
    return jsonData

def getReadyItems() -> list[MarketItem]:
    global g_marketItems
    return g_marketItems