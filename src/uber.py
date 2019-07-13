import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

class Uber:
	def __init__(self, email, password):
		self.email = email
		self.password = password

	def request():
		requests.post()

	@staticmethod
	def signup(first_name, last_name, number, email, password, promo):
		driver = webdriver.Chrome()

		driver.get('https://get.uber.com/')
		title = driver.title

		driver.find_element_by_id('fname').send_keys(first_name)
		driver.find_element_by_id('lname').send_keys(last_name)
		driver.find_element_by_id('mobile').send_keys(number)
		driver.find_element_by_id('email').send_keys(email)
		driver.find_element_by_id('password').send_keys(password)
		driver.find_element_by_link_text('Add a promo code').click()
		driver.find_element_by_id('promo').send_keys(promo)
		driver.find_element_by_id('submit-btn').click()

		sleep(5)

		driver.switch_to.frame(WebDriverWait(driver.find_element_by_id('captcha'), 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe'))))

		try:
			WebDriverWait(driver, 60).until(lambda driver: driver.find_element_by_id('recaptcha-anchor').get_attribute('aria-checked') == 'true')

			driver.switch_to.window('')
			driver.find_element_by_id('signup-form').submit()

			WebDriverWait(driver, 60).until_not(EC.title_is(title))
		except (TimeoutException, UnexpectedAlertPresentException):
			driver.quit()
			Uber.signup(first_name, last_name, number, email, password, promo)

		driver.quit()

		return Uber(email, password)
