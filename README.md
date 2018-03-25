# TF2 Trading bot
this is a TF2 trading bot written in python,
it's still far from being at the level i want it to be.

replace these files and fill with your information

Settings_example.json -> Settings.json
___
SteamGuard_example.json -> SteamGuard.json

at this point here's what the bot can do:
* check for offers every 15 seconds and process them
* send a bp.tf heartbeat every 5mins
* update the current_stock in db if it accepts a trade in the last 5mins

stuff i need to add:
* check for incoming messages the deal with them
* auto add/remove/update bp.tf listings
    * still have to think about that.
* work on the website
    * learn the django rest api
    * finish the index page (add/delete/update items from db)
    * add a login system so that only the admin can change
        * when that's done show only prices/stock to normal users
* ideas that might not happen:
    * make an android app to replace the website for phones

i may updating only this file for quite a while since i have other things to focus on.

[My steam profil](http://steamcommunity.com/id/devossa)