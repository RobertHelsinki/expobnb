import requests
from bs4 import BeautifulSoup


def coin_price(coin):

    page = requests.get("https://coinmarketcap.com/currencies/{}/".format(coin))

    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find('div', class_='priceValue___11gHJ').string

    price = price[1:]
    price = float(price)
    return price


