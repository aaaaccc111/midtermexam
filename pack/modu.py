import json
import csv
import sqlite3
import os
from datetime import datetime

db_file = "libary.db"
user_file = "user.csv"
book_file = "books.json"


##資料庫函數(包含資料表的建立及資料匯入)
def create_db(db_file, user_file, book_file):
    """
    這裡建立一個名為librart.db的資料庫，其中包含users和books兩個資料表

    users資料表包含兩個欄位: user_id, username, password
    books資料表包含四個欄位: book_id, title, author, publisher, year

    users資料表為user.csv檔案匯入
    books資料表為books.json檔案匯入
    """

    try:
        if not os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            ''')

            #檢查.json檔案及.csv檔案是否存在
            try:
                if not os.path.exists(book_file):
                    raise FileNotFoundError(f"找不到 {book_file} 檔案")
                if not os.path.exists(user_file):
                    raise FileNotFoundError(f"找不到 {user_file} 檔案")
            except FileNotFoundError as e:
                print(e)


            # 開啟 CSV 檔案並匯入users資料表
            with open(user_file, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)

                for row in csvreader:
                    if len(row) < 2:
                        continue
                    username, password = row
                    cursor.execute(
                        'INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, password)
                    )


            #開啟.json檔案並匯入books資料表
            with open(book_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for book in data:
                cursor.execute(
                    'INSERT INTO books\
                        (title, author, publisher, year) VALUES (?, ?, ?, ?)',
                    (book['title'], book['author'], \
                        book['publisher'], book['year'])
                )

            conn.commit()
            conn.close()
    except Exception as e:
        print("建立資料庫時發生錯誤:", e)


#此函數為更新資料庫
def update_json_from_database():
    """
    更新 books.json 檔案，將資料庫中的書籍資料寫入 JSON 檔案中
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()

        book_list = []
        for book in books:
            book_dict = {
                'title': book[1],
                'author': book[2],
                'publisher': book[3],
                'year': book[4]
            }
            book_list.append(book_dict)

        with open(book_file, 'w', encoding='utf-8') as file:
            json.dump(book_list, file, ensure_ascii=False, indent=4)

        conn.close()
    except Exception as e:
        print("更新 JSON 檔案時發生錯誤:", e)


#函數(登入帳號密碼)
def login(account, password):
    """
    簡單的登入帳號及密碼，當使用者輸入帳號及密碼後會透過資料庫確認是否有此帳號及密碼
    """
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 檢查使用者輸入的帳號和密碼是否存在於資料庫中的 users 表中
        cursor.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (account, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user
    except Exception as e:
        print("=>", e)
        return None


#函數 功能選單
def menu():
    """
    功能選單
    """
    print(f"{'-'*19}")
    print(f"{' '*4}資料表 CRUD")
    print(f"{'-'*19}")
    print(f"{' '*4}1. 增加紀錄")
    print(f"{' '*4}2. 刪除紀錄")
    print(f"{' '*4}3. 修改紀錄")
    print(f"{' '*4}4. 查詢紀錄")
    print(f"{' '*4}5. 資料清單")
    print(f"{'-'*19}")


# 函數 選項一
def option_one():
    """
    增加紀錄，並且在新增後打開option_five()函數(資料清單)
    """
    try:
        title = input("請輸入要新增的書名:")
        author = input("請輸入要新增的作者:")
        publisher = input("請輸入要新增的出版社:")
        year = input("請輸入要新增的年份:")

        if not (title.strip() and author.strip() and publisher.strip() and year.strip()):
            raise ValueError("給定的條件不足，無法進行新增作業")

        if not year.isdigit():
            raise ValueError("年份必須為數字，請重新輸入")

        now_year = datetime.now().year
        if int(year) > now_year:
            raise ValueError("年份不可大於當前年份")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books WHERE title = ?', (title,))
        existing_book = cursor.fetchone()
        if existing_book:
            raise ValueError("資料庫已有該書名")

        cursor.execute('INSERT INTO books (title, author, publisher, year) VALUES (?, ?, ?, ?)',
                       (title, author, publisher, year))
        conn.commit()
        conn.close()

        print("異動 1 紀錄")

        # 開啟資料選單
        option_five()
    except Exception as e:
        print("=>", e)


# 函數 選項二
def option_two():
    """
    刪除紀錄，先開啟option_five(資料清單)，再輸入要刪除的書名，刪除後開啟option_five()函數(資料清單)確認結果
    """
    try:
        # 開啟資料清單
        option_five()

        bookdelete = input("請問要刪除哪一本書？")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books WHERE title = ?', (bookdelete,))
        book = cursor.fetchone()

        if not book:
            raise ValueError("資料庫未有該書名")

        if bookdelete == "":
            raise ValueError("給定的條件不足，無法進行刪除作業")

        cursor.execute('DELETE FROM books WHERE title = ?', (bookdelete,))
        conn.commit()
        conn.close()

        print("異動 1 紀錄")

        # 開啟資料清單
        option_five()
    except Exception as e:
        print("=>", e)

#函數 選項三
def option_three():
    """
    修改紀錄，先開啟option_five(資料清單)，再輸入要修改的書名，修改後開啟option_five()函數(資料清單)確認結果
    """
    try:
        # 開啟資料清單
        option_five()

        bookrevise = input("請問要修改哪一本書的書名？")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books WHERE title = ?', (bookrevise,))
        book = cursor.fetchone()

        if not bookrevise:
            raise ValueError("請輸入要修改的書名")

        if not book:
            raise ValueError("資料庫未有該書名")

        title = input("請輸入要更改的書名:")
        author = input("請輸入要更改的作者:")
        publisher = input("請輸入要更改的出版社:")
        year = input("請輸入要更改的年份:")

        if not (title.strip() and author.strip() and publisher.strip() and year.strip()):
            raise ValueError("給定的條件不足，無法進行修改作業")

        if not year.isdigit():
            raise ValueError("年份必須為數字，請重新輸入")

        now_year = datetime.now().year
        if int(year) > now_year:
            raise ValueError("年份不可大於當前年份")

        cursor.execute('''
            UPDATE books
            SET title = ?,
                author = ?,
                publisher = ?,
                year = ?
            WHERE title = ?
        ''', (title, author, publisher, year, bookrevise))

        conn.commit()
        conn.close()

        print("異動 1 紀錄")

        # 開啟資料清單
        option_five()
    except Exception as e:
        print("=>", e)


#函數 選項四
def option_four():
    """
    查詢紀錄，透過輸入的關鍵字進入資料庫查詢，查詢後顯示結果
    """
    try:
        search = input("請輸入要查詢的關鍵字:")
        query = 'SELECT * FROM books WHERE title=? OR author=? OR ' \
                'publisher=? OR year=?'

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(query, (search, search, search, search))
        books = cursor.fetchall()

        if not search:
            raise ValueError("給定的條件不足，無法進行查詢作業")
        if books:
            for book in books:
                print(f"|{'書名'.center(11, chr(12288))}|{'作者'.center(11, chr(12288))}|{'出版社'.center(11, chr(12288))}|{'年份'.center(9, chr(12288))}|")
                print(f"| {book[1].ljust(10, chr(12288))} | {book[2].ljust(10, chr(12288))} | {book[3].ljust(10, chr(12288))} | {str(book[4]).ljust(10, chr(12288))} |")
        else:
            raise ValueError("查此關鍵字")

        conn.commit()
        conn.close()
    except Exception as e:
        print("=>", e)


#函數 選項五
def option_five():
    """
    資料清單，先透過update_json_from_database()函數更新資料庫，再顯示資料庫內容
    """
    try:
        #呼叫update_json_from_database()函數(最新資料庫資料)
        update_json_from_database()

        print(f"|{'書名'.center(11, chr(12288))}|{'作者'.center(11, chr(12288))}|{'出版社'.center(11, chr(12288))}|{'年份'.center(9, chr(12288))}|")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM books')
        books = cursor.fetchall()

        for book in books:
            print(f"| {book[1].ljust(10, chr(12288))} | {book[2].ljust(10, chr(12288))} | {book[3].ljust(10, chr(12288))} | {str(book[4]).ljust(10, chr(12288))} |")

        conn.close()
    except Exception as e:
        print("顯示資料清單時發生錯誤:", e)
