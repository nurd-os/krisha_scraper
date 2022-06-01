import time
import requests
from bs4 import BeautifulSoup
import re
import telebot


class OlxScraper():

    def __init__(self):
        self.url = 'https://krisha.kz/arenda/kvartiry/almaty/?das[flat.renovation]=1&das[live.rooms][0]=2&das[live.rooms][1]=3&das[price][to]=200000&das[rent.period]=2&das[who]=1'
        self.base_url = 'https://krisha.kz/'
        self.response = ''
        self.soup = ''

    def request_olx(self):
        response = requests.get(self.url)
        self.response = response

    def extract(self):
        soup = BeautifulSoup(self.response.text, 'html.parser')
        self.soup = soup

    def get_descr(self):
        return self.soup.find_all(class_='a-card__descr')

    def get_title(self, descr):
        title = descr.find('a')
        title = title.text.replace('\n', '')
        return title

    def get_link(self, descr):
        href = descr.find('a')
        return href['href']

    def get_address(self, descr):
        address = descr.find(class_='a-card__subtitle')
        address = address.text.replace('\n', '')
        pattern = re.compile('\w+ р-н')
        res = pattern.search(address)
        if res:
            return res.group()[0:-4]
        else:
            return "test"

    def get_price(self, descr):
        price = descr.find(class_='a-card__price')
        return ''.join(([i for i in price.text if i in '0123456789']))

    def get_year(self, descr):
        year = descr.find(class_='a-card__text-preview')
        year = year.text.replace('\n', '')
        pattern = re.compile('\d\d\d\d')
        res = pattern.search(year)
        return res.group()


all_adds = []

id = 0

def execute2(i):
    global id
    res = ''
    olx = OlxScraper()
    olx.url += '&page=' + str(i)
    olx.request_olx()
    olx.extract()
    descr = olx.get_descr()
    for each in descr:
        title = olx.get_title(each)
        href = olx.base_url + olx.get_link(each)
        price = olx.get_price(each)
        address = olx.get_address(each)
        year = olx.get_year(each)
        if href not in all_adds:
            all_adds.append(href)
            # if address in ['Алмалинский', 'Бостандыкский', 'Медеуский']:
            if address in ['Бостандыкский', 'Медеуский', 'Ауэзовский']:
                res += '-----------' + 'Ad ID: ' + str(id) + '-----------\n'
                res += title + '\n'
                res += href + '\n'
                res += 'Цена: ' + price + '\n'
                res += 'Год постройки: ' + year + '\n'
                res += 'Адрес: ' + address + '\n'
                id += 1
    return res



bot = telebot.TeleBot(API)



# @bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['start'])
def get_text_messages(message):
    while True:
        flag = 0 
        for i in range(1, 10):
            
            time.sleep(1.5)
            result = execute2(i)
            if result:
                flag = 1
                bot.send_message(message.from_user.id, "-----Уау смотри что нашел-----\n")
                bot.send_message(message.from_user.id, result)
        if not flag:
            bot.send_message(message.from_user.id, "-----Пока ничего не нашел :( ---\n")
        time.sleep(300)


bot.polling()
