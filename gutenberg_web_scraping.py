import os
import requests as req
from bs4 import BeautifulSoup as bs
from time import sleep
import re
import json
from pprint import pprint

url = 'https://www.gutenberg.org/browse/languages/zh'
prefix = 'https://www.gutenberg.org/'
out_json = 'gutenberg_book_list.json'
out_dir = 'project_gutenberg'

my_headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
}

def fetch_book_list():
    gutenberg_book_list = []
    r = req.get(url, headers=my_headers, timeout=30)
    r.raise_for_status()
    soup = bs(r.text, 'lxml')

    for a in soup.select('li.pgdbetext > a[href]'):
        gutenberg_book_list.append({
            'book': a.get_text(strip=True),
            'link': prefix + a['href']
        })

    for idx, obj in enumerate(gutenberg_book_list):
        try:
            r2 = req.get(obj['link'], headers=my_headers, timeout=30)
            r2.raise_for_status()
            soup2 = bs(r2.text, 'lxml')
            link_tag = soup2.select_one('a[title="Read online"]')

            gutenberg_book_list[idx]['text_link'] = prefix + link_tag['href'] if link_tag else None
            sleep(0.5)
        except Exception as e:
            gutenberg_book_list[idx]['text_link'] = None
            print(f"[WARN] Can't Read online: {obj['link']} | {e}")

    return gutenberg_book_list

def dump_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=None))

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|\r\n\t]', '', name)

def extract_text_from_page(url: str) -> str:
    # 修正：headers=url -> headers=my_headers
    r = req.get(url, headers=my_headers, timeout=30)
    r.raise_for_status()
    soup = bs(r.text, 'lxml')

    paragraphs = soup.select('p')
    text = ''.join(p.get_text() for p in paragraphs) if paragraphs else soup.get_text()


    clean_text = re.sub(r'[a-zA-Z]', '', text)
    return clean_text

def save_books_to_txt(json_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        books = json.load(f)

    for index, book in enumerate(books):
        book_name = book.get('book', f'book_{index:02d}')
        text_link = book.get('text_link')

        if not text_link:
            print(f"[SKIP] {book_name} haven't Read online link")
            continue

        try:
            content = extract_text_from_page(text_link)
            clear_name = sanitize_filename(book_name)
            filename = os.path.join(out_dir, f"{index:02d}_{clear_name}.txt")
            with open(filename, 'w', encoding='utf-8') as fw:
                fw.write(content)
            print(f"[OK]：{filename}")
            sleep(0.5)

  
            has_chinese = re.search(r'[\u4e00-\u9fff]', content) is not None
            has_english = re.search(r'[A-Za-z]', content) is not None
            if not (has_chinese or has_english):
                os.remove(filename)
                print(f"[DEL] No Chinese/English content -> deleted: {filename}")

        except Exception as e:
            print(f"[FAIL] download {book_name} fail：{e}")

def main():
    book_list = fetch_book_list()
    pprint(f"output book's name and link:{book_list[:3]}")
    dump_json(book_list, out_json)
    save_books_to_txt(out_json, out_dir)

if __name__ == "__main__":
    main()
