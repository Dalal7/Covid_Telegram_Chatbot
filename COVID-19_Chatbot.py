import json
import requests
import urllib3
from bs4 import BeautifulSoup
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)
f_handler = logging.FileHandler('file.log')
f_handler.setLevel(logging.DEBUG)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)


TOKEN = "here goes your access token from BotFather"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    # Telegram understands UTF-8, so encode text for unicode compatibility
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def getData(text,chat_id):
    try:
        url = "https://www.worldometers.info/coronavirus/"
        req = urllib3.PoolManager()
        res = req.request('GET', url)
        soup = BeautifulSoup(res.data, 'html.parser')
        table = soup.find("table", attrs={"id": "main_table_countries_today"})
        rows = table.findChildren('tr')
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                #logger.debug("Checking the country name: {}, given {}".format((cell.string),text))
                if str(cell.text).lower() == text.lower():
                    logger.debug("Country is found")
                    #if (cell.string.encode('utf8').decode('utf-8')).lower() == text.lower():
                    return cells
                    break
    except:
        message = "Please write the name of the country in english and without extra spaces."
        return message

def extract(message):
    try:
        l = []
        soup = BeautifulSoup(str(message), 'html.parser')
        for td in soup.find_all('td'):
            if td.string==" ":
                l.append(0)
            else:
                l.append(td.string)
        message = (
            "Country: {}\nTotal Cases: {}\nNew Cases: {}\nTotal Deaths: {}\nNew Deaths: {}\nTotal Recovered: {}\nActive Cases: {}\nCritical Cases: {}\n% of people infected at the moment on the total since the beginning: {} ".format(*l))
        return message
    except:
        message = "Please write the name of the country in english and without extra spaces."
        return message


def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(extract(getData(text, chat_id)), chat_id)
    get_url(url)


def main():
    last_textchat = (None, None)
    while True:
        text, chat = get_last_chat_id_and_text(get_updates())
        if (text, chat) != last_textchat:
            send_message(text, chat)
            last_textchat = (text, chat)


if __name__ == '__main__':
    logger.debug('Script start')
    main()