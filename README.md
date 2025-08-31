![](readme_assets/market_engine_api.png)
# Market Engine API
## Overview
An API that combines fetching steam market item prices with various other item data, 
such as min/max float values and collections. Mandatory for the Market Engine Client.

## Download
For prebuilt archives, head over to https://marketengine/1fil0.com.

## How to use
If you wish to run the API yourself, here are the steps:  
1: Pay for a Steam Web API Key.  
2: Run the program with flags.

flags:  
```--bymykel``` - refreshes ByMykel CSGO API items. You should only call this once.  
```--assets``` - fetch all skin images. You should only call this once.  
```--steamwebapi``` - refreshes Steam Web API Items.  
```--steamwebapi-key XXXXX``` - provide your key for the Steam Web API.  
```--process``` - create items that are ready to be in use with the client.  
```--sync local``` - sync ready items locally to your client data folder.  
```--interval-sec``` - rerun every x seconds.

## Compile from source
Building happens in the shell network, follow instructions at https://github.com/1FIL0/Market-Engine-Shell-Network.

## LICENCE
Market Engine is licenced under the GPL-V3.0 Licence.










