from faker import Faker

fk = Faker(locale='zh_CN')
print(fk.text())