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
#* read LICENCE file

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

def updateServer(envPath: str = ""):
    if not envPath:
        envPath: Path = Path(__file__).resolve().parents[3] / ".env"
    _ = env.loadEnv(envPath)
    logger.sendMessage("Pushing ready items to server")
    data: dict[str, Any] = file_handler.loadJson(str(definitions.PATH_DATA_API_READY_ITEMS))
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
    file_handler.copyFile(str(definitions.PATH_DATA_API_READY_ITEMS), str(definitions.PATH_DATA_CLIENT_READY_ITEMS))
    logger.sendMessage("Done")