import json
import random as rand

from eemail import Email
from urllib import request

class User:
	def __init__(self, email, first_name, last_name, username, password, picture):
		self.email = email
		self.first_name = first_name
		self.last_name = last_name
		self.username = username
		self.password = password
		self.picture = picture

		self.name = self.first_name.capitalize() + ' ' + self.last_name.capitalize()

	@staticmethod
	def create(handlers=[]):
		opener = request.build_opener(*handlers)

		url = 'https://randomuser.me/api'
		req = request.Request(url)
		res = opener.open(req)
		text = res.read().decode()
		info = json.loads(text)

		first_name = info['results'][0]['name']['first']
		last_name = info['results'][0]['name']['last']
		username = (first_name + last_name + str(rand.randint(1000, 9909))).replace(' ', '')[:20]
		password = info['results'][0]['login']['password'] + str(rand.randint(100, 999))

		if not all([len(s.encode()) == len(s) for s in (first_name, last_name, username, password)]):
			return User.create()

		email = Email.generate()
		picture = info['results'][0]['picture']['large']

		return User(email, first_name, last_name, username, password, picture)
