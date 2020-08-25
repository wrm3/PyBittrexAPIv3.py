################################################################################
# Imports #
################################################################################

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging
import time
import decimal


################################################################################
# External Local Imports #
################################################################################

from loc_bittrex_v3 import bittrex_api3, TRADE_FEE


################################################################################
# Local Imports #
################################################################################


################################################################################
# Variables #
################################################################################

lib_display_lvl = 0
lib_debug_lvl = 0


################################################################################
# Code #
################################################################################

#<=====>#


def dec(val):
	if val is None:
		val = 0
	else:
		val = decimal.Decimal(str(val))
	return val


#<=====>#


def logger_setup(logger_name, log_file, level=logging.WARNING):
	l = logging.getLogger(logger_name)

	formatter  = logging.Formatter('\n\n%(asctime)s - %(levelname)s: %(message)s')

	filedateformat = '{:%Y-%m-%d}'.format(datetime.now())
	log_file_name = 'logs/log_' + filedateformat + '_' + log_file
	print(log_file_name)
	dir_val(log_file_name)
	fileHandler = logging.FileHandler(log_file_name, mode='w')
	fileHandler.setFormatter(formatter)

	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)

	l.setLevel(level)
	l.addHandler(fileHandler)
	l.addHandler(streamHandler)


#<=====>#


logger_setup('error_log', 'error_log.log')
logger = logging.getLogger('error_log')


def secrets_get(upd_YN, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_secrets.secrets_get(upd_YN=" + upd_YN +", display_lvl=" + str(lib_display_lvl) + ", debug_lvl=" + str(lib_debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)


#	print("secrets_get(" + upd_YN + ")")
	secrets_file_directory = "settings/secrets.json"
	secrets_template = {
		"bittrex": {
			"bittrexKey": "BITTREX_API_KEY",
			"bittrexSecret": "BITTREX_SECRET"
		}
	}
	secrets_content = json_file_read(secrets_file_directory, secrets_template)
	if upd_YN == 'Y' and secrets_content == secrets_template:
		print("Please complete the `secrets.json` file in your `settings` directory")
		exit()
	return secrets_content


#<=====>#


secrets = secrets_get('Y')


#<=====>#


def dir_val(directory_string, debug_lvl=lib_debug_lvl):
	"""
	Check if a directory exists. If it doesn't, then create it.
	:param directory_string: The relative directory string (ex: settings/secrets.json)
	:type directory_string: str
	"""
	if not os.path.exists(os.path.dirname(directory_string)):
		try:
			os.makedirs(os.path.dirname(directory_string))
			print("Successfully created `{}` file directory".format(directory_string))
		except OSError as exception:  # Guard against race condition
			if exception.errno != errno.EEXIST:
				raise


#<=====>#


def json_file_read(directory_string, default_json_content=None):
	"""
	Get the contents of a JSON file. If it doesn't exist,
	create and populate it with specified or default JSON content.
	:param directory_string: The relative directory string (ex: settings/secrets.json)
	:type directory_string: str
	:param default_json_content: The content to populate a non-existing JSON file with
	:type default_json_content: dict, list
	"""
	dir_val(directory_string)
	try:
		with open(directory_string) as file:
			file_content = json.load(file)
			file.close()
			return file_content
	except (IOError, json.decoder.JSONDecodeError):
		with open(directory_string, "w") as file:
			if default_json_content is None:
				default_json_content = {}
			json.dump(default_json_content, file, indent=4)
			file.close()
			return default_json_content


#<=====>#
#def bittrex_order_handler(order_data, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
#	func_name = "lib_bittrex3.bittrex_order_handler("
#	func_name += "order_data"
#	func_name += ", display_lvl="   + str(display_lvl) + ""
#	func_name += ", debug_lvl="     + str(debug_lvl) + ")"
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print(func_name)
#
#	if debug_lvl >= 2: print(order_data)
#
#	od = {}
#	od['success']                    = order_data['success']
#	od['message']                    = order_data['message']
##	od['result']                     = order_data['result']
#
#	od['id']                         = None
#	od['marketsymbol']               = None
#	od['direction']                  = None
#	od['type']                       = None
#	od['quantity']                   = None
#	od['limit']                      = None
#	od['ceiling']                    = None
#	od['timeinforce']                = None
#	od['clientorderid']              = None
#	od['fillquantity']               = None
#	od['commission']                 = None
#	od['proceeds']                   = None
#	od['status']                     = None
#	od['createdat']                  = None
#	od['updatedat']                  = None
#	od['closedat']                   = None
#	od['cancelordertype']            = None
#	od['cancelorderuuid']            = None
#
#	if 'result' in order_data:
#		result = order_data['result']
#		if 'id'            in result: od['orderuuid']     = result['id']
#		if 'id'            in result: od['id']            = result['id']
#		if 'marketSymbol'  in result: od['marketsymbol']  = result['marketSymbol']
#		if 'direction'     in result: od['direction']     = result['direction']
#		if 'type'          in result: od['type']          = result['type']
#
#		if 'quantity'      in result:
#			if result['quantity']:    od['quantity']      = result['quantity']
#		if 'limit'         in result:
#			if result['limit']:       od['limit']         = result['limit']
#		if 'ceiling'       in result:
#			if result['ceiling']:     od['ceiling']       = result['ceiling']
#
#		if 'timeInForce'   in result: od['timeinforce']   = result['timeInForce']
#		if 'clientOrderId' in result: od['clientorderid'] = result['clientOrderId']
#		if 'fillQuantity'  in result: od['fillquantity']  = result['fillQuantity']
#		if 'commission'    in result: od['commission']    = result['commission']
#		if 'proceeds'      in result: od['proceeds']      = result['proceeds']
#		if 'status'        in result: od['status']        = result['status']
#
#		if 'createdAt'     in result:
#			if result['createdAt']:   od['createdat']     = datetime.strptime(result['createdAt'][:19], '%Y-%m-%dT%H:%M:%S')
#		if 'updatedAt'     in result:
#			if result['updatedAt']:   od['updatedat']     = datetime.strptime(result['updatedAt'][:19], '%Y-%m-%dT%H:%M:%S')
#		if 'closedAt'      in result:
#			if result['closedAt']:    od['closedat']      = datetime.strptime(result['closedAt'][:19], '%Y-%m-%dT%H:%M:%S')
#
#		if 'orderToCancel' in result:
#			orderToCancel = result['orderToCancel']
#			if 'type' in orderToCancel:
#				if orderToCancel['type']: od['cancelordertype'] = orderToCancel['type']
#			if'id'    in orderToCancel:
#				if orderToCancel['id']: od['cancelorderuuid'] = orderToCancel['id']
#
#	return od
#
#
##<=====>#


def bittrex_order_create(marketSymbol=None, direction=None, type=None, quantity=None, ceiling=None, limit=None, timeInForce=None, clientOrderId=None, useAwards=None, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_order_create("
	func_name += "marketSymbol="    + str(marketSymbol) + ""
	func_name += ", direction="     + str(direction) + ""
	func_name += ", type="          + str(type) + ""
	func_name += ", quantity="      + str(quantity) + ""
	func_name += ", ceiling="       + str(ceiling) + ""
	func_name += ", limit="         + str(limit) + ""
	func_name += ", timeInForce="   + str(timeInForce) + ""
	func_name += ", clientOrderId=" + str(clientOrderId) + ""
	func_name += ", useAwards="     + str(useAwards) + ""
	func_name += ", display_lvl="   + str(display_lvl) + ""
	func_name += ", debug_lvl="     + str(debug_lvl)
	func_name += ")"

	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)


	if marketSymbol is None:
#		marketSymbol: string
#		unique symbol of the market this order is being placed on
		print(func_name)
		print('MARKETSYMBOL is missing')
		exit()

	if direction not in ('BUY','SELL'):
#		direction: string  BUY, SELL
#		order direction
		print(func_name)
		print('DIRECTION has an incorrect value : ' + str(direction))
		exit()

	if type not in ('LIMIT', 'MARKET', 'CEILING_LIMIT', 'CEILING_MARKET'):
		print(func_name)
		print('TYPE has an incorrect value : ' + str(type))
		exit()

	if (quantity is None or quantity == 0) and type in ('LIMIT', 'MARKET'):
#		quantity: number (double)
#		quantity (optional, must be included for non-ceiling orders and excluded for ceiling orders)
		print(func_name)
		print('LIMIT & MARKET Orders require a quantity value : ' + str(quantity))
		exit()

	if (ceiling is None or ceiling == 0) and type in ('CEILING_LIMIT', 'CEILING_MARKET'):
#		ceiling: number (double)
#		ceiling (optional, must be included for ceiling orders and excluded for non-ceiling orders)
		print(func_name)
		print('CEILING Orders require a ceiling value : ' + str(ceiling))
		exit()

	if (limit is None or limit == 0) and type in ('MARKET'):
#		limit: number (double)
#		limit (optional, must be included for LIMIT orders and excluded for MARKET orders)
		print(func_name)
		print('MARKET Orders require a limit value : ' + str(limit))
		exit()

#	if timeInForce not in ('GOOD_TIL_CANCELLED', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL', 'POST_ONLY_GOOD_TIL_CANCELLED', 'BUY_NOW'):
	if timeInForce not in ('GOOD_TIL_CANCELLED', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL'):
#		timeInForce: string  GOOD_TIL_CANCELLED, IMMEDIATE_OR_CANCEL, FILL_OR_KILL, POST_ONLY_GOOD_TIL_CANCELLED, BUY_NOW
#		time in force
		print(func_name)
		print('timeInForce has an incorrect value : ' + str(timeInForce))
		exit()


	od = bittrex_api3.prv_post_orders_v3(
			marketSymbol=marketSymbol,
			direction=direction,
			type=type,
			quantity=quantity,
			ceiling=ceiling,
			limit=limit,
			timeInForce=timeInForce,
			clientOrderId=clientOrderId,
			useAwards=useAwards
			)

#	print(order_data)
#
#	od = {}
#	if order_data['success']:
#		od =  bittrex_order_handler(order_data, display_lvl=display_lvl, debug_lvl=debug_lvl)
#	else:
##		{'success': False, 'message': "''", 'result': {'code': 'DUST_TRADE_DISALLOWED_MIN_VALUE'}, 'status_code': 400}
#		print(func_name)
#		print(order_data)
##		exit()
#		od = order_data

	return od


#<=====>#


def bittrex_order_get(OrderUuid, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_order_get("
	func_name += "OrderUuid="    + str(OrderUuid) + ""
	func_name += ", display_lvl="   + str(display_lvl) + ""
	func_name += ", debug_lvl="     + str(debug_lvl)
	func_name += ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	od = bittrex_api3.prv_get_orders_v3(OrderUuid)
#	if debug_lvl >= 2: print(order_data)

#	od = {}
#	if order_data['success']:
#		od =  bittrex_order_handler(order_data, display_lvl=display_lvl, debug_lvl=debug_lvl)
#	else:
#		od = order_data

	return od


#<=====>#


def bittrex_orders_closed_get(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_orders_closed_get("
	func_name += "  display_lvl="   + str(display_lvl) + ""
	func_name += ", debug_lvl="     + str(debug_lvl)
	func_name += ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

# prv_get_orders_closed_v3(self, marketSymbol=None, nextPageToken=None, prevPageToken=None, pageSize=None, startDate=None, endDate=None)
	sd = '2020-01-01T00:00:00.00Z'
	ms = 'BTC-USD'
	ps=200

	ol = []
	od = bittrex_api3.prv_get_orders_closed_v3(pageSize=ps)
	print(od.keys())
	if 'result' in od:
		print(type(od['result']))
		if type(od['result']) ==list:
			ol.extend(od['result'])
			ol_len = len(ol)
			print(len(ol))
			print(ol[-1])

		more = True
		while more:
			npt = ol[-1]['id']
			print(npt)
			# 429 Errors
			time.sleep(4)
			od = bittrex_api3.prv_get_orders_closed_v3(nextPageToken=npt, pageSize=ps)
			if 'result' in od:
				print(type(od['result']))
				if type(od['result']) ==list:
					ol.extend(od['result'])
					print(len(ol))
				if len(ol) == ol_len:
					more = False
				else:
					ol_len = len(ol)
			print(ol[-1])

	print(len(ol))

	orders = dict()
	for o in ol:
		orders[o['id']] = o

	sorted_orders = dict()
	for k, v in sorted(orders.items(), key=lambda e: e[1]["createdAt"]):
		sorted_orders[k] = v

	return sorted_orders


#<=====>#


def bittrex_order_cancel(OrderUuid, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex.bittrex_order_cancel("
	func_name += "OrderUuid="    + str(OrderUuid) + ""
	func_name += ", display_lvl="   + str(display_lvl) + ""
	func_name += ", debug_lvl="     + str(debug_lvl)
	func_name += ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)


	od = bittrex_api3.prv_delete_orders_v3(OrderUuid)
#	print(order_data)
#
#	od = {}
#	if order_data['success']:
#		od =  bittrex_order_handler(order_data, display_lvl=display_lvl, debug_lvl=debug_lvl)
#	else:
#		od = order_data

	return od


#<=====>#


def bittrex_get_addresses(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_addresses(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	addr_data = None
	cnt = 0
	try:
		while addr_data is None:
			addr_data = bittrex_api3.prv_get_addresses_v3()
			if addr_data['success'] == False or addr_data['result'] is None: addr_data = None
			if addr_data is None:
				cnt += 1
				print(func_name + ' - addr_data - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - addr_data - errord.')
		exit()

	d_addresses = dict()
	for address in addr_data['result']:
		d_addresses[address['currencySymbol']] = address

	return d_addresses


#<=====>#


def bittrex_request_an_address(c, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_request_an_address(c=" + c + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	##### For whatever reason this often returns None, so skip repeat attempts for now
	addr_data = bittrex_api3.prv_post_addresses_v3(currencySymbol=c)

	ad = ''
	adt = ''

	if addr_data['success'] == False or addr_data['result'] is None:
		if 'cryptoAddress' in addr_data['result']:
			ad = addr_data['result']['cryptoAddress']
			adt = addr_data['result']['cryptoAddressTag']

	return ad, adt


#<=====>#


#app_buy.mkt_eval
def bittrex_get_balance(c, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_balance(c=" + str(c) + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	bal_data = None
	cnt = 0
	try:
		while bal_data is None:
			bal_data = bittrex_api3.prv_get_balances_v3(c)
			if bal_data['success'] == False or bal_data['result'] is None: bal_data = None
			if bal_data is None:
				cnt += 1
				print(func_name + ' retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' errord.')
		exit()

#	print(bal_data)
	return bal_data


#<=====>#


def bittrex_get_balances(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_balances(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	bal_data = None
	cnt = 0
	try:
		while bal_data is None:
			bal_data = bittrex_api3.prv_get_balances_v3()
			if bal_data['success'] == False or bal_data['result'] is None: bal_data = None
			if bal_data is None:
				cnt += 1
				print(func_name + ' - bal_data -  retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - bal_data -  errord.')
		exit()

	d_balances = dict()
	for balance in bal_data['result']:
		d_balances[balance['currencySymbol']] = balance

	return d_balances


#<=====>#


def bittrex_get_currencies(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_currencies(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	cnt = 0
	currencies = None
	try:
		while currencies is None:
			currencies = bittrex_api3.pub_get_currencies_v3()
			if currencies['success'] == False or currencies['result'] is None: currencies = None
			if currencies is None:
				cnt += 1
				print(func_name + ' - currencies - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - currencies - errord.')
		exit()

	d_currencies = dict()
	for currency in currencies['result']:
		d_currencies[currency['symbol']] = currency

	return d_currencies


#<=====>#


def bittrex_get_markets(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_markets(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	cnt = 0
	markets = None
	try:
		while markets is None:
			markets = bittrex_api3.pub_get_markets_v3()
			if markets['success'] == False or markets['result'] is None: markets = None
			if markets is None:
				cnt += 1
				print(func_name + ' - markets - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - markets - errord.')
		exit()

	d_markets = dict()
	for market in markets['result']:
		if 'US' not in market['prohibitedIn']:
			d_markets[market['symbol']] = market

	return d_markets


#<=====>#


def bittrex_get_summaries(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_summaries(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	cnt = 0
	summaries = None
	try:
		while summaries is None:
			summaries = bittrex_api3.pub_get_markets_summaries_v3()
			if summaries['success'] == False or summaries['result'] is None: summaries = None
			if summaries is None:
				cnt += 1
				print(func_name + ' - summaries - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - summaries - errord.')
		exit()

	d_summaries = dict()
	for summary in summaries['result']:
		d_summaries[summary['symbol']] = summary

	return d_summaries


#<=====>#


def bittrex_get_tickers(display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_tickers(display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	cnt = 0
	tick_data = None
	try:
		while tick_data is None:
			tick_data = bittrex_api3.pub_get_markets_tickers_v3()
			if tick_data['success'] == False or tick_data['result'] is None: tick_data = None
			if tick_data is None:
				cnt += 1
				print(func_name + ' - tick_data - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - tick_data - errord.')
		exit()

	d_tickers = dict()
	for ticker in tick_data['result']:
		d_tickers[ticker['symbol']] = ticker

	return d_tickers


#<=====>#


def bittrex_get_tickers_tpf(tpf, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_tickers_tpf(tpf=" + tpf + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	cnt = 0
	tick_data = None
	try:
		while tick_data is None:
			tick_data = bittrex_api3.pub_get_markets_tickers_v3(tpf)
			if tick_data['success'] == False or tick_data['result'] is None: tick_data = None
			if tick_data is None:
				cnt += 1
				print(func_name + ' - tick_data - retry' + str(cnt))
				time.sleep(5)
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' - tick_data - errord.')
		exit()

#	print(tick_data)
#	exit()
	last = dec(tick_data['result']['lastTradeRate'])
	bid  = dec(tick_data['result']['bidRate'])
	ask  = dec(tick_data['result']['askRate'])

	return last, bid, ask


#<=====>#


def bittrex_get_hist(tpf, freq, recs=500, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_hist(tpf=" + tpf + ", freq=" + freq + ", recs=" + str(recs) + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	valid_freq_list = ['MINUTE_1','MINUTE_5','HOUR_1','DAY_1']

	today_date = date.today()
	if freq in valid_freq_list:
		if recs < 500:
			recs = 500
	elif freq == 'oneMin':
		freq = 'MINUTE_1'
		if recs < 500:
			recs = 500
	elif freq == 'fiveMin':
		freq = 'MINUTE_5'
		if recs < 500:
			recs = 500
	elif freq == 'hour':
		freq = 'HOUR_1'
		if recs < 500:
			recs = 500
	elif freq == 'Day':
		freq = 'DAY_1'
		if recs < 500:
			recs = 500
	else:
		print(func_name)
		print('invalid freq - forcing to 1 Hour')
		freq = 'HOUR_1'
		if recs < 500:
			recs = 500

	if debug_lvl >= 3: print('freq=' + freq)
	if debug_lvl >= 3: print('recs=' + str(recs))

	hist_data = []
	hist_dict = {}

	hist = None
	cnt = 0
	try:
		while hist is None:
			actv_msg = 'bittrex_api3.get_candles'
			hist = bittrex_api3.pub_get_markets_candles_v3(marketSymbol = tpf, candleInterval = freq)
			if hist['success'] == False or hist['result'] is None: hist = None
			if hist is None:
				cnt += 1
				print(func_name + ' - recent - retry' + str(cnt) + ' - ' + tpf + ' - ' + freq)
				time.sleep(5)
			else:
				if hist is not None:
					hist = hist['result']
					if debug_lvl >= 3: print(hist[-1])
					for row in hist:
						hist_row = {}
						hist_row['time']         = row['startsAt'][:19]
						hist_row['open']         = float(row['open'])
						hist_row['high']         = float(row['high'])
						hist_row['low']          = float(row['low'])
						hist_row['close']        = float(row['close'])
						hist_row['volume']       = float(row['volume'])
						hist_row['basevolume']   = float(row['volume'])
						hist_dict[hist_row['time']] = hist_row
				else:
					obj_ta['success_tf'] = False
					print(func_name + ' - ' + tpf + ' - ' + freq + ' - ' + actv_msg + ' failed.')
	except Exception:
		logger.exception(Exception)
		print(Exception)
		print(func_name + ' errord.')
		print('error with ' + func_name + '(' + tpf + ', ' + freq + ')')
		play_beep()
		exit()

	hist_date = today_date
	while len(hist_dict) < recs:
		if debug_lvl >= 3: print('len(hist_dict):'+str(len(hist_dict)))
		if freq == 'MINUTE_1':
			hist_date -= timedelta(days=1)
		elif freq == 'MINUTE_5':
			hist_date -= timedelta(days=1)
		elif freq == 'HOUR_1':
			hist_date -= timedelta(months=1)
		elif freq == 'DAY_1':
			hist_date -= timedelta(years=1)

		if debug_lvl >= 3: print('requesting candles - new')
		hist = None
		cnt = 0

		if tpf == 'USD-CELO': print('data_date : ' + str(hist_date))

		sd_yyyy = str(hist_date.year)
		sd_mm = str(hist_date.month)
		sd_dd = str(hist_date.day)

		if debug_lvl >= 3: print('')
		if debug_lvl >= 3: print('')
		if debug_lvl >= 3: print('sd_yyyy : ' + str(sd_yyyy))
		if debug_lvl >= 3: print('sd_mm   : ' + str(sd_mm))
		if debug_lvl >= 3: print('sd_dd   : ' + str(sd_dd))
		if debug_lvl >= 3: print('')
		if debug_lvl >= 3: print('')

		try:
			while hist is None:
				actv_msg = 'bittrex_api3.get_candles'
				hist = bittrex_api3.pub_get_markets_candles_v3(marketSymbol = tpf, candleInterval = freq, yyyy = sd_yyyy, mm = sd_mm, dd = sd_dd)
				if hist['success'] == False or hist['result'] is None: hist = None
				if hist is None:
					cnt += 1
					print(func_name + ' - historical - retry' + str(cnt) + ' - ' + tpf + ' - ' + freq + ' - ' + str(sd_yyyy) + ' - ' + str(sd_mm) + ' - ' + str(sd_dd))
					time.sleep(5)
				else:
					if hist is not None:
						hist = hist['result']
						if debug_lvl >= 3: print(hist[-1])
						for row in hist:
							hist_row = {}
							hist_row['time']         = row['startsAt'][:19]
							hist_row['open']         = float(row['open'])
							hist_row['high']         = float(row['high'])
							hist_row['low']          = float(row['low'])
							hist_row['close']        = float(row['close'])
							hist_row['volume']       = float(row['volume'])
							hist_row['basevolume']   = float(row['volume'])
							hist_dict[hist_row['time']] = hist_row
					else:
						obj_ta['success_tf'] = False
						print(func_name + ' - ' + tpf + ' - ' + freq + ' - ' + actv_msg + ' failed.')
		except Exception:
			logger.exception(Exception)
			print(Exception)
			print(func_name + ' errord.')
			print('error with ' + func_name + '(' + tpf + ', ' + freq + ')')
			play_beep()
			exit()

	hist_dict_sort = {}
	for d in sorted(hist_dict):
		hist_dict_sort[d] = hist_dict[d]

	for k,v in hist_dict_sort.items():
		v['time'] = datetime.strptime(v['time'], '%Y-%m-%dT%H:%M:%S')
		hist_data.append(v)

	if debug_lvl >= 3:
		print('hist_data_new first:')
		print(hist_data[0])
		print('hist_data_new last:')
		print(hist_data[-1])
		print('hist_data_new length:')
		print(len(hist_data))

	return hist_data


#<=====>#


#app_buy.buy_tp_loop
#app_sell.sell_eval
#app_sell.sell_eval_new
def bittrex_get_prices_usd(bs, mc, tc, price, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_bittrex3.bittrex_get_price_usd(bs=" + bs + ", mc=" + mc + ", tc=" + tc + ", price=" + str(price)+ ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

	price = dec(price)
	tpf = mc + '-USD'

	if mc == 'USD':
		mc_price_usd = 1
		tc_price_usd = price
	else:
		last, bid, ask = bittrex_get_tickers_tpf(tpf, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl)

		if bs == 'buy':
			mc_2_usd_factor  = ask
		elif bs == 'sell':
			mc_2_usd_factor  = bid
		else:
			mc_2_usd_factor = 1

		mc_price_usd = round(mc_2_usd_factor, 8)
		tc_price_usd = round(mc_2_usd_factor * price, 8)

	return mc_price_usd, tc_price_usd


#<=====>#


# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
# Alias   Description
# B       business day frequency
# C       custom business day frequency (experimental)
# D       calendar day frequency
# W       weekly frequency
# M       month end frequency
# BM      business month end frequency
# CBM     custom business month end frequency
# MS      month start frequency
# BMS     business month start frequency
# CBMS    custom business month start frequency
# Q       quarter end frequency
# BQ      business quarter endfrequency
# QS      quarter start frequency
# BQS     business quarter start frequency
# A       year end frequency
# BA      business year end frequency
# AS      year start frequency
# BAS     business year start frequency
# BH      business hour frequency
# H       hourly frequency
# T, min  minutely frequency
# S       secondly frequency
# L, ms   milliseonds
# U, us   microseconds
# N       nanoseconds


#<=====>#


#def ta_get_candles_df(hist, freq, rfreq, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
#	func_name = "lib_ta.ta_get_candles_df(hist, freq=" + freq + ", rfreq=" + rfreq + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print(func_name)
#
##	print(func_name)
#
#	actv_msg = 'resampling'
#
##	if rfreq == '1T':
##		freq = 'oneMin'
##		freq = 'MINUTE_1'
##	elif rfreq == '3T':
##		freq = 'oneMin'
##		freq = 'MINUTE_1'
##	elif rfreq == '5T':
##		freq = 'fiveMin'
##		freq = 'MINUTE_5'
##	elif rfreq == '10T':
##		freq = 'fiveMin'
##		freq = 'MINUTE_5'
##	elif rfreq == '15T':
##		freq = 'fiveMin'
##		freq = 'MINUTE_5'
##	elif rfreq == '30T':
##		freq = 'thirtyMin'
##		freq = 'MINUTE_5'
##	elif rfreq == '60T' or rfreq == '1H':
##		freq = 'hour'
##		freq = 'HOUR_1'
##	elif rfreq == '2H':
##		freq = 'hour'
##		freq = 'HOUR_1'
##	elif rfreq == '3H':
##		freq = 'hour'
##		freq = 'HOUR_1'
##	elif rfreq == '6H':
##		freq = 'hour'
##		freq = 'HOUR_1'
##	elif rfreq == '12H':
##		freq = 'hour'
##		freq = 'HOUR_1'
##	elif rfreq == '1D':
##		freq = 'day'
##		freq = 'DAY_1'
##	elif rfreq == '3D':
##		freq = 'day'
##		freq = 'DAY_1'
##	elif rfreq == '7D':
##		freq = 'day'
##		freq = 'DAY_1'
##	else:
##		print('freq : ' + freq)
##		exit()
#
##	print('freq : ' + freq)
#
#
#	try:
#		if debug_lvl >= 3: print('converting to dataframe')
#		df = to_dataframe(hist[freq])
#
#		if debug_lvl >= 3: print('before resampling - freq=' + freq + ' - rfreq=' + rfreq)
#		if debug_lvl >= 3: print(df.head(10))
#		if debug_lvl >= 3: print(df.tail(10))
#
#
#		if debug_lvl >= 3: print(df.tail(10))
#
#		if debug_lvl >= 3: print('resampling')
#		df = resample(df, rfreq)
#
#		if debug_lvl >= 3: print('after resampling - freq=' + freq + ' - rfreq=' + rfreq)
#		if debug_lvl >= 3: print(df.head(10))
#		if debug_lvl >= 3: print(df.tail(10))
#
#		if debug_lvl >= 3: print(df.tail(10))
#
##		if debug_lvl >= 3: print('filling nan')
##		# volume should always be 0 (if there were no trades in this interval)
##		df['volume'] = df['volume'].fillna(0.0)
##		# ie pull the last close into this close
##		df['close']  = df['close'].fillna(method='ffill')
##		# now copy the close that was pulled down from the last timestep into this row, across into o/h/l
##		df['open']   = df['open'].fillna(df['close'])
##		df['low']    = df['low'].fillna(df['close'])
##		df['high']   = df['high'].fillna(df['close'])
##		if debug_lvl >= 3: print(df.tail(10))
##		if debug_lvl >= 3: print('deleting')
##		df = df[df.volume != 0]
##		if debug_lvl >= 3: print(df.tail(10))
#
#
#	except Exception:
#		print('error with ' + func_name + '(' + rfreq + ')')
#		logger.exception(Exception)
#		print(Exception)
#		play_beep()
#		exit()
#
#	return df


##<=====>#
#
#
##app_buy.sell_order
#def bittrex_old_sell_limit(tp, cnt, price, debug_lvl=lib_debug_lvl):
#	func_name = "lib_bittrex.bittrex_old_sell_limit(tp=" + tp + ", cnt=" + str(cnt) + ", price=" + str(price) + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print(func_name)
#
#	c1 = tp.split('-')[0]
#	c2 = tp.split('-')[1]
#	if c1 == 'USD':
#		newprice = dec(round(price, 3))
#		print('Rounding USD price from ' + str(dec(price)) + ' to ' + str(dec(newprice)))
#		price = newprice
#
#	success_tf = True
#
#	actv_msg = 'Calling bittrex_api1.sell_limit...'
#
#	if success_tf == True:
#		sell_data = bittrex_api1.sell_limit(tp, cnt, price)
#		if sell_data is not None:
#
#			if sell_data['success'] == True:
#				success_tf = True
#				print(sell_data)
#			else:
#				success_tf = False
#				print('tp    : ' + tp)
#				print('cnt   : ' + str(cnt))
#				print('price : ' + str(price))
#				print(sell_data)
#
#			if sell_data['success'] == False and sell_data['message'] == 'RATE_PRECISION_NOT_ALLOWED':
#				sell_data = bittrex_api1.sell_limit(tp, cnt, round(price,3))
#				if sell_data['success'] == True:
#					success_tf = True
#					print(sell_data)
#				else:
#					success_tf = False
#					print(func_name + ' ' + actv_msg + ' failed.')
#
#		else:
#			success_tf = False
#			print(func_name + ' ' + actv_msg + ' failed.')
#
#
#	if success_tf == True:
#		sell_data['success_tf'] = True
#		return sell_data
#	else:
##		sell_data = {}
#		sell_data['success_tf'] = False
#		return sell_data
#
#
##<=====>#
#
#
##app_buy.buy_order
#def bittrex_old_buy_limit(tp, cnt, price, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
#	func_name = "lib_bittrex.bittrex_old_buy_limit(tp=" + tp + ", cnt=" + str(cnt) + ", price=" + str(price) + ", display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print('')
#	if debug_lvl >= 1: print(func_name)
#
#	success_tf = True
#
#	actv_msg = 'Calling bittrex_api1.buy_limit...'
##	if debug_lvl >= 1 : print(func_name + ' ' + actv_msg)
#
##	if success_tf == True:
##		buy_data = bittrex_api1.buy_limit(tp, cnt, price)
##		if buy_data is not None:
##			success_tf = True
##			print(buy_data)
##		else:
##			success_tf = False
##			print(func_name + ' ' + actv_msg + ' failed.')
#
#
#	if success_tf == True:
#		buy_data = bittrex_api1.buy_limit(tp, cnt, price)
#		if buy_data is not None:
#
#			if buy_data['success'] == True:
#				success_tf = True
#				print(buy_data)
#			else:
#				success_tf = False
#				print('tp    : ' + tp)
#				print('cnt   : ' + str(cnt))
#				print('price : ' + str(price))
#				print(buy_data)
#
#			if buy_data['success'] == False and buy_data['message'] == 'RATE_PRECISION_NOT_ALLOWED':
#				buy_data = bittrex_api1.buy_limit(tp, cnt, round(price,3))
#				if buy_data['success'] == True:
#					success_tf = True
#					print(buy_data)
#				else:
#					success_tf = False
#					print(func_name + ' ' + actv_msg + ' failed.')
#
#		else:
#			success_tf = False
#			print(func_name + ' ' + actv_msg + ' failed.')
#
#
#	if success_tf == True:
#		buy_data['success_tf'] = True
#		return buy_data
#	else:
#		buy_data = {}
#		buy_data['success_tf'] = False
#		return buy_data
#
#
##<=====>#


