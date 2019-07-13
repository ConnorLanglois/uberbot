from textnow import Textnow
from uber import Uber
from user import User

user = User.create()
print(user.email.address)
print(user.username)
print(user.password)

textnow = Textnow.signup(user.first_name, user.last_name, user.username, user.password, user.email.address)
textnow.login()

number = textnow.get_info_about_user()['phone_number']
print(number)

uber = Uber.signup(user.first_name, user.last_name, number, user.email.address, user.password, '')
