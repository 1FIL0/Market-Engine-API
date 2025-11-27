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

class ItemSteamweb:
    def __init__(self):
        self.permID: int = -1
        self.fullName: str = ""
        self.weaponName: str = ""
        self.skinName: str = ""
        self.category: int = -1
        self.grade: int = -1
        self.wear: int = -1
        self.marketPrice: float = -1.0
        self.imageUrl: str = ""
        self.imageName: str = ""
        self.steamMarketUrl: str = ""