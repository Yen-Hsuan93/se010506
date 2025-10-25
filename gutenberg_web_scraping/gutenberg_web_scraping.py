#建立解析書本清單
#儲存書本清單
#清整內文
#抽取文字
#儲存成txt

#Imports
import os
import re
import json
from time import sleep
from pprint import pprint
import requests as req
from bs4 import BeautifulSoup as bs
import logging

out_json = 'gutenberg_book_list.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


my_headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}
url = 'https://www.gutenberg.org/browse/languages/zh'
prefix = 'https://www.gutenberg.org'

def book_list():
    
    gutenberg_book_list = []

    request_url = req.get(url, headers = my_headers , timeout = 30)
    request_url.raise_for_status()
    logging.info(f" step1 success!: {url}")
    soup_0 = bs(request_url.text,'lxml')
    
    for catch in soup_0.select('div.container li.pgdbetext a[href]'):
        name = catch.get_text(strip=True)
        if re.fullmatch(r'[A-Za-z0-9\s\W]+',name):
            continue

        gutenberg_book_list.append({
            'book_name':name,
            'link' : prefix + catch['href']            
        })
    
    for idx , obj in enumerate(gutenberg_book_list):
        try:
            request_url_inn = req.get(obj['link'], headers = my_headers, timeout = 30)
            request_url_inn.raise_for_status()
            logging.info(f" step2 success!: {obj['link']}")
            soup_1 = bs(request_url_inn.text, 'lxml')
            tag = soup_1.select_one('table.files a[href].link.read_html[title="Read online"]')
            if tag is None:
                raise ValueError("No 'Read online' link found")
            text_link = prefix + tag['href']
            gutenberg_book_list[idx]['text_link'] = text_link
            logging.info(f" step3 success!: {obj['link']}")
        except Exception as e:
            gutenberg_book_list[idx]['text_link'] = None
            logging.error(f" step3 fail!: Can't Read online: {obj['link']} | {e}")
    
    return gutenberg_book_list
    #pprint(gutenberg_book_list)

def dump_json(data, path):
    with open(path, 'w', encoding = 'utf8') as file:
        file.write(json.dumps(data, ensure_ascii = False, indent = None))
        return data

def text_cleaner(gutenberg_book_list):
    try:
        gutenberg_content = []
        gutenberg_content.clear()

        os.makedirs('books_gutenberg', exist_ok=True)

        for idx , obj in enumerate(gutenberg_book_list):
            print(f"正在抓第 {idx+1} 本：{obj.get('book_name')}")
            if not obj.get('text_link'):
                logging.warning(f'skip (no text link):{obj}')
                continue
            request_url_inn = req.get(obj['text_link'], headers = my_headers, timeout = 30)
            request_url_inn.raise_for_status()
            logging.info(f"step4 success!: {obj['text_link']}")
            soup_2 = bs(request_url_inn.text, 'lxml')

            title_tag = soup_2.select_one('div.container > p:nth-child(1) strong')
            title_text = "Unknown title"
            if title_tag and title_tag.next_sibling:
                title_text = re.sub(r'^[\s"：:，、]*', '', title_tag.next_sibling.strip())

            body_tag = soup_2.select('p[id^="id0000"]')
            body_text = ("\n".join(p.get_text(strip= True)for p in body_tag) if body_tag else "Unknown text")

            gutenberg_content.append({
                'title':title_text,
                'content':body_text
            })
            logging.info(f"step4 success!: {obj['text_link']}")

            safe_title = re.sub(r'[\\/:*?"<>|\n\t\r]', '', (title_text or '').strip()) or f"{idx+1:02d}_Unknown_title"
            file_name = f"{idx+1:02d}_{safe_title}.txt"
            file_path = os.path.join('books_gutenberg', file_name)
            with open(file_path, 'w', encoding='utf8') as file:
                file.write(f"【{safe_title}】\n\n")
                file.write(body_text)
            logging.info(f'step5 success! :save {safe_title}')

            sleep(0.5)

        return gutenberg_content
    
    except Exception as e:
        logging.error(f" step4 fail!: haven't text: {obj.get('text_link')} | {e}")
        return []

def main():
    gutenberg_book = book_list()
    json_list = dump_json(gutenberg_book, out_json)
    gutenberg_content = text_cleaner(json_list)


if __name__ =="__main__":
    main()


