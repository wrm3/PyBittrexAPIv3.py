"""
	Developed from the Original Work of Eric Somdahl @ https://raw.githubusercontent.com/ericsomdahl/python-bittrex/master/bittrex/bittrex.py
	See https://bittrex.github.io/api/v3
"""

#import urllib.parse
import winsound


#from lib_secrets import secrets

import time
import hmac
import hashlib
import sys
import json

try:
	from urllib import urlencode
except ImportError:
	from urllib.parse import urlencode

try:
	from Crypto.Cipher import AES
except ImportError:
	encrypted = False
else:
	import getpass
	import ast
	import json

	encrypted = True

import requests



TRADE_FEE = 0.0025



def beep(debug_lvl=0):
	frequency = 2500  # Set Frequency To 2500 Hertz
	duration = 1000  # Set Duration To 1000 ms == 1 second
	winsound.Beep(frequency, duration)



def encrypt(api_key, api_secret, export=True, export_fn='settings/secrets.json'):
	print('def encrypt')
	cipher = AES.new(getpass.getpass(
		'Input encryption password (string will not show)'))
	api_key_n = cipher.encrypt(api_key)
	api_secret_n = cipher.encrypt(api_secret)
	api = {'key': str(api_key_n), 'secret': str(api_secret_n)}
	if export:
		with open(export_fn, 'w') as outfile:
			json.dump(api, outfile)
	return api



class Bittrex(object):
	"""
	Used for requesting Bittrex with API key and API secret
	"""


#	def __init__(self, api_key, api_secret, calls_per_second=1, dispatch=using_requests):
	def __init__(self, api_key, api_secret, calls_per_second=1):
		self.api_key = str(api_key) if api_key is not None else ''
		self.api_secret = str(api_secret) if api_secret is not None else ''
#		self.dispatch = dispatch
		self.call_rate = 1.0 / calls_per_second
		self.last_call = None
#		self.api_version = api_version



	def decrypt(self):
		print('def Bittrex.decrypt')
		if encrypted:
			cipher = AES.new(getpass.getpass(
				'Input decryption password (string will not show)'))
			try:
				if isinstance(self.api_key, str):
					self.api_key = ast.literal_eval(self.api_key)
				if isinstance(self.api_secret, str):
					self.api_secret = ast.literal_eval(self.api_secret)
			except Exception:
				pass
			self.api_key = cipher.decrypt(self.api_key).decode()
			self.api_secret = cipher.decrypt(self.api_secret).decode()
		else:
			raise ImportError('"pycrypto" module has to be installed')



	def wait(self):
		print('def Bittrex.wait')
		if self.last_call is None:
			self.last_call = time.time()
		else:
			now = time.time()
			passed = now - self.last_call
			if passed < self.call_rate:
				# print("sleep")
				time.sleep(self.call_rate - passed)
			self.last_call = time.time()



	def urlbuild(self, opts):
		firstYN = 'Y'
		retstr = ''
		optskeylist = list(opts.keys())
		if opts:
			for optskey in optskeylist:
				if firstYN == 'Y':
					firstYN = 'N'
					retstr += '?'+ optskey + '=' + opts[optskey]
				else:
					retstr += '&'+ optskey + '=' + opts[optskey]
		return retstr



	def _public_api_query(self, sub_path=None, options=None):
		print('def Bittrex._public_api_query')
		"""
		Queries Bittrex
		:param request_url: fully-formed URL to request
		:type options: dict
		:return: JSON response from Bittrex
		:rtype : dict
		"""
		if not options: options = {}
		request_url = 'https://api.bittrex.com/v3{path}?'
		request_url = request_url.format(path=sub_path)
		request_url += urlencode(options)
		print('request_url : ' + request_url)
		try:
			apisign = hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()
			self.wait()
		except Exception:
			error_handler("unknown", [], True)
			logger.exception(Exception)
			exit()
		return requests.get(
			request_url,
			headers={"apisign": apisign},
			timeout=10
		).json()




	def _private_api_query(self, http_meth, sub_path, options=None):
		print('def Bittrex.api_query(http_meth=' + http_meth + ', sub_path=' + sub_path + ', options=' + json.dumps(options) + ')')

		api_key = self.api_key
#		print('api_key                    : ' + api_key)


		api_timestamp = str(int(time.time() * 1000))
#		print('api_timestamp              : ' + api_timestamp)


		payload = ''
		if http_meth == 'GET':
			if options and options != '':
#				request_url = "https://api.bittrex.com/v3" + str(sub_path) + str('?') + str(urllib.parse.urlencode(options))
				request_url = "https://api.bittrex.com/v3" + str(sub_path) + self.urlbuild(options)
			else:
				request_url = "https://api.bittrex.com/v3" + str(sub_path)

		elif http_meth == "HEAD":
			request_url = "https://api.bittrex.com/v3" + str(sub_path)
			payload = ''

		elif http_meth == "POST":
			request_url = "https://api.bittrex.com/v3" + str(sub_path)
			payload = json.dumps(options)

		elif http_meth == "DELETE":
			if options:
				delete_key = list(options.values())[0]
			else:
				delete_key = ''
			request_url = "https://api.bittrex.com/v3" + str(sub_path) + str('/') + delete_key
			payload = ''

		else:
			request_url = "https://api.bittrex.com/v3" + str(sub_path)
			payload = ''

		print('request_url                : ' + request_url)
#		print('payload                    : ' + payload)


		contentHash = hashlib.sha512(payload.encode()).hexdigest()
#		print('contentHash                : ' + contentHash)

		pre_sign = api_timestamp + request_url + http_meth + contentHash
#		print('pre_sign                   : ' + pre_sign)

		signature = hmac.new(self.api_secret.encode(), pre_sign.encode(), hashlib.sha512).hexdigest()
#		print('signature                  : ' + signature)

		headers = {
					'Api-Key': api_key, 
					'Api-Timestamp': api_timestamp, 
					'Api-Content-Hash': contentHash, 
					'Api-Signature': signature, 
					'Content-Type': 'application/json', 
					'Accept': 'application/json'
					}
#		print('headers                    : ' + json.dumps(headers))

		if http_meth == 'GET':
			r = requests.get(url = request_url, params = payload, headers = headers)
		if http_meth == 'HEAD':
			r = requests.get(url = request_url, params = payload, headers = headers)
		elif http_meth == "POST":
			r = requests.post(url = request_url, data=json.dumps(options), headers = headers)
		elif http_meth == "DELETE":
			r = requests.delete(url = request_url, headers = headers)
		else:
			r = requests.get(url = request_url, params = payload, headers = headers)

#		Property/Method			Description
#		--------------------------------------------------------------------------------------------------------------------------------
#		apparent_encoding		Returns the apparent encoding
#		close()					Closes the connection to the server
#		content					Returns the content of the response, in bytes
#		cookies					Returns a CookieJar object with the cookies sent back from the server
#		elapsed					Returns a timedelta object with the time elapsed from sending the request to the arrival of the response
#		encoding				Returns the encoding used to decode r.text
#		headers					Returns a dictionary of response headers
#		history					Returns a list of response objects holding the history of request (url)
#		is_permanent_redirect	Returns True if the response is the permanent redirected url, otherwise False
#		is_redirect				Returns True if the response was redirected, otherwise False
#		iter_content()			Iterates over the response
#		iter_lines()			Iterates over the lines of the response
#		json()					Returns a JSON object of the result (if the result was written in JSON format, if not it raises an error)
#		links					Returns the header links
#		next					Returns a PreparedRequest object for the next request in a redirection
#		ok						Returns True if status_code is less than 200, otherwise False
#		raise_for_status()		If an error occur, this method returns a HTTPError object
#		reason					Returns a text corresponding to the status code
#		request					Returns the request object that requested this response
#		status_code				Returns a number that indicates the status (200 is OK, 404 is Not Found)
#		text					Returns the content of the response, in unicode
#		url						Returns the URL of the response

#		print(r)
#		print('status_code : ' + str(r.status_code))

		data = r.json()
		print(type(data))
		if isinstance(data, list):
			status_code = r.status_code
			data = dict()
			data['status_code'] = r.status_code
		if isinstance(data, dict):
			data['status_code'] = r.status_code

		return data



### Works
	def prv_get_account(self):
		print('def Bittrex.prv_get_account')
		"""
		Retrieve information for the account associated with the request. 
		For now, it only echoes the subaccount if one was specified in the header, 
		which can be used to verify that one is operating on the intended account. 
		More fields will be added later.

		3.0		GET		https://api.bittrex.com/v3/account

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
			 				{
							"subaccountId": "string (uuid)",
							"accountId": "string (uuid)"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/account'
			)



### Works
	def prv_get_account_volume(self):
		print('def Bittrex.prv_get_account_volume')
		"""
		Get 30 day volume for account
		3.0		GET		https://api.bittrex.com/v3/account/volume
		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
			 				{
								"updated": "string (date-time)",
								"volume30days": "number (double)"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/account/volume'
			)



### Works
	def prv_get_addresses(self, currencySymbol=None):
		"""
		List deposit addresses that have been requested or provisioned.
		3.0		GET		https://api.bittrex.com/v3/addresses
		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
			 				{
								"status": "string",
								"currencySymbol": "string",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string"
							}
						]
			}
		"""
		if currencySymbol == None:
			path = '/addresses'
		else:
			path = '/addresses/' + currencySymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = path
			)



### Works
	def prv_get_balances(self, currencySymbol=None):
		"""
		3.0		GET		https://api.bittrex.com/v3/balances
		List account balances across available currencies. Returns a Balance entry 
		for each currency for which there is either a balance or an address.

		3.0		GET		https://api.bittrex.com/v3/balances/{currencySymbol}
		List account balances across available currencies. Returns a Balance entry 
		for each currency for which there is either a balance or an address.

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
			 				{
								"currencySymbol": "string",
								"total": "number (double)",
								"available": "number (double)",
								"updatedAt": "string (date-time)"
							},
							...
						]
			}
		"""
		if currencySymbol == None:
			path = '/balances'
		else:
			path = '/balances/' + currencySymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = path
			)



### Works
	def pub_get_currencies(self, currencySymbol=None):
		print('def Bittrex.pub_get_currencies')
		"""
		List currencies.

		3.0		GET		https://api.bittrex.com/v3/currencies
		3.0		GET		https://api.bittrex.com/v3/currencies/{currencySymbol}

		Parameters
			currencySymbol: string
			optional
			in path
			symbol of the currency to retrieve the deposit address for

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"symbol": "string",
								"name": "string",
								"coinType": "string",
								"status": "string",
								"minConfirmations": "integer (int32)",
								"notice": "string",
								"txFee": "number (double)",
								"logoUrl": "string",
								"prohibitedIn": [
									"string"
									]
							},
							....
						]
			}
		"""
		if currencySymbol == None:
			path = '/currencies'
		else:
			path = '/currencies/' + currencySymbol
		return self._public_api_query(sub_path = path)



### Works
	def prv_get_deposits_open(self, status=None, currencySymbol=None):
		"""
		List open deposits. Results are sorted in inverse order of UpdatedAt, and are 
		limited to the first 1000.

		3.0		GET		https://api.bittrex.com/v3/deposits/open

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							},
							....
						]
			}
		"""
		opts = {}
		if status:
			opts['status'] = status
		if status:
			opts['currencySymbol'] = currencySymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/deposits/open',
			options=opts
			)



### Works
	def prv_get_deposits_closed(self, status=None, currencySymbol=None, nextPageToken=None, prevPageToken=None, pageSize=None, startDate=None, endDate=None):
		"""
		List closed deposits. StartDate and EndDate filters apply to the CompletedAt 
		field. Pagination and the sort order of the results are in inverse order of 
		the CompletedAt field.

		3.0		GET		https://api.bittrex.com/v3/deposits/closed

		Parameters
			status: string  COMPLETED, ORPHANED, INVALIDATED 
			in query
			filter by deposit status (optional)
			
			currencySymbol: string
			in query
			filter by currency (optional)
			
			nextPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			start after, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the forward direction. 
			(Optional. May only be specified if PreviousPageToken is not specified.)
			
			previousPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			end before, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the reverse direction. 
			(Optional. May only be specified if NextPageToken is not specified.)
			
			pageSize: integer (int32)
			in query
			maximum number of items to retrieve -- default 100, minimum 1, maximum 200 (optional)
			
			startDate: string (date-time)
			in query
			(optional) Filters out results before this timestamp. In ISO 8601 format 
			(e.g., "2019-01-02T16:23:45Z"). Precision beyond one second is not 
			supported. Use pagination parameters for more precise filtering.
			
			endDate: string (date-time)
			in query
			(optional) Filters out result after this timestamp. Uses the same format 
			as StartDate. Either, both, or neither of StartDate and EndDate can be 
			set. The only constraint on the pair is that, if both are set, then 
			EndDate cannot be before StartDate.

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							},
							....
						]
			}
		"""
		opts = {}
		if status:
			opts['status'] = status
		if currencySymbol:
			opts['currencySymbol'] = currencySymbol
		if nextPageToken:
			opts['nextPageToken'] = nextPageToken
		if prevPageToken:
			opts['prevPageToken'] = prevPageToken
		if pageSize:
			opts['pageSize'] = pageSize
		if startDate:
			opts['startDate'] = startDate
		if endDate:
			opts['endDate'] = endDate
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/deposits/closed',
			options = opts
			)



### Works
	def prv_get_deposits_txid(self, txid):
		"""
		Retrieves all deposits for this account with the given TxId

		3.0		GET		https://api.bittrex.com/v3/deposits/ByTxId/{txId}

		Parameters
			txId: string
			in path
			the transaction id to lookup

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/deposits/ByTxId/' + txid
			)



### Works
	def prv_get_deposits_depid(self, depid):
		"""
		Retrieve information for a specific deposit.

		3.0		GET		https://api.bittrex.com/v3/deposits/{depositId}

		Parameters
			depositId: string
			in path
			(uuid-formatted string) - ID of the deposit to retrieve

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/deposits/' + depid
			)



### Works
	def pub_get_markets(self, marketSymbol=None):
		print('def Bittrex.pub_get_markets')
		"""
		List markets.
		Retrieve information for a specific market.

		3.0		GET		https://api.bittrex.com/v3/markets
		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"symbol": "string",
								"baseCurrencySymbol": "string",
								"quoteCurrencySymbol": "string",
								"minTradeSize": "number (double)",
								"precision": "integer (int32)",
								"status": "string",
								"createdAt": "string (date-time)",
								"notice": "string",
								"prohibitedIn": [
 									"string"
									]
							},
							....
						]
			}
		"""
		if marketSymbol == None:
			path = '/markets'
		else:
			path = '/markets/' + marketSymbol
		return self._public_api_query(sub_path = path)



### Works
	def pub_get_markets_summaries(self, marketSymbol=None):
		print('def Bittrex.pub_get_markets_summaries')
		"""
		List summaries of the last 24 hours of activity for all markets.
		Retrieve summary of the last 24 hours of activity for a specific market.

		3.0		GET		https://api.bittrex.com/v3/markets/summaries
		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/summary

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"symbol": "string",
								"high": "number (double)",
								"low": "number (double)",
								"volume": "number (double)",
								"quoteVolume": "number (double)",
								"percentChange": "number (double)",
								"updatedAt": "string (date-time)"
								},
							....
						]
			}
		"""
		if marketSymbol == None:
			path = '/markets/summaries'
		else:
			path = '/markets/' + marketSymbol + '/summary'
		return self._public_api_query(sub_path = path)



### Works
	def pub_get_markets_tickers(self, marketSymbol=None):
		print('def Bittrex.pub_get_markets_tickers')
		"""
		List tickers for all markets.
		Retrieve the ticker for a specific market.

		3.0		GET		https://api.bittrex.com/v3/markets/tickers
		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/ticker

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"symbol": "string",
								"lastTradeRate": "number (double)",
								"bidRate": "number (double)",
								"askRate": "number (double)"
							},
							....
						]
			}
		"""
		if marketSymbol == None:
			path = '/markets/tickers'
		else:
			path = '/markets/' + marketSymbol + '/ticker'
		return self._public_api_query(sub_path = path)



### Works
	def pub_get_markets_orderbook(self, marketSymbol, depth):
		print('def Bittrex.pub_get_markets_orderbook')
		"""
		Retrieve the order book for a specific market.

		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/orderbook

		Parameters
			marketSymbol: string
			required
			in path
			symbol of market to retrieve order book for

			depth: integer (int32)
			in query
			maximum depth of order book to return (optional, allowed values are [1, 25, 
				500], default is 25)

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"bid": [
											{
												"quantity": "number (double)",
												"rate": "number (double)"
											},
											....
										],
								"ask": [
											{
												"quantity": "number (double)",
												"rate": "number (double)"
											},
											....
										]
							}
						]
			}
		"""
		path = '/markets/' + marketSymbol + '/orderbook'
		return self._public_api_query(
			sub_path = path
			, options={
				'depth' : depth
				}
			)



### Works
	def pub_get_markets_trades(self, marketSymbol):
		print('def Bittrex.pub_get_markets_trades')
		"""
		Retrieve the recent trades for a specific market.

		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/trades

		Parameters
			marketSymbol: string
			required
			in path
			symbol of market to retrieve order book for

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"executedAt": "string (date-time)",
								"quantity": "number (double)",
								"rate": "number (double)",
								"takerSide": "string"
							}
						]
			}
		"""
		path = '/markets/' + marketSymbol + '/trade'
		return self._public_api_query(sub_path = path)



### Works
	def pub_get_markets_candles(self, marketSymbol, candleInterval, yyyy = None, mm = None, dd = None):
		print('def Bittrex.pub_get_markets_candles')
		"""
		Retrieve recent candles for a specific market and candle interval. The 
		maximum age of the returned candles depends on the interval as follows: 
		(MINUTE_1: 1 day, MINUTE_5: 1 day, HOUR_1: 31 days, DAY_1: 366 days). 
		Candles for intervals without any trading activity are omitted.

		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/candles/{candleInterval}/recent
		3.0		GET		https://api.bittrex.com/v3/markets/{marketSymbol}/candles/{candleInterval}/historical/{year}/{month}/{day}

		Parameters
			marketSymbol: string
			required
			in path
			symbol of market to retrieve order book for

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"startsAt": "string (date-time)",
								"open": "number (double)",
								"high": "number (double)",
								"low": "number (double)",
								"close": "number (double)",
								"volume": "number (double)",
								"quoteVolume": "number (double)"
							},
							....
						]
			}
		"""
		if yyyy == None or mm == None or dd == None:
			path = '/markets/' + marketSymbol + '/candles/' + candleInterval + '/recent'
		else:
			path = '/markets/' + marketSymbol + '/candles/' + candleInterval + '/historical/' + yyyy + '/' + mm + '/' + dd
		return self._public_api_query(sub_path = path)



### Works
	def pub_get_ping(self):
		print('def Bittrex.pub_get_ping')
		"""
		Pings the service

		3.0		GET		https://api.bittrex.com/v3/ping

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [
							{
								"serverTime": "integer (int64)"
							}
						]
			}
		"""
		return self._public_api_query(sub_path = '/ping')



### Works
	def prv_get_withdrawals_open(self, status=None, currencySymbol=None):
		"""
		List open withdrawals. Results are sorted in inverse order of the CreatedAt 
		field, and are limited to the first 1000.

		3.0		GET		https://api.bittrex.com/v3/withdrawals/open

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txCost": "string",
								"txId": "string",
								"status": "string",
								"startedAt": "string (date-time)",
								"completedAt": "string (date-time)"
							},
							....
						]
			}
		"""
		opts = {}
		if status:
			opts['status'] = status
		if currencySymbol:
			opts['currencySymbol'] = currencySymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/withdrawals/open',
			options = opts
			)



### Works
	def prv_get_withdrawals_closed(self, status=None, currencySymbol=None, nextPageToken=None, prevPageToken=None, pageSize=None, startDate=None, endDate=None):
		"""
		List closed withdrawals. StartDate and EndDate filters apply to the 
		CompletedAt field. Pagination and the sort order of the results are in 
		inverse order of the CompletedAt field.

		3.0		GET		https://api.bittrex.com/v3/withdrawals/closed

		Parameters
			status: string  COMPLETED, ORPHANED, INVALIDATED 
			in query
			filter by deposit status (optional)
			
			currencySymbol: string
			in query
			filter by currency (optional)
			
			nextPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			start after, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the forward direction. 
			(Optional. May only be specified if PreviousPageToken is not specified.)
			
			previousPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			end before, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the reverse direction. 
			(Optional. May only be specified if NextPageToken is not specified.)
			
			pageSize: integer (int32)
			in query
			maximum number of items to retrieve -- default 100, minimum 1, maximum 200 (optional)
			
			startDate: string (date-time)
			in query
			(optional) Filters out results before this timestamp. In ISO 8601 format 
			(e.g., "2019-01-02T16:23:45Z"). Precision beyond one second is not 
			supported. Use pagination parameters for more precise filtering.
			
			endDate: string (date-time)
			in query
			(optional) Filters out result after this timestamp. Uses the same format 
			as StartDate. Either, both, or neither of StartDate and EndDate can be 
			set. The only constraint on the pair is that, if both are set, then 
			EndDate cannot be before StartDate.

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txCost": "string",
								"txId": "string",
								"status": "string",
								"startedAt": "string (date-time)",
								"completedAt": "string (date-time)"
							},
							....
						]
			}
		"""
		opts = {}
		if status:
			opts['status'] = status
		if currencySymbol:
			opts['currencySymbol'] = currencySymbol
		if nextPageToken:
			opts['nextPageToken'] = nextPageToken
		if prevPageToken:
			opts['prevPageToken'] = prevPageToken
		if pageSize:
			opts['pageSize'] = pageSize
		if startDate:
			opts['startDate'] = startDate
		if endDate:
			opts['endDate'] = endDate
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/withdrawals/closed',
			options = opts
			)



### Works
	def prv_get_withdrawals_txid(self, txid):
		"""
		Retrieves all withdrawals for this account with the given TxId

		3.0		GET		https://api.bittrex.com/v3/withdrawals/ByTxId/{txId}

		Parameters
			txId: string
			in path
			the transaction id to lookup

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/withdrawals/ByTxId/' + txid
			)



### Works
	def prv_get_withdrawals_withid(self, withid):
		"""
		Retrieve information for a specific deposit.

		3.0		GET		https://api.bittrex.com/v3/withdrawals/{withdrawalId}

		Parameters
			withdrawalId: string
			in path
			(uuid-formatted string) - ID of the deposit to retrieve

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/withdrawals/' + withid
			)



### Works
	def prv_get_withdrawals_whitelist(self):
		"""
		Returns a list of white listed addresses.

		3.0		GET		/withdrawals/whitelistAddresses

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"currencySymbol": "string",
								"createdAt": "string (date-time)",
								"status": "string",
								"activeAt": "string (date-time)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/withdrawals/whitelistAddresses'
			)



### Works
	def prv_get_orders_executions(self, orderId):
		"""
		Retrieve executions for a specific order. Results are sorted in inverse 
		order of execution time, and are limited to the first 1000. NOTE: Executions 
		from before 5/27/2019 are not available. Also, there may be a delay before 
		an executed trade is visible in this endpoint.

		3.0		GET		https://api.bittrex.com/v3/orders/{orderId}/executions

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"executedAt": "string (date-time)",
								"quantity": "number (double)",
								"rate": "number (double)",
								"orderId": "string (uuid)",
								"commission": "number (double)",
								"isTaker": "boolean"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/orders/' + orderId + '/executions'
			)



### Works
	def prv_get_orders(self, orderId):
		"""
		Retrieve information on a specific order.

		3.0		GET		https://api.bittrex.com/v3/orders/{orderId}

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"direction": "string",
								"type": "string",
								"quantity": "number (double)",
								"limit": "number (double)",
								"ceiling": "number (double)",
								"timeInForce": "string",
								"clientOrderId": "string (uuid)",
								"fillQuantity": "number (double)",
								"commission": "number (double)",
								"proceeds": "number (double)",
								"status": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)",
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
									}
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/orders/' + orderId
			)



### Broken - Possibly Reversed Market Name using old convention
### Fixed - when currency is reversed
### {'code': 'INVALID_MARKET'}
	def prv_get_conditional_orders(self, conditionalOrderId):
		"""
		Retrieve information on a specific conditional order.

		3.0		GET		https://api.bittrex.com/v3/conditional-orders/{conditionalOrderId}

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"operand": "string",
								"triggerPrice": "number (double)",
								"trailingStopPercent": "number (double)",
								"createdOrderId": "string (uuid)",
								"orderToCreate": {
									"marketSymbol": "string",
									"direction": "string",
									"type": "string",
									"quantity": "number (double)",
									"ceiling": "number (double)",
									"limit": "number (double)",
									"timeInForce": "string",
									"clientOrderId": "string (uuid)",
									"useAwards": "boolean"
								},
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								},
								"clientConditionalOrderId": "string (uuid)",
								"status": "string",
								"orderCreationErrorCode": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)"
							}
						]
			}
		"""
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/conditional-orders/' + conditionalOrderId
			)



### Works
	def prv_get_orders_open(self, marketSymbol=None):
		"""
		List open orders.

		3.0		GET		https://api.bittrex.com/v3/orders/open

		Parameters
			marketSymbol: string
			in query
			filter by market (optional)

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"direction": "string",
								"type": "string",
								"quantity": "number (double)",
								"limit": "number (double)",
								"ceiling": "number (double)",
								"timeInForce": "string",
								"clientOrderId": "string (uuid)",
								"fillQuantity": "number (double)",
								"commission": "number (double)",
								"proceeds": "number (double)",
								"status": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)",
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
									}
							},
							....
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/orders/open',
			options=opts
			)



### Works
	def prv_get_conditional_orders_open(self, marketSymbol=None):
		"""
		List open conditional orders.

		3.0		GET		https://api.bittrex.com/v3/conditional-orders/open

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"operand": "string",
								"triggerPrice": "number (double)",
								"trailingStopPercent": "number (double)",
								"createdOrderId": "string (uuid)",
								"orderToCreate": {
									"marketSymbol": "string",
									"direction": "string",
									"type": "string",
									"quantity": "number (double)",
									"ceiling": "number (double)",
									"limit": "number (double)",
									"timeInForce": "string",
									"clientOrderId": "string (uuid)",
									"useAwards": "boolean"
								},
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								},
								"clientConditionalOrderId": "string (uuid)",
								"status": "string",
								"orderCreationErrorCode": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)"
							},
							....
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/conditional-orders/open',
			options = opts
			)





### Works
	def prv_get_orders_closed(self, marketSymbol=None, nextPageToken=None, prevPageToken=None, pageSize=None, startDate=None, endDate=None):
		"""
		List closed orders.
		StartDate and EndDate filters apply to the ClosedAt field. Pagination and 
		the sort order of the results are in inverse order of the ClosedAt field.

		3.0		GET		https://api.bittrex.com/v3/orders/closed

		Parameters
			marketSymbol: string
			in query
			filter by market (optional)
			
			nextPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			start after, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the forward direction. (Optional. May only be 
			specified if PreviousPageToken is not specified.)
			
			previousPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			end before, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the reverse direction. (Optional. May only be 
			specified if NextPageToken is not specified.)
			
			pageSize: integer (int32)
			in query
			maximum number of items to retrieve -- default 100, minimum 1, 
			maximum 200 (optional)
			
			startDate: string (date-time)
			in query
			(optional) Filters out results before this timestamp. In ISO 8601 format 
			(e.g., "2019-01-02T16:23:45Z"). Precision beyond one second is not 
			supported. Use pagination parameters for more precise filtering.
			
			endDate: string (date-time)
			in query
			(optional) Filters out result after this timestamp. Uses the same format 
			as StartDate. Either, both, or neither of StartDate and EndDate can be 
			set. The only constraint on the pair is that, if both are set, then 
			EndDate cannot be before StartDate.

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"direction": "string",
								"type": "string",
								"quantity": "number (double)",
								"limit": "number (double)",
								"ceiling": "number (double)",
								"timeInForce": "string",
								"clientOrderId": "string (uuid)",
								"fillQuantity": "number (double)",
								"commission": "number (double)",
								"proceeds": "number (double)",
								"status": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)",
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
									}
							},
							....
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		if nextPageToken:
			opts['nextPageToken'] = nextPageToken
		if prevPageToken:
			opts['prevPageToken'] = prevPageToken
		if pageSize:
			opts['pageSize'] = pageSize
		if startDate:
			opts['startDate'] = startDate
		if endDate:
			opts['endDate'] = endDate
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/orders/closed',
			options = opts
			)



#### Works
	def prv_get_conditional_orders_closed(self, marketSymbol=None, nextPageToken=None, prevPageToken=None, pageSize=None, startDate=None, endDate=None):
		"""
		List closed conditional orders. StartDate and EndDate filters apply to the 
		ClosedAt field. Pagination and the sort order of the results are in inverse 
		order of the ClosedAt field.

		3.0		GET		https://api.bittrex.com/v3/conditional-orders/closed

		Parameters
			marketSymbol: string
			in query
			filter by market (optional)
			
			nextPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			start after, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the forward direction. 
			(Optional. May only be specified if PreviousPageToken is not specified.)
			
			previousPageToken: string
			in query
			The unique identifier of the item that the resulting query result should 
			end before, in the sort order of the given endpoint. Used for traversing 
			a paginated set in the reverse direction. 
			(Optional. May only be specified if NextPageToken is not specified.)
			
			pageSize: integer (int32)
			in query
			maximum number of items to retrieve -- default 100, minimum 1, maximum 200 (optional)
			
			startDate: string (date-time)
			in query
			(optional) Filters out results before this timestamp. In ISO 8601 format 
			(e.g., "2019-01-02T16:23:45Z"). Precision beyond one second is not 
			supported. Use pagination parameters for more precise filtering.
			
			endDate: string (date-time)
			in query
			(optional) Filters out result after this timestamp. Uses the same format 
			as StartDate. Either, both, or neither of StartDate and EndDate can be 
			set. The only constraint on the pair is that, if both are set, then 
			EndDate cannot be before StartDate.


		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"operand": "string",
								"triggerPrice": "number (double)",
								"trailingStopPercent": "number (double)",
								"createdOrderId": "string (uuid)",
								"orderToCreate": {
									"marketSymbol": "string",
									"direction": "string",
									"type": "string",
									"quantity": "number (double)",
									"ceiling": "number (double)",
									"limit": "number (double)",
									"timeInForce": "string",
									"clientOrderId": "string (uuid)",
									"useAwards": "boolean"
								},
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								},
								"clientConditionalOrderId": "string (uuid)",
								"status": "string",
								"orderCreationErrorCode": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)"
							},
							....
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		if nextPageToken:
			opts['nextPageToken'] = nextPageToken
		if prevPageToken:
			opts['prevPageToken'] = prevPageToken
		if pageSize:
			opts['pageSize'] = pageSize
		if startDate:
			opts['startDate'] = startDate
		if endDate:
			opts['endDate'] = endDate
		return self._private_api_query(
			http_meth = 'GET',
			sub_path = '/conditional-orders/closed',
			options = opts
			)



### Works
	def prv_post_orders(self, marketSymbol=None, direction=None, type=None, quantity=None, ceiling=None, limit=None, timeInForce=None, clientOrderId=None, useAwards=None):
		pass
		"""
		Create a new order.

		3.0		POST	https://api.bittrex.com/v3/orders

		Parameters
			marketSymbol: string 
			unique symbol of the market this order is being placed on

			direction: string  BUY, SELL  
			order direction

			type: string  LIMIT, MARKET, CEILING_LIMIT, CEILING_MARKET  
			order type

			quantity: number (double)
			quantity (optional, must be included for non-ceiling orders and excluded for ceiling orders)

			ceiling: number (double)
			ceiling (optional, must be included for ceiling orders and excluded for non-ceiling orders)

			limit: number (double)
			limit (optional, must be included for LIMIT orders and excluded for MARKET orders)

			timeInForce: string  GOOD_TIL_CANCELLED, IMMEDIATE_OR_CANCEL, FILL_OR_KILL, POST_ONLY_GOOD_TIL_CANCELLED, BUY_NOW  
			time in force

			clientOrderId: string (uuid)
			client-provided identifier for advanced order tracking (optional)

			useAwards: boolean
			option to use Bittrex credits for the order (optional)


		Request Content-Types: application/json
		Request Body Example
			{
				"marketSymbol": "string",
				"direction": "string",
				"type": "string",
				"quantity": "number (double)",
				"ceiling": "number (double)",
				"limit": "number (double)",
				"timeInForce": "string",
				"clientOrderId": "string (uuid)",
				"useAwards": "boolean"
			}


		Response Content-Types: application/json
		Response Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"direction": "string",
								"type": "string",
								"quantity": "number (double)",
								"limit": "number (double)",
								"ceiling": "number (double)",
								"timeInForce": "string",
								"clientOrderId": "string (uuid)",
								"fillQuantity": "number (double)",
								"commission": "number (double)",
								"proceeds": "number (double)",
								"status": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)",
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
									}
							}
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		if direction:
			opts['direction'] = direction
		if type:
			opts['type'] = type
		if quantity:
			opts['quantity'] = quantity
		if ceiling:
			opts['ceiling'] = ceiling
		if limit:
			opts['limit'] = limit
		if timeInForce:
			opts['timeInForce'] = timeInForce
		if clientOrderId:
			opts['clientOrderId'] = clientOrderId
		if useAwards:
			opts['useAwards'] = useAwards
		return self._private_api_query(
			http_meth = 'POST',
			sub_path = '/orders',
			options=opts
			)



### Works
	def prv_delete_orders(self, orderId):
		"""
		Cancel an order.

		3.0		GET		https://api.bittrex.com/v3/orders/{orderId}

		Parameters
			orderId: string
			in path
			(uuid-formatted string) - ID of the deposit to cancel

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"direction": "string",
								"type": "string",
								"quantity": "number (double)",
								"limit": "number (double)",
								"ceiling": "number (double)",
								"timeInForce": "string",
								"clientOrderId": "string (uuid)",
								"fillQuantity": "number (double)",
								"commission": "number (double)",
								"proceeds": "number (double)",
								"status": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)",
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								}
							}
						]
			}
		"""
		opts = {}
		if orderId:
			opts['orderId'] = orderId
		return self._private_api_query(
			http_meth = 'DELETE',
			sub_path = '/orders',
			options = opts
			)



### Works
	def prv_post_conditional_order(self, marketSymbol, operand, triggerPrice=None, trailingStopPercent=None, orderToCreate=None, orderToCancel=None, clientConditionalOrderId=None):
		pass
		"""
		Create a new conditional order.

		3.0		POST	https://api.bittrex.com/v3/conditional-orders

		Parameters
			marketSymbol: string 
			unique symbol of the market this conditional order will be tracking

			operand: string  LTE, GTE  
			price above (GTE) or below (LTE) which the conditional order will trigger This value will be set automatically if trailingStopPercent is specified. (either this or trailingStopPercent must be specified)

			triggerPrice: number (double)
			percent above the minimum price (GTE) or below the maximum price (LTE) at which to trigger (either this or triggerPrice must be specified)

			trailingStopPercent: number (double)
			The stop price will automatically adjust relative to the most extreme trade value seen. (either this or trigger price must be specified)

			orderToCreate: NewOrder
			order to create if this conditional order is triggered

			orderToCancel: NewCancelConditionalOrder
			order or conditional order to cancel if this conditional order triggers Note that this relationship is reciprocal.

			clientConditionalOrderId: string (uuid)
			client-provided identifier for idempotency (optional)


		Request Content-Types: application/json
		Request Body Example
		{
			"marketSymbol": "string",
			"operand": "string",
			"triggerPrice": "number (double)",
			"trailingStopPercent": "number (double)",
			"orderToCreate": {
				"marketSymbol": "string",
				"direction": "string",
				"type": "string",
				"quantity": "number (double)",
				"ceiling": "number (double)",
				"limit": "number (double)",
				"timeInForce": "string",
				"clientOrderId": "string (uuid)",
				"useAwards": "boolean"
				},
			"orderToCancel": {
				"type": "string",
				"id": "string (uuid)"
				},
			"clientConditionalOrderId": "string (uuid)"
		}
		201 Created
		ConditionalOrder
		Created

		Response Content-Types: application/json
		Response Example (201 Created)

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"operand": "string",
								"triggerPrice": "number (double)",
								"trailingStopPercent": "number (double)",
								"createdOrderId": "string (uuid)",
								"orderToCreate": {
									"marketSymbol": "string",
									"direction": "string",
									"type": "string",
									"quantity": "number (double)",
									"ceiling": "number (double)",
									"limit": "number (double)",
									"timeInForce": "string",
									"clientOrderId": "string (uuid)",
									"useAwards": "boolean"
								},
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								},
								"clientConditionalOrderId": "string (uuid)",
								"status": "string",
								"orderCreationErrorCode": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)"
							}
						]
			}
		"""
		opts = {}
		if marketSymbol:
			opts['marketSymbol'] = marketSymbol
		if operand:
			opts['operand'] = operand
		if triggerPrice:
			opts['triggerPrice'] = triggerPrice
		if trailingStopPercent:
			opts['trailingStopPercent'] = trailingStopPercent
		if orderToCreate:
			opts['orderToCreate'] = orderToCreate
		if orderToCancel:
			opts['orderToCancel'] = orderToCancel
		if clientConditionalOrderId:
			opts['clientConditionalOrderId'] = clientConditionalOrderId
		return self._private_api_query(
			http_meth = 'POST',
			sub_path = '/conditional-orders/',
			options=opts
			)



### Works
	def prv_delete_conditional_orders(self, conditionalOrderId):
		"""
		Cancel a conditional order.

		3.0		DELETE	https://api.bittrex.com/v3/conditional-orders/{conditionalOrderId}

		Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"marketSymbol": "string",
								"operand": "string",
								"triggerPrice": "number (double)",
								"trailingStopPercent": "number (double)",
								"createdOrderId": "string (uuid)",
								"orderToCreate": {
									"marketSymbol": "string",
									"direction": "string",
									"type": "string",
									"quantity": "number (double)",
									"ceiling": "number (double)",
									"limit": "number (double)",
									"timeInForce": "string",
									"clientOrderId": "string (uuid)",
									"useAwards": "boolean"
								},
								"orderToCancel": {
									"type": "string",
									"id": "string (uuid)"
								},
								"clientConditionalOrderId": "string (uuid)",
								"status": "string",
								"orderCreationErrorCode": "string",
								"createdAt": "string (date-time)",
								"updatedAt": "string (date-time)",
								"closedAt": "string (date-time)"
							}
						]
			}
		"""
		opts = {}
		if conditionalOrderId:
			opts['conditionalOrderId'] = conditionalOrderId
		return self._private_api_query(
			http_meth = 'DELETE',
			sub_path = '/conditional-orders',
			options=opts
			)




### Works
	def prv_post_withdrawals(self, currencySymbol, quantity, cryptoAddress, cryptoAddressTag=None):
		"""
		Returns a list of white listed addresses.

		3.0		POST		/withdrawals

		Parameters
			withdrawalId: string
			in path
			(uuid-formatted string) - ID of the deposit to retrieve

		Request Example:
			{
				"currencySymbol": "string",
				"quantity": "number (double)",
				"cryptoAddress": "string",
				"cryptoAddressTag": "string"
			}

		Response Example:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txCost": "number (double)",
								"txId": "string",
								"status": "string",
								"createdAt": "string (date-time)",
								"completedAt": "string (date-time)"
							}
						]
			}

		"""
		opts = {}
		if currencySymbol:
			print('currencySymbol')
			opts['currencySymbol'] = currencySymbol
		if quantity:
			print('quantity')
			opts['quantity'] = quantity
		if cryptoAddress:
			print('cryptoAddress')
			opts['cryptoAddress'] = cryptoAddress
		if cryptoAddressTag:
			print('cryptoAddressTag')
			opts['cryptoAddressTag'] = cryptoAddressTag
		return self._private_api_query(
			http_meth = 'POST',
			sub_path = '/withdrawals',
			options=opts
			)



### Works
	def prv_delete_withdrawals(self, withdrawalId):
		"""
		Cancel a withdrawal. (Withdrawals can only be cancelled if status is REQUESTED, AUTHORIZED, or ERROR_INVALID_ADDRESS.)

		3.0		DELETE	https://api.bittrex.com/v3/withdrawals/{withdrawalId}

		Parameters
			withdrawalId: string
			in path
			(uuid-formatted string) - ID of the deposit to retrieve

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
							{
								"id": "string (uuid)",
								"currencySymbol": "string",
								"quantity": "number (double)",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string",
								"txId": "string",
								"confirmations": "integer (int32)",
								"updatedAt": "string (date-time)",
								"completedAt": "string (date-time)",
								"status": "string",
								"source": "string"
							}
						]
			}
		"""
		opts = {}
		if withdrawalId:
			opts['withdrawalId'] = withdrawalId
		return self._private_api_query(
			http_meth = 'DELETE',
			sub_path = '/withdrawals/' + withdrawalId
			)




### Works
	def prv_post_addresses(self, currencySymbol=None):
		"""
		Request provisioning of a deposit address for a currency for which no address has been requested or provisioned.

		3.0		POST	https://api.bittrex.com/v3/addresses

		Parameters
			currencySymbol: string
			in body

		Example Response:
			{'success': True,
			 'message': '',
			 'result': [ 
			 				{
								"status": "string",
								"currencySymbol": "string",
								"cryptoAddress": "string",
								"cryptoAddressTag": "string"
							}
						]
			}
		"""
		opts = {}
		if currencySymbol:
			opts['currencySymbol'] = currencySymbol
		return self._private_api_query(
			http_meth = 'POST',
#			sub_path = '/addresses/' + currencySymbol,
			sub_path = '/addresses',
			options=opts
			)



def test_gets_all():

### ACCOUNT
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_account()')
	c= bittrex_api3.prv_get_account()
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_account_volume()')
	c= bittrex_api3.prv_get_account_volume()
	print(c)



### ADDRESSES
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_addresses()')
	c= bittrex_api3.prv_get_addresses()
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_addresses(currencySymbol="BTC")')
	c= bittrex_api3.prv_get_addresses(currencySymbol='BTC')
	print(c)



### BALANCES
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_balances()')
	c= bittrex_api3.prv_get_balances()
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_balances(currencySymbol="BTC")')
	c= bittrex_api3.prv_get_balances(currencySymbol='BTC')
	print(c)



### CURRENCIES
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_currencies()')
	c= bittrex_api3.pub_get_currencies()
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_currencies(currencySymbol="BTC")')
	c= bittrex_api3.pub_get_currencies(currencySymbol='BTC')
	print(c)



### DEPOSITS
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_open()')
	c= bittrex_api3.prv_get_deposits_open()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_open(currencySymbol="BTC")')
	c= bittrex_api3.prv_get_deposits_open(currencySymbol='BTC')
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_open(status="PENDING",currencySymbol="BTC")')
	c= bittrex_api3.prv_get_deposits_open(status='PENDING',currencySymbol='BTC')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_closed()')
	c= bittrex_api3.prv_get_deposits_closed()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_closed(currencySymbol="HIVE")')
	c= bittrex_api3.prv_get_deposits_closed(currencySymbol='HIVE')
	print(c)
	#Status
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_closed(status="COMPLETED",currencySymbol="HIVE")')
	c= bittrex_api3.prv_get_deposits_closed(status='COMPLETED',currencySymbol='HIVE')
	print(c)

	#Dates cannot use the urlencode, use the new urlbuild
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_closed(status="COMPLETED",currencySymbol="HIVE", startDate="2020-01-01T00:00:01Z", endDate="2020-06-30T00:00:01Z")')
	c= bittrex_api3.prv_get_deposits_closed(status='COMPLETED',currencySymbol='HIVE', startDate='2020-01-01T00:00:01Z', endDate='2020-06-30T00:00:01Z')
	print(c)


	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_txid("7b6909f9feb2769....6eb8edc727bfb4e077c33d")')
	c= bittrex_api3.prv_get_deposits_txid('7b6909f9feb2769....6eb8edc727bfb4e077c33d')
	print(c)

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_deposits_depid("f67003c7-....-....-....-fea32fcd3dbd")')
	c= bittrex_api3.prv_get_deposits_depid('f67003c7-....-....-....-fea32fcd3dbd')
	print(c)



### MARKETS
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets()')
	c= bittrex_api3.pub_get_markets()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets(marketSymbol="BTC-USD"")')
	c= bittrex_api3.pub_get_markets(marketSymbol='BTC-USD')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_summaries()')
	c= bittrex_api3.pub_get_markets_summaries()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_summaries(marketSymbol="BTC-USD")')
	c= bittrex_api3.pub_get_markets_summaries(marketSymbol='BTC-USD')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_tickers()')
	c= bittrex_api3.pub_get_markets_tickers()
	#works
	print(c)
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_tickers(marketSymbol="BTC-USD")')
	c= bittrex_api3.pub_get_markets_tickers(marketSymbol='BTC-USD')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_orderbook(marketSymbol="BTC-USD", depth=500)')
	c= bittrex_api3.pub_get_markets_orderbook(marketSymbol='BTC-USD', depth=500)
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_trades(marketSymbol="BTC-USD")')
	c= bittrex_api3.pub_get_markets_trades(marketSymbol='BTC-USD')
	print(c)

	#works - recent
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_candles("BTC-USD", "MINUTE_5")')
	c= bittrex_api3.pub_get_markets_candles('BTC-USD', 'MINUTE_5')
	print(c)

	#works - historical
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_markets_candles("BTC-USD", "MINUTE_5", 2020, 5, 1)')
	c= bittrex_api3.pub_get_markets_candles('BTC-USD', 'MINUTE_5', '2020', '5', '1')
	print(c)



### PING
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.pub_get_ping()')
	c= bittrex_api3.pub_get_ping()
	print(c)



### WITHDRAWALS
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_open()')
	c= bittrex_api3.prv_get_withdrawals_open()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_open(currencySymbol="BAT")')
	c= bittrex_api3.prv_get_withdrawals_open(currencySymbol='BAT')
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_open(status="REQUESTED",currencySymbol="BAT"")')
	c= bittrex_api3.prv_get_withdrawals_open(status='REQUESTED',currencySymbol='BAT')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_closed()')
	c= bittrex_api3.prv_get_withdrawals_closed()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_closed(currencySymbol="BTC")')
	c= bittrex_api3.prv_get_withdrawals_closed(currencySymbol='BTC')
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_closed(status=CANCELLED,currencySymbol="BTC")')
	c= bittrex_api3.prv_get_withdrawals_closed(status='CANCELLED',currencySymbol='BTC')
	print(c)

	#Dates cannot use the urlencode, use the new urlbuild
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_closed(currencySymbol="BTC", startDate="2019-06-30T00:00:01Z", endDate="2019-12-31T00:00:01Z")')
	c= bittrex_api3.prv_get_withdrawals_closed(currencySymbol='BTC', startDate='2019-06-30T00:00:01Z', endDate='2019-12-31T00:00:01Z')
	print(c)


	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_txid("7b6909f9feb276...19806eb8edc727bfb4e077c33d")')
	c= bittrex_api3.prv_get_withdrawals_txid('7b6909f9feb276...19806eb8edc727bfb4e077c33d')
	print(c)

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_withid("f67003c7-...-....-....-fea32fcd3dbd")')
	c= bittrex_api3.prv_get_withdrawals_withid('f67003c7-....-....-....-fea32fcd3dbd')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_withdrawals_whitelist()')
	c= bittrex_api3.prv_get_withdrawals_whitelist()
	print(c)



### ORDERS
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders_open()')
	c= bittrex_api3.prv_get_orders_open()
	print(c)
	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders_open(marketSymbol="BTC-USD")')
	c= bittrex_api3.prv_get_orders_open(marketSymbol='BTC-USD')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders_closed()')
	c= bittrex_api3.prv_get_orders_closed()
	print(c)

	#Dates cannot use the urlencode, use the new urlbuild
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders_closed(startDate="2020-01-01T00:00:01Z", endDate="2020-06-30T00:00:01Z")')
	c= bittrex_api3.prv_get_orders_closed(startDate='2020-01-01T00:00:01Z', endDate='2020-06-30T00:00:01Z')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders(orderId="5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb")')
	c= bittrex_api3.prv_get_orders(orderId='5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb')
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders_executions(orderId="5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb")')
	c= bittrex_api3.prv_get_orders_executions(orderId='5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb')
	print(c)



### CONDITIONAL ORDERS
	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders_open()')
	c= bittrex_api3.prv_get_conditional_orders_open()
	print(c)

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders_open(marketSymbol="BTC-USD")')
	c= bittrex_api3.prv_get_conditional_orders_open(marketSymbol='BTC-USD')
	print(c)

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders_closed()')
	c= bittrex_api3.prv_get_conditional_orders_closed()
	print(c)

	#Dates cannot use the urlencode, use the new urlbuild
	#{'code': 'INVALID_MARKET'}
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders_closed(startDate="2020-01-01T00:00:01Z", endDate="2020-06-30T00:00:01Z")')
	c= bittrex_api3.prv_get_conditional_orders_closed(startDate='2020-01-01T00:00:01Z', endDate='2020-06-30T00:00:01Z')
	print(c)


	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders(conditionalOrderId="5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb")')
	c= bittrex_api3.prv_get_conditional_orders(conditionalOrderId='5cbbab0d-fd8e-4cbc-bc96-0b2ca0729aeb')
	print(c)

	return



def test_gets_broken():

	#Broken - Possibly Reversed Market Name using old convention
	#Fixed - when currency is reversed
	#{'code': 'INVALID_MARKET'}
	print('')
	print('')
	print('')
#	print('bittrex_api3.prv_get_conditional_orders_closed(marketSymbol="BTC-USD")')
#	c= bittrex_api3.prv_get_conditional_orders_closed(marketSymbol='BTC-USD')
	print('bittrex_api3.prv_get_conditional_orders_closed(marketSymbol="USD-BTC")')
	c= bittrex_api3.prv_get_conditional_orders_closed(marketSymbol='USD-BTC')
	print(c)

	return



def test_posting_all():

### ORDERS
	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_post_orders(marketSymbol="BTC-USD", direction="BUY", type="LIMIT", quantity=0.005, limit=100.00, timeInForce="GOOD_TIL_CANCELLED")')
	c = bittrex_api3.prv_post_orders(marketSymbol='BTC-USD', direction='BUY', type='LIMIT', quantity=0.005, limit=100.00, timeInForce='GOOD_TIL_CANCELLED')
	print(c)
	orderid = c['id']

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders(orderId="' + orderid + '")')
	c= bittrex_api3.prv_get_orders(orderId=orderid)
	print(c)


	print('')
	print('')
	print('')
	print('bittrex_api3.prv_delete_orders(orderId="' + orderid + '")')
	c = bittrex_api3.prv_delete_orders(orderId=orderid)
	print(c)


	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_orders(orderId="' + orderid + '")')
	c= bittrex_api3.prv_get_orders(orderId=orderid)
	print(c)


### CONDITIONAL ORDERS
	#Works
	print('')
	print('')
	print('')
	#prv_post_conditional_order(self, marketSymbol, operand, triggerPrice, trailingStopPercent, orderToCreate, orderToCancel, clientConditionalOrderId=None):
	print('bittrex_api3.prv_post_conditional_order(marketSymbol="BTC-USD", operand="LTE", triggerPrice=100, trailingStopPercent, orderToCreate, orderToCancel, clientConditionalOrderId=None)')
	c = bittrex_api3.prv_post_conditional_order(marketSymbol='BTC-USD' 
												,operand='LTE'
												,triggerPrice=100.00
#												,trailingStopPercent=2.0
												,orderToCreate={'marketSymbol':'BTC-USD', 'direction':'BUY', 'type':'LIMIT', 'quantity':0.005, 'limit':100.00, 'timeInForce':'GOOD_TIL_CANCELLED'}
#												,orderToCancel
#												,clientConditionalOrderId=None
												)
	print(c)
	orderid = c['id']

	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders(conditionalOrderId="' + orderid + '")')
	c= bittrex_api3.prv_get_conditional_orders(conditionalOrderId=orderid)
	print(c)

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_delete_conditional_orders(conditionalOrderId="' + orderid + '")')
	c = bittrex_api3.prv_delete_conditional_orders(conditionalOrderId=orderid)
	print(c)


	#works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_get_conditional_orders(conditionalOrderId="' + orderid + '")')
	c= bittrex_api3.prv_get_conditional_orders(conditionalOrderId=orderid)
	print(c)



### WITHDRAWALS
	#Works
	print('')
	print('')
	print('')
#	print('bittrex_api3.prv_post_withdrawals(currencySymbol="EXP", quantity=0.00000001, cryptoAddress="AddAddress", cryptoAddressTag="")')
#	c = bittrex_api3.prv_post_withdrawals(currencySymbol='EXP', quantity=0.00000001, cryptoAddress='AddAddress', cryptoAddressTag='')
#	print('bittrex_api3.prv_post_withdrawals(currencySymbol="ETH", quantity=0.1, cryptoAddress="AddAddress", cryptoAddressTag="")')
#	c = bittrex_api3.prv_post_withdrawals(currencySymbol='ETH', quantity=0.1, cryptoAddress='AddAddress', cryptoAddressTag='')
	print(c)
	withdrawalId = c['id']

#{'code': 'INVALID_PERMISSIONS', 'status_code': 
#{'code': 'WITHDRAWAL_TOO_SMALL', 'status_code': 409}

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_delete_withdrawals(withdrawalId="' +str(withdrawalId) + '")')
	c = bittrex_api3.prv_delete_withdrawals(withdrawalId=withdrawalId)
	print(c)



### ADDRESSES	
	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_post_addresses("BTC")')
	c= bittrex_api3.prv_post_addresses('BTC')
	print(c)
#	{'code': 'CRYPTO_ADDRESS_ALREADY_EXISTS', 'status_code': 409}

	#Works
	print('')
	print('')
	print('')
	print('bittrex_api3.prv_post_addresses("XXXX")')
	c= bittrex_api3.prv_post_addresses('XXXX')
	print(c)
#	{'code': 'CURRENCY_DOES_NOT_EXIST', 'status_code': 400}


	return




bittrex_api3 = Bittrex(secrets["bittrex"]["bittrexKey"], secrets["bittrex"]["bittrexSecret"])

def test():
	print('test()')

	test_gets_all()
#	test_gets_broken()
#	test_posting_all()
#	test_posting_broken()


test()


#	// 'Call to Cancel was throttled. Try again in 60 seconds.': DDoSProtection,
#	// 'Call to GetBalances was throttled. Try again in 60 seconds.': DDoSProtection,
#	'APISIGN_NOT_PROVIDED': AuthenticationError,
#	'INVALID_SIGNATURE': AuthenticationError,
#	'INVALID_CURRENCY': ExchangeError,
#	'INVALID_PERMISSION': AuthenticationError,
#	'INSUFFICIENT_FUNDS': InsufficientFunds,
#	'QUANTITY_NOT_PROVIDED': InvalidOrder,
#	'MIN_TRADE_REQUIREMENT_NOT_MET': InvalidOrder,
#	'ORDER_NOT_OPEN': OrderNotFound,
#	'INVALID_ORDER': InvalidOrder,
#	'UUID_INVALID': OrderNotFound,
#	'RATE_NOT_PROVIDED': InvalidOrder, // createLimitBuyOrder ('ETH/BTC', 1, 0)
#	'WHITELIST_VIOLATION_IP': PermissionDenied,
