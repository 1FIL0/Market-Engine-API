import sys
import os
import path
sys.path.insert(0, path.PATH_SHARE)
from item import MarketItem
import requests
import logger
import time
import file_handler
import definitions
import response
import ready_item_processor

def refreshSkinImagesFromReadyItems():
    logger.sendMessage("Refreshing images")
    readyItems: list[MarketItem] = ready_item_processor.getReadyItems()
    for readyItem in readyItems:
        refreshSkinImageReadyItem(readyItem)
    logger.sendMessage("Finished")

def refreshSkinImageReadyItem(readyItem: MarketItem):
    res = requests.get(readyItem.imageUrl)
    response.sendFastResponseMessage(res)
    if res.status_code != 200: 
        timeWaitSec = 10
        logger.sendMessage(f"Error, Trying again in {timeWaitSec} seconds")
        time.sleep(timeWaitSec)
        refreshSkinImageReadyItem(readyItem)
    filePath = f"{definitions.PATH_DIST_ASSETS_SKINS}/{readyItem.weaponName}.{readyItem.skinName}.{readyItem.category}.{readyItem.wear}.ico"
    logger.sendMessage(filePath)
    if os.path.exists(filePath):
        os.remove(filePath)
    file_handler.writeFile(filePath, res.content, binary=True)