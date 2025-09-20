import requests
from bs4 import BeautifulSoup

url = ''
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

description_div = soup.find('div', class_='description__text description__text--rich')
description_text = description_div.get_text()

print(description_text)