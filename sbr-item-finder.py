import base64
import nbt
import io
import requests
import time
import colorama
colorama.init()


api_key = "API-KEY"
restInterval = 0.55


searchedItems = ["KUUDRA_RELIC","KUUDRA_FOLLOWER_BOOTS","KUUDRA_FOLLOWER_LEGGINGS",
                 "KUUDRA_FOLLOWER_CHESTPLATE","KUUDRA_FOLLOWER_HELMET","CREATIVE_MIND",
                 "DCTR_SPACE_HELM","DUECES_BUILDER_CLAY","ANCIENT_ELEVATOR","KLOONBOAT",
                 "WIKI_JOURNAL","EDITOR_PENCIL","POTATO_BASKET","QUALITY_MAP",
                 "DEAD_BUSH_OF_LOVE","GAME_ANNIHILATOR","GAME_BREAKER","SHINY_RELIC",
                 "POTATO_CROWN","POTATO_SILVER_MEDAL","WIZARD_WAND","CLOVER_HELMET",
                 "RACING_HELMET","PRICELESS_THE_FISH","DIRT_ROD","GIANT_FISHING_ROD"]


titles = ["Item ID", "UTC Timestamp", "Edition", "Auction", "Bid", "Recipient", "Sender", "Price Paid", "Item UUID", "UTC Date", "UUID", "Username"]
titleTags = {
    "UTC Timestamp": ["TAG_Long('date')", "TAG_Long('relic_finder_ts')"],
    "Edition": ["TAG_Int('edition')", "TAG_Int('basket_edition')", "TAG_Int('relic_index')"],
    "Recipient": ["TAG_String('recipient_name')", "TAG_String('user')", "TAG_String('basket_player_name')", "TAG_String('player')", "TAG_String('relic_finder_chat_name')"],
    "Sender": ["TAG_String('sender_name')", "TAG_String('sender')"],
    "Item UUID": ["TAG_String('uuid')", "TAG_String('relic_finder_uuid')"],
    "UTC Date": ["TAG_String('timestamp')"],
    "Auction": ["TAG_Int('auction')"],
    "Bid": ["TAG_Int('bid')"],
    "Price Paid": ["TAG_Long('price')"]
}
def parseInfo(data, line):
    found_info = dict()
    
    dataRange = [line, line] #find the data range for all of the searched information (anything at the same indentation level)
    while data[dataRange[0]].count("\t") >= 5:
        dataRange[0] -= 1
    while data[dataRange[1]].count("\t") >= 5:
        dataRange[1] += 1
    
    for i in range(dataRange[0], dataRange[1]+1): #loop through everything in the data range and extract anything that contains one of the searched tags
        try:
            for title in list(titleTags.keys()):
                for tag in titleTags[title]:
                    if tag in data[i]:  
                        found_info[title] = data[i].split(": ")[1]

        except:
            pass
    
    return found_info


colourCodes = {
    "§4": "\033[0;31m", #dark_red
    "§c": "\033[1;31m", #red
    "§6": "\033[0;33m", #gold
    "§e": "\033[1;33m", #yellow
    "§2": "\033[0;32m", #dark_green
    "§a": "\033[1;32m", #green
    "§b": "\033[1;36m", #aqua
    "§3": "\033[0;36m", #dark_aqua
    "§1": "\033[0;34m", #dark_blue
    "§9": "\033[1;34m", #blue
    "§d": "\033[1;35m", #light_purple
    "§5": "\033[0;35m", #dark_purple
    "§f": "\033[1;37m", #white
    "§7": "\033[0;37m", #gray
    "§8": "\033[1;30m", #dark_gray
    "§0": "\033[0;30m", #black
    
    "§l": "\033[1m", #bold
    "§m": "\033[9m", #strikethrough
    "§n": "\033[4m", #underline
    "§o": "\033[3m", #italic
    
    "§r": "\033[0m" #reset
    }


def read_skyblock_profile(uuid, username):
    try:
        response = requests.get("https://api.hypixel.net/skyblock/profiles?key=" + api_key + "&uuid=" + str(uuid)) #tries to get the skyblock profile of the uuid from the Hypixel API
        data = response.json()
        success = True
    except:
        success = False
        global failure
        failure = True
    
    
    if success == True: #checks if the Hypixel API request was successful
        data = str(data)
        data = data.replace("{", "}").split("}")
        
        all_found_info = list()
        found = False
        for item in data:
            if "'profiles': None" in item:
                found = None
                
            elif "data" in item:
                item_bytes = (item.split(":")[-1].strip(" '"))
                try:
                    itemData = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(item_bytes))).pretty_tree().split("\n") #attempts to read any values as NBT data
                    
                    for line in range(len(itemData)):
                        if "TAG_String('id')" in itemData[line]: #loops through each line in the data to find item IDs
                            itemID = itemData[line].split(": ")[1] #gets just the item ID
                            
                            if itemID in searchedItems: #check if the item ID is one that is being searched for
                                found_info = parseInfo(itemData, line) #get all data for this item
                                found_info["Item ID"] = itemID
                                found_info["UUID"] = uuid
                                found_info["Username"] = username
                                
                                if itemID == "SHINY_RELIC": #since shiny relic 'editions' are indexes, add 1
                                    found_info["Edition"] = str(int(found_info["Edition"])+1)
                                
                                for title in titles: #remove unnecessary colouring on the end
                                    if title in found_info:
                                        if found_info[title].endswith("§f") or found_info[title].endswith("§7"):
                                            found_info[title] = found_info[title][:-2]
                                
                                all_found_info.append(found_info) #add the item to the list of all current found items
                                
                                found = True
                        
                except Exception as error:
                    pass


        if found != True:
            return found
        
        
        if found == True:
            return all_found_info



failure = False
while True:
    username = input("\n----------------------------\n\nPlayer Username: ")
    try:
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/" + str(username)).json()["id"] #tries to get uuid from mojang API
    except:
        print("\nPlayer not found.")
        uuid = None
    
    if uuid != None:
        print("Player UUID: " + uuid)
        
        try:
            response = read_skyblock_profile(uuid, username) #tries to get sb profile from Hypixel API
        except:
            pass
        
        if failure == False:
            if response == False:
                print("\nNo results found.")
            elif response == None:
                print("\nThis player doesn't have any profiles.")
            else:
                for item in response:
                    if item["Item ID"] == "KUUDRA_RELIC": #checks if the player has any Kuudra Relic, and just displays true if they have 1 or more
                        print("\nKUUDRA_RELIC: TRUE")
                        break
                for item in response:
                    if item["Item ID"] != "KUUDRA_RELIC": #prints out any item that isn't a Kuudra Relic
                        print()
                        for title in titles: #loops through each possible data point the item could have
                            if title not in ["UUID", "Username"]: #doesn't print uuid or username since it's redundant
                                if title in item: #checks if the item has that data point
                                    text = title + ": " + item[title] + "§r" #formats the display text to show what each data point is, and adds the reset colour on the end
                                    if "MVP" in item[title] and "+" in item[title]: #checks if an MVP+ or MVP++ rank is in the data
                                        plusColour = item[title].split("+")[0][7] #gets the plus colour code
                                        text += " (plus colour: " + plusColour + ")" #display the plus colour code at the end, since it can be hard to tell with just the displayed colour
                                    for code in colourCodes.keys(): #replaces all of the colour codes with actual colours to display to the console
                                        text = text.replace(code, colourCodes[code])
                                    print(text)
        
        if failure == True: #checks if the Hypixel API request failed
            print("\nThe Hypixel API is currently down.")
            failure = False
    time.sleep(restInterval) #to prevent accidentally going over the rate limit
