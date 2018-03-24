from steam import SteamID
import sqlite3
import json


db = sqlite3.connect("tf2.db")
dbCur = db.cursor()

class TradeOffer:
	""" This Class takes care of the incomming trades """
	def __init__(self, offer=[]):
		self.trade = offer
		self.sqldata = self.sqlToDict(dbCur.execute("select * from items").fetchall())
		self.partnerObj = SteamID(offer.get('accountid_other'))
		self.partner = self.partnerObj.as_64
		self.offerId = offer.get('tradeofferid')
		self.message = offer.get('message')
		self.theirItems = self.getItemsInfo(self.itemName(offer.get('items_to_receive')))
		self.ourItems = self.getItemsInfo(self.itemName(offer.get('items_to_give')))
		self.keyPrice = self.sqlToDict(dbCur.execute("select * from items where item_name = 'Mann Co. Supply Crate Key'").fetchall())['Mann Co. Supply Crate Key']
		self.currency = ['Scrap Metal', 'Reclaimed Metal', 'Refined Metal', 'Mann Co. Supply Crate Key']
		self.settings = self.readJsonFile('Settings.json')
	
	def processOffer(self):
		# NEEDS WORK
		if self.partner == self.settings['owner_id']:
			print('incomming offer from the owner')
			return 'accepted'

		our = {'total': self.totalPrice(), 'allItemsInDB': self.allItemsInDB()}
		their = {'total': self.totalPrice(True), 'allItemsInDB': self.allItemsInDB(True)}
		if our['total'] == 0 and our['allItemsInDB']:
			print('incomming Donation from: {}'.format(self.partner))
			if self.message != "": print('message: {}'.format(self.message))
			return 'accepted'

		their.update({'total+overpay': their['total'] + self.settings['overpay']*self.overPayNeeded()})

		print('Incomming offer from: {}'.format(self.partner))
		if self.message != "": print('message: {}'.format(self.message))
		print('they offered: {} \n with total={}'.format(self.formatItems(True), self.formatPrice(their['total+overpay'])))
		if not their['allItemsInDB']: print('(they offered an item that\'s not in db)')
		print('for our: {} \n with total={}'.format(self.formatItems(), self.formatPrice(our['total'])))
		if not our['allItemsInDB']:
			print('(they took an item that\'s not in db)')
			return 'ignored'

		# I feel like this still needs work
		if their['total+overpay'] < our['total']:
			return 'declined'
		else:
			return 'accepted'

	def formatPrice(self, price:int, sellOrBuy = 'buy') -> str:
		''' Takes in price(in scraps) and returns the formatted price as a string '''
		price = int(price)
		keyP = self.keyPrice[sellOrBuy]
		keys = price//keyP
		refs = (price - keys*keyP)//9
		scraps = (price - keys*keyP) - 9*refs
		priceDict = {'keys': keys, 'refs': refs, 'scraps': scraps}
		ret = [(str(priceDict[curr])+" "+curr) for curr in priceDict if priceDict[curr] != 0]
		return ' '.join(ret) if ret != [] else "0 scraps"
	
	def formatItems(self, hisStuff = False) -> str:
		'''
			Takes a dictionnary of items and returns a string.
			If hisStuff is True it return the received items, else if returns what we're giving
		'''
		if hisStuff:
			return ', '.join(['{}x {}'.format(self.theirItems[item]['amount'], item) for item in self.theirItems])
		else:
			return ', '.join(['{}x {}'.format(self.ourItems[item]['amount'], item) for item in self.ourItems])

	def itemName(self, items:dict) -> dict:
		''' This function add the "uncraftable" prefix if one of the items is unscraftable '''
		for item in items:
			descs = items[item].get('descriptions')
			if descs != None:
				for desc in descs: # type(descs) = list
					if desc.get('value') == '( Not Usable in Crafting )':
						items[item]['market_name'] = 'Non-Craftable ' + items[item]['market_name']
		return items

	def overPayNeeded(self) -> bool:
		overpay = [False, False]
		for item in self.theirItems:
			if item not in self.currency:
				overpay[0] = True
				break
		for item in self.ourItems:
			if item not in self.currency:
				overpay[1] = True
				break
		return False not in overpay

	def sqlToDict(self, items:list = []) -> dict:
		''' Converts the DB list of tuples into a dictionary with key=item_name '''
		newFormattedList = {}
		for item in items:
			newFormattedList[item[1]] = {'item_id': item[0], 'item_name': item[1], 'quality': item[2], 'img_url': item[3], 'buy': item[4], 'sell': item[5]}
		return newFormattedList

	def getItemsInfo(self, items={}) -> dict:
		newItemsDict = {}
		for item in items:
			itemName = items[item]['market_name']
			if self.sqldata.get(itemName) != None:
				if newItemsDict.get(itemName) == None:
					newItemsDict[itemName] = self.sqldata[itemName]
					newItemsDict[itemName].update({'amount': 1})
				else:
					newItemsDict[itemName]['amount'] += 1
		return newItemsDict
	
	def allItemsInDB(self, hisStuff = False) -> bool:
		''' Checks if all items are in DB and returns a Boolean '''
		if hisStuff:
			theirLength = 0
			for item in self.theirItems:
				theirLength += self.theirItems[item]['amount']
			return theirLength == len(self.trade.get('items_to_receive'))
		else:
			ourLength = 0
			for item in self.ourItems:
				ourLength += self.ourItems[item]['amount']
			return ourLength == len(self.trade.get('items_to_give'))

	def totalPrice(self, hisStuff = False) -> int:
		total = 0
		if hisStuff and self.theirItems != {}:
			for itm in self.theirItems:
				total += self.theirItems[itm]['buy']*self.theirItems[itm]['amount']
		elif not hisStuff and self.ourItems != {}:
			for itm in self.ourItems:
				total += self.ourItems[itm]['sell']*self.ourItems[itm]['amount']
		return total

	@staticmethod
	def readJsonFile(filename) -> dict:
		try:
			with open(filename) as fsonFile:
				return json.load(fsonFile)
		except FileNotFoundError:
			return {}
		except json.decoder.JSONDecodeError:
			print('{} file isn\'t formatted correctly, please fix it.'.format(filename))
			exit()


class SteamPlayer:
	''' This Class takes care of the partners stuff '''
	def __init__(self, steam_id_64):
		self.id_64 = steam_id_64
	
	def isBanned(self):
		return False

# db.close()