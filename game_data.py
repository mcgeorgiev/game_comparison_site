#TODO: tidyup code.

"""VISUAL"""
#TODO: Sort table with jquery
#TODO: add image for vendor
#TODO: make hyperlinks
#TODO: Add colour to cheapest row


#TODO: Figure out way to filter dlc in humble # Compare HUmble bundle content to steams DLC and if it is the same then determine dlc
#TODO: Add currency???


try:
	import requests
	import bs4
	import re
except ImportError as e:
	print 'Module could not be loaded: '
	print e


def steam(soup, GAME_NAME, dlc):
	""" Scrapes the steam website for data"""

	try:
		elements = soup.findAll("div", 
			{'class':'responsive_search_name_combined'})
	except AttributeError as e:
		print e
		
	rows = []
	for element in elements:
		# gets the title
		try:
			title = element.find('span', {'class':'title'})
		except AttributeError as e:
			print 'Title could not be found'
			print e

		# title therefore exists
		# gets the full/current price and discount
		if is_searched_name_in_list(title, GAME_NAME): 
			
			try:
				# means title is not on sale
				full_price = element.find('div', 
					{'class': 'col search_price responsive_secondrow'})

				current_price = full_price
				discount = '0%'

				if full_price == None :
					raise ValueError

			except:
				# means title is on sale
				try:
					# gets full_price
					prices_tag = element.find("div", 
						{"class": 
						"col search_price discounted responsive_secondrow"})
					full_price = prices_tag.strike
	
		
					try:
						# gets current price
						current_price = prices_tag.contents[2]
					except:
						print 'contents is broken need'

					try:
						# gets DISCOUNT
						discount = element.find("div", {"class": 
							"col search_discount responsive_secondrow"})
					except:
						print 'percentage probably'

				except:
					print 'Something bad'

			#if full_price == 'Free Demo' or full_price == 'Free to Play':
			#	full_price = '0' test with shadow 

		
			

			# get text and encode stuff
			title = title.get_text()
			full_price = full_price.get_text().strip() 
			try:
				discount = discount.get_text().strip() 
				
			except:
				discount = discount
			current_price = current_price.get_text().strip() 
		
			raw_dict = {
						"title": title, 
						"vendor": "steam", 
						"full_price": full_price, 
						"discount": discount, 
						"current_price": current_price, 
						"dlc": dlc
						}

			row = convert_steam(raw_dict)

			rows.append(row)
	return rows


def is_searched_name_in_list(element, GAME_NAME):
	# searches lower case game names in product list
	game_name_list = GAME_NAME.lower().split()

	for word in game_name_list:
		search_regex = re.compile(word)
		game_in_element = search_regex.search(str(element).lower())
		if not game_in_element:
			return False
	return True


def compare_humble_steam(humble_rows, GAME_NAME):

	black_list = [
		'deluxe', 
		'dlc', 
		'pack', 
		'portraits', 
		'unit pack', 
		'music', 
		'pdf'
		]

	humble_rows_copy = humble_rows[:]
	for row in humble_rows_copy:
		title = row['title'].lower()
		title = str(re.sub(r'[^\x00-\x7F]', '', title))
		for word in black_list:
			if word in title:
				row['dlc'] = True

		print row
		print '------'

"""
	url = 'https://steamdb.info/search/?a=app&q='+ GAME_NAME +'&type=4&category=0'
	
	try:
		res = res = requests.get(url)
		res.raise_for_status()
	except:
		print 'e'
	soup = bs4.BeautifulSoup(res.text)
	try:
		elements = soup.findAll("tr", {"class": "app"})
		for element in elements:
			for table_row in element:
				rows = soup.findAll("td")
				print rows
				print '***'
	except:
		print 'something is wrong'
	"""
	
def convert_steam(row):
	new_row = dict(row) # copy

	new_row['full_price'] = float(
		re.sub(r'[^\x00-\x7F]', '', new_row['full_price']))

	new_row['discount'] = int(re.sub('[-%]', '', new_row['discount']))

	new_row['current_price'] = float(
		re.sub(r'[^\x00-\x7F]', '', new_row['current_price']))

	return new_row


def humble_webscrape(data):
	print 'Humble'
	HUMBLE = 'humble'
	rows = []
	for i in range(len(data['results'])):
		title = data['results'][i]["human_name"]
		current_price = data['results'][i]["current_price"][0]
		full_price = data['results'][i]["full_price"][0]
		discount = get_discount(current_price, full_price)
		dlc = False # temporary
		row = {
				"title": title, 
				"vendor": "humble", 
				"full_price": full_price, 
				"discount": discount, 
				"current_price": current_price, 
				"dlc": dlc
				}

		rows.append(row)

	
	return rows


def get_discount(discounted, full_price):
	eqn = (discounted*100)/full_price
	discount = 100 - int(round(eqn, 0))
	return discount


def gog_webscrape(data):

	GOG = 'gog'
	rows = []
	for i in range(len(data['products'])):
		
		title = data['products'][i]["title"]
		current_price = data['products'][i]["price"]['finalAmount']
		full_price = data['products'][i]["price"]['baseAmount']
		discount = data['products'][i]["price"]['discountPercentage']
			
		if data['products'][i]['type'] != 1:
			dlc = True
		else:
			dlc = False

		row = {
						"title": title, 
						"vendor": "gog", 
						"full_price": float(full_price), 
						"discount": int(discount), 
						"current_price": float(current_price), 
						"dlc": dlc
						}

		rows.append(row)

	return rows


def arrange_data(rows, data_list):
	for row in rows:
		data_list.append(row)
	return data_list


def get_data(GAME_NAME):

	URLS = [ 
	['http://store.steampowered.com/search/results?term=' + GAME_NAME + 
		'&sort_by=_ASC&category1=998&page=1&snr=1_7_7_151_7', 'steam', 
		False],

	['http://store.steampowered.com/search/results?term=' + GAME_NAME +'&sort_by=_ASC&category1=21&page=1&snr=1_7_7_151_7', 'steam', True],

	['https://www.humblebundle.com/store/api?request=1&page_size=20&search=' + GAME_NAME, 'humble'],

	['http://www.gog.com/games/ajax/filtered?mediaType=game&page=1&search=' + GAME_NAME, 'gog']
	] 
	
	list_of_data = []

	for url in URLS: 
		website_title = url[1]
		
		try:
			res = requests.get(url[0])
			res.raise_for_status()
		except requests.exceptions.RequestException as e:
			print e

		if website_title == 'steam':
			soup = bs4.BeautifulSoup(res.text)
			rows = steam(soup, GAME_NAME, url[2])

		elif website_title == 'humble':
			data = res.json()
			rows = humble_webscrape(data)
			compare_humble_steam(rows, GAME_NAME)

		elif website_title == 'gog':
			data = res.json()
			rows = gog_webscrape(data)

		list_of_data = arrange_data(rows, list_of_data)

	return list_of_data
