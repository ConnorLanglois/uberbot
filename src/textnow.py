#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import random
import requests
import urllib.request, urllib.parse, urllib.error

from collections import OrderedDict
from selenium import webdriver
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

class Textnow:
	API_URL = 'http://api.textnow.me/api2.0/'
	SIGN_KEY = ''
	USER_AGENT = 'TextNow 5.15.0 (Android SDK built for x86; Android OS 5.1.1; en_US)'

	def __init__(self, TN_username, TN_password):
		self.TN_username = TN_username
		self.TN_password = TN_password
		self.Login = False
		self.username = None
		self.userInfo = None

	@staticmethod
	def signup(first_name, last_name, username, password, email):
		driver = webdriver.Chrome()

		driver.get('https://www.textnow.com/signup')
		title = driver.title
		
		driver.find_element_by_name('firstname').send_keys(first_name)
		driver.find_element_by_name('lastname').send_keys(last_name)
		driver.find_element_by_name('username').send_keys(username)
		driver.find_element_by_name('password').send_keys(password)
		driver.find_element_by_name('email').send_keys(email)

		try:
			driver.switch_to.frame(2)
			WebDriverWait(driver, 60).until(lambda driver: driver.find_element_by_id('recaptcha-anchor').get_attribute('aria-checked') == 'true')
		except (NoSuchFrameException, TimeoutException):
			driver.quit()
			Textnow.signup(first_name, last_name, username, password, email)

		sleep(1)

		driver.switch_to.window('')
		driver.find_element_by_name('userForm').submit()

		WebDriverWait(driver, 60).until_not(EC.title_is(title))

		driver.get('https://www.textnow.com/messaging')
		areacode_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'areacode')))
		areacode_input.send_keys(random.randint(200, 999))
		areacode_input.send_keys(Keys.ENTER)

		sleep(1)

		driver.quit()

		return Textnow(username, password)

	def gen_signature(self, method, node, query):
		return hashlib.md5(('%s%s%s%s' % (self.SIGN_KEY, method, node, str(query).replace('\\\\', '\\'))).encode()).hexdigest() # Signature Pattern in GITHUB README

	def gen_json(self, data):
		return json.dumps(data, sort_keys=False, separators=(',', ':'))

	def send_req(self, method, url, sign, data=None):
		url = '%s%s'%(url, '&signature=' + sign)
		if method == 'POST':
			if data == None:
				return requests.post(url, headers={'User-Agent':self.USER_AGENT}).json()
			return requests.post(url, data={'json':str(data).replace('\\\\', '\\')}, headers={'User-Agent':self.USER_AGENT}).json()

		if method == 'PATCH':
			return requests.patch(url, data={'json':str(data).replace('\\\\', '\\')}, headers={'User-Agent':self.USER_AGENT}).text

		if method == 'GET':
			return requests.get(url, headers={'User-Agent':self.USER_AGENT}).json()

	def login(self):
		# return if logged in
		if self.Login != False:
			return True

		node = 'sessions'
		query = '?client_type=TN_ANDROID'

		loginData = OrderedDict([
			('password', self.TN_password),
			('username', self.TN_username),
			('esn', '00000000000000'),
			('os_version', '22'),
			('app_version', '5.15.0'),
			('iccid', '89014103211118510720')
			])
		jsonData = self.gen_json(loginData)
		sign = self.gen_signature('POST', node, query + jsonData)
		req = self.send_req('POST', '%s%s%s'%(self.API_URL, node, query), sign, jsonData)
		if 'id' in req:
			self.Login = req['id'] # id like AUTH_KEY
			self.username = req['username']
			self.userInfo = self.get_info_about_user()
			return True
		else:
			return False

	def get_info_about_user(self):
		if self.Login == False:
			return False

		node = 'users/%s'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)
		sign = self.gen_signature('GET', node, query)
		req = self.send_req('GET', '%s%s%s'%(self.API_URL, node, query), sign)
		return req

	def get_messages(self, start_message_id = 1, page_size = 30, get_all = 1):
		if self.Login == False:
			return False

		node = 'users/%s/messages'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s&get_all=%s&page_size=%s&start_message_id=%s'%(self.Login, get_all, page_size, start_message_id)
		sign = self.gen_signature('GET', node, query)
		req = self.send_req('GET', '%s%s%s'%(self.API_URL, node, query), sign)
		return req

	def get_wallet(self):
		if self.Login == False:
			return False

		node = 'users/%s/wallet'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)
		sign = self.gen_signature('GET', node, query)
		req = self.send_req('GET', '%s%s%s'%(self.API_URL, node, query), sign)
		return req

	def send_message(self, number, msg):
		# return if logged in
		if self.Login == False:
			return False

		node = 'users/%s/messages'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)

		msgData = OrderedDict([
			('from_name', self.userInfo['first_name']),
			('contact_type', '2'),
			('contact_value', '+%s'%(number)),
			('message', msg.replace('/', '\/')),
			('to_name', '')
			])
		jsonData = self.gen_json(msgData)
		sign = self.gen_signature('POST', node, query + jsonData)
		req = self.send_req('POST', '%s%s%s'%(self.API_URL, node, query), sign, jsonData)
		return req['id']

	def change_full_name(self, first_name, last_name):
		# return if logged in
		if self.Login == False:
			return False

		node = 'users/%s'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)

		msgData = OrderedDict([
			('first_name', first_name),
			('last_name', last_name)
			])
		jsonData = self.gen_json(msgData)
		sign = self.gen_signature('PATCH', node, query + jsonData)
		req = self.send_req('PATCH', '%s%s%s'%(self.API_URL, node, query), sign, jsonData)
		if req == '[]':
			return True
		else:
			return False

	def change_email(self, email):
		# return if logged in
		if self.Login == False:
			return False

		node = 'users/%s'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)

		msgData = OrderedDict([
			('email', email)
			])
		jsonData = self.gen_json(msgData)
		sign = self.gen_signature('PATCH', node, query + jsonData)
		req = self.send_req('PATCH', '%s%s%s'%(self.API_URL, node, query), sign, jsonData)
		if req == '[]':
			return True
		else:
			return False

	def change_password(self, old_password, new_password):
		# return if logged in
		if self.Login == False:
			return False

		node = 'users/%s'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)

		msgData = OrderedDict([
			('old_password', old_password),
			('password', new_password)
			])
		jsonData = self.gen_json(msgData)
		sign = self.gen_signature('PATCH', node, query + jsonData)
		req = self.send_req('PATCH', '%s%s%s'%(self.API_URL, node, query), sign, jsonData)
		if req == '[]':
			return True
		else:
			return False

	def resend_verify_email(self):
		# return if logged in
		if self.Login == False:
			return False

		node = 'users/%s/email'%(self.username)
		query = '?client_type=TN_ANDROID&client_id=%s'%(self.Login)
		sign = self.gen_signature('POST', node, query)
		req = self.send_req('POST', '%s%s%s'%(self.API_URL, node, query), sign)
		return req

if __name__ == '__main__':
	print("can't run this file.")
