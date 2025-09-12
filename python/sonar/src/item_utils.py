from item import MarketItem
import re

def pushSplitItemName(fullName: str, item: MarketItem):
    if " | " in fullName:
        cleanedName = re.sub(r'\s*\|\s*', '|', fullName)
        parts = cleanedName.split('|')
        weaponName = parts[0].strip()
        skinName = parts[1].strip()
        item.weaponName = weaponName
        item.skinName = skinName
    else:
        item.weaponName = fullName