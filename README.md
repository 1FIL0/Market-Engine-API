![](readme_assets/market_engine_api.png)
# Market Engine API
## Overview
An API that combines fetching steam market item prices with various other item data, 
such as min/max float values and collections. Market Engine runs an offical version of this API.

## Download
There's a windows and linux version you can download over at https://website.com or here in the github releases. I currently only support a CLI version of this program

## How to use
In order to use this API, you must get a Steam Web API Key first.  
flags:  
```--bymykel``` - refreshes ByMykel CSGO API items. You should only call this once.  
```--steamwebapi``` - refreshes Steam Web API Items  
```--steamwebapi-key XXXXX``` - provide your key for the Steam Web API  
```--assets``` - fetch all skin images  
```--process``` - create items that are ready to be in use with the client  
```--sync local``` - sync ready items locally to your client data folder  

## Compile from source
### README IN PROGRESS
<!--
### Base
Clone the repo and dependencies:
```git clone https://github.com/1FIL0/Market-Engine-API/ market_engine_api && git clone https://github.com/1FIL0/Market-Engine-Share market_engine_share && https://github.com/1FIL0/Market-Engine-Shell-Network market_engine_shell_network```

### Windows Build setup

### Linux Build setup
navigate to the MarketEngine/ directory, create virtual environment and install packages
```mkdir -p venvs/linux_x86_64/ && source python3 -m venv venvs/linux_x86_64/api_venv && source venvs/linux_x86_64/api_venv/bin/activate && python3 -m pip install requests dotenv```

### Create 7Zip Archive

### Create AppImage
-->

## LICENCE
Market Engine is licenced under the GPL-V3.0 Licence


