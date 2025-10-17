# Gutenberg Web Scraping

這是一個使用 **Python** 撰寫的爬蟲程式，用來從 [Project Gutenberg](https://www.gutenberg.org/browse/languages/zh) 擷取中文書籍內容。  
程式會自動建立書單、下載書籍全文，並清除沒有中文或英文內容的檔案。  

---

## 功能說明

- 擷取古登堡中文書籍清單  
- 抓取每本書的線上閱讀連結  
- 下載書籍文字內容（.txt）  

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