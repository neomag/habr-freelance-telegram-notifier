#!/usr/bin/python3
import requests
import json
import os.path
from bs4 import BeautifulSoup
from dotenv import load_dotenv

current_file = os.path.realpath(__file__)
current_directory = os.path.dirname(current_file)

os.chdir(current_directory)
if os.path.isfile('.env'):
    print(".env file found, loading")
else: 
    print("ERROR! .env file NOT found, exit")
    exit()    

load_dotenv()

url   = os.getenv('url')
TOKEN = os.getenv('TOKEN')
inject_url = os.getenv('inject_url')
base_file = os.getenv('base_file')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

#store parsed data
base_file = './base.json'

#get chat_id
r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
js=json.loads(r.text)
chat_id=js['result'][0]['message']['chat']['id']

def telegram_sendmessage(message):
   send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(chat_id) + '&parse_mode=Markdown&text=' + message
   response = requests.get(send_text)
   return response.json()


page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, 'html.parser')

tasks = [div['title'] for div in soup.find_all('div', title=True)]
hrefs = soup.find_all('div',class_='task__title')

def get_clean_url(h):
    tmp = href.find('a')
    link = tmp.get('href')
    return inject_url+link
  
base = {}

#load/save database
if os.path.isfile(base_file):
    print("base.json found, loading")
    with open(base_file) as f:
        base = json.load(f)
else:
    print("file does not exists, saving to base.json")
    with open(base_file, 'w') as f:
        json.dump(base,f)

#check for a new records
for task, href in zip(tasks,hrefs):
    if href.find('a')['href'] not in base.keys():
        base[ href.find('a')['href'] ] = task
        print(f"new task found: {task}")
        print(f"url: {get_clean_url(href)}")
        telegram_sendmessage(str(task))
        telegram_sendmessage(str(get_clean_url(href)))


if  len(base) >0:
    with open(base_file, 'w') as f:
        json.dump(base,f)
