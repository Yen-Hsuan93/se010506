# Gutenberg Web Scraping

本專案為一個使用 Python 撰寫的爬蟲程式，從 Project Gutenberg擷取中文書籍內容。

---

## 功能說明

- 擷取古登堡中文書籍清單  
- 抓取每本書的線上閱讀連結  
- 下載書籍文字內容（.txt） 
- 本專案以練習 Python 網頁爬蟲與資料清理使用。

---

## 執行方式

### 1.安裝必要套件

pip install requests beautifulsoup4 lxml

### 2.執行程式

python gutenberg_web_scraping.py

### 3.執行結果
- 抓取書籍清單
- 產生 gutenberg_book_list.json
- 下載各書籍文字檔