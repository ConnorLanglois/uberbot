import json
import random
import re
import string
from http.cookiejar import CookieJar
from time import sleep
from urllib import request

class Email:
	def __init__(self, address, opener=None):
		self.address = address
		self.opener = opener

	@staticmethod
	def create(handlers=[]):
		cj = CookieJar()
		cookie_handler = request.HTTPCookieProcessor(cj)
		opener = request.build_opener(cookie_handler, *handlers)
		opener.addheaders = [
			('Host', '10minutemail.com'),
			('Origin', 'https://10minutemail.com'),
			# ('Referer', 'https://10minsms.com/'),
			('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
			('X-Requested-With', 'XMLHttpRequest')
		]

		url = 'https://www.10minutemail.com'
		req = request.Request(url)
		res = opener.open(req)

		url = 'https://10minutemail.com/10MinuteMail/resources/session/address'
		req = request.Request(url)
		res = opener.open(req)

		address = res.read().decode()

		return Email(address, opener=opener)

	@staticmethod
	def generate(lp=None, domain=None):
		lp_length = random.randint(5, 10)
		domain_length = random.randint(3, 5)
		lp = ''.join(random.choice(string.ascii_lowercase) for i in range(lp_length)) if lp is None else lp
		domain = ''.join(random.choice(string.ascii_lowercase) for i in range(domain_length)) if domain is None else domain
		tld = '.com'
		address = '@'.join([lp, domain]) + tld
		email = Email(address)

		return email

	@property
	def message_count(self):
		url = 'https://10minutemail.com/10MinuteMail/resources/messages/messageCount'
		req = request.Request(url)
		res = opener.open(req)
		text = res.read().decode()

		message_count = int(text)

		return message_count

	def query_messages(self, interval=5, times=None):
		def get_messages():
			url = 'https://10minutemail.com/10MinuteMail/resources/messages/messagesAfter/0'
			req = request.Request(url)
			res = self.opener.open(req)
			text = res.read().decode()

			messages = json.loads(text)

			return messages

		while times is None or times > 0:
			messages = get_messages()

			print(messages, end='', flush=True)

			if len(messages) > 0:
				print()

				return messages
			else:
				times = times - 1 if times is not None else None

				sleep(interval)

		raise Exception('Timeout')
