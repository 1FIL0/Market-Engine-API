![](readme_assets/market_engine_api.png)
# Market Engine API
## Overview
An API that combines fetching steam market item prices with various other item data, 
such as min/max float values and collections. Market Engine runs an offical version of this API.

## Download
There's a windows and linux version you can download over at https://website.com or here in the github releases. This program is CLI Only

## How to use
In order to use this API, you must get a Steam Web API Key first.  
flags:  
```--bymykel``` - refreshes ByMykel CSGO API items. You should only call this once.  
```--assets``` - fetch all skin images. You should only call this once  
```--steamwebapi``` - refreshes Steam Web API Items  
```--steamwebapi-key XXXXX``` - provide your key for the Steam Web API  
```--process``` - create items that are ready to be in use with the client  
```--sync local``` - sync ready items locally to your client data folder  

## Compile from source
Building happens in the shell network, follow instructions at https://github.com/1FIL0/market_engine_shell_network

## LICENCE
Market Engine is licenced under the GPL-V3.0 Licence






