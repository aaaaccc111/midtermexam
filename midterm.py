import pack.modu as lib
import os
import sqlite3


db_file = "libary.db"
user_file = "user.csv"
book_file = "books.json"

# 判斷libary.db資料庫是否存在
if not os.path.exists(db_file):
    lib.create_db(db_file, user_file, book_file)

# 建立連結資料庫
conn = sqlite3.connect(db_file)

while True:
    account = input("請輸入帳號:")
    password = input("請輸入密碼:")
    user_info = lib.login(account, password)
    if user_info:
        break
    else:
        continue

while True:
    lib.menu()

    options = input("選擇要執行的功能(Enter離開):")

    # 輸入enter則跳離迴圈(離開)
    if options == "":
        break

    # 判斷輸入是否為數字
    if not options.isdigit():
        print("無效的選項")
        continue

    # 將輸入的選項轉換為整數
    options = int(options)

    # 選項1: 增加紀錄
    if options == 1:
        lib.option_one()

    # 選項2: 刪除紀錄
    elif options == 2:
        lib.option_two()

    # 選項3: 修改紀錄
    elif options == 3:
        lib.option_three()

    # 選項4: 查詢紀錄
    elif options == 4:
        lib.option_four()

    # 選項5: 資料清單
    elif options == 5:
        lib.option_five()

    # 輸入超過選項的數字則顯示無效選項
    elif options >= 6 or options <= 0:
        print("=>無效的選項")
        continue

conn.close()
