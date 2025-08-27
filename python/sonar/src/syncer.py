import sys
import os
from typing import Any
import path
sys.path.insert(0, path.PATH_SHARE)
import file_handler
import definitions
import logger
import requests
from pathlib import Path
import env

def updateServer():
    envPath: Path = Path(__file__).resolve().parents[3] / ".env"
    _ = env.loadEnv(envPath)
    logger.sendMessage("Pushing ready items to server")
    data: dict[str, Any] = file_handler.loadJson(definitions.PATH_DATA_API_READY_ITEMS)
    try:
        res = requests.post(
            definitions.URL_MARKET_ENGINE_UPDATE_ITEMS,
            headers={
                "Authorization": f"Bearer {os.getenv("SERVER_UPDATE_ITEMS_SECRET")}",
                "Content-Type": "application/json"
            },
            json=data
        )
        msg = f"Response: {res.status_code} {res.text}"
        if res.status_code != 200:
            logger.errorMessage(msg)
        else:
            logger.sendMessage(msg)
    except:
        logger.errorMessage("Something went wrong")
    logger.sendMessage("Done")

def updateLocal():
    logger.sendMessage("Copying ready items to client")
    file_handler.copyFile(definitions.PATH_DATA_API_READY_ITEMS, definitions.PATH_DATA_CLIENT_READY_ITEMS)
    logger.sendMessage("Done")