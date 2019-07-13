from textnow import Textnow

textnow = Textnow('', '')
textnow.login()

print(textnow.get_info_about_user()['phone_number'])
print(textnow.get_messages())
