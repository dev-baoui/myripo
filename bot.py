import time
import json
import sqlite3
from tradeoffer import SteamPlayer, TradeOffer, readJsonFile, send_heartbeat, my_inventory, updateStock
from steampy.client import SteamClient


db = sqlite3.connect("tf2.db")
dbCur = db.cursor()

emptySettings = {'username': '', 'password': '', 'owner_id': '', 'steamApiKey': '', 'bp_api_key': '', 'bp_user_token': '', 'mp_api_key': '', 'overpay': 0}
settings = readJsonFile('Settings.json')
if settings == {}:
    with open('Settings.json', 'w') as settingsJson:
        json.dump(emptySettings, settingsJson)
    print('{} is empty or not found, an empty "shell" was created please fill it out and reboot the bot'.format('Settings.json'))
    exit()
for set in settings:
    if settings[set] == '':
        print('looks like you haven\'t filled up Settings.json yet, please do so before rebooting the bot')
        exit()


tradesToIgnore = [trade[0] for trade in dbCur.execute('SELECT * FROM trades_history WHERE action="ignored"').fetchall()]


def check():
    response = client.get_trade_offers().get('response')
    if response.get('trade_offers_received') != None and response.get('trade_offers_received') != []:
        trades = response.get('trade_offers_received')
        for trade in trades:
            if int(trade['tradeofferid']) not in tradesToIgnore:
                print('#'*75)
                offer = TradeOffer(trade)
                processed = offer.processOffer()
                if processed not in ('accepted', 'declined', 'ignored'):
                    print('unexpected response, please check this trade offer manually.')
                else:
                    if processed == 'accepted':
                        client.accept_trade_offer(offer.trade['tradeofferid'])
                    elif processed == 'declined':
                        client.decline_trade_offer(offer.trade['tradeofferid'])
                    # elif processed == 'ignored':
                    #     pass
                    print('trade offer {}.'.format(processed))
                    db.execute('INSERT INTO trades_history (tradeofferid, partner, items_to_receive, items_to_give, action, message, time_created) VALUES (?, ?, ?, ?, ?, ?, ?)', (int(offer.trade['tradeofferid']), offer.partner, str(offer.theirItems), str(offer.ourItems), processed, offer.message, offer.trade['time_created']))
                    db.commit()
                print('#'*75)
        return True
    else: return False

# convert a strDict into a dict
# json_acceptable_string = s.replace("'", "\"")
# d = json.loads(json_acceptable_string)




if __name__ == "__main__":
    client = SteamClient(settings['steamApiKey'])
    print("""
    TF2 trading Bot
    Created by: Devossa      Steam: https://steamcommunity.com/id/devossa
    """)
    print('Logging into Steam...\r', end="")
    client.login(settings['username'], settings['password'], 'SteamGuard.json')
    print("SUCCESSFULY LOGGED IN")


    start_time = time.time()
    tradesin5min = 0
    print('Checking for offers...')
    print('{} Heartbeat Sent to backpack.tf {} listings were bumped\r'.format(time.strftime("%H:%M:%S", time.gmtime()), send_heartbeat()), end="")
    
    while True:
        try:
            if check(): tradesin5min += 1
            # print("messages: ", client.chat.fetch_messages())
            if time.time() - start_time > 5*60:
                start_time = time.time()
                print('{} Heartbeat Sent to backpack.tf {} listings were bumped\r'.format(time.strftime("%H:%M:%S", time.gmtime()), send_heartbeat()), end="")
                if tradesin5min > 0:
                    updateStock()
                    tradesin5min = 0
        except Exception as error:
            print(help(error))
            print("#"*75)
            print(dir(error))
        time.sleep(15) # wait 15sec before checking again


db.close()