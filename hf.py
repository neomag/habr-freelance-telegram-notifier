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
if os.path.isfile("chat_id"):
    if os.path.getsize("chat_id") > 0:
        print("chat_id found, loading")
        with open("chat_id") as f:
             chat_id=f.readline()
             print(f'chat_id from file = {chat_id}')
    else:
        print("chat_id file is empty, it is recommended to delete it")         
        exit()
else:
    print(f"chat_id file does not exists, trying https://api.telegram.org/bot{TOKEN}/getUpdates")
    r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
    js=json.loads(r.text)
    if r.status_code==200:
        try:
            chat_id=js['result'][0]['message']['from']['id']
            with open("chat_id", 'w') as f:
                print(f"chat_id={chat_id}")
                f.write(str(chat_id))
                f.close
        except:
            print('chat_id not found, try send some random msg to group')
            exit()
    else:
        print(f"https://api.telegram.org/bot{TOKEN}/getUpdates  return non 200 code")
        exit()


def telegram_sendmessage(message):
   send_text = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={str(chat_id)}&parse_mode=Markdown&text={message}'
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

#check for a new tasks
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
