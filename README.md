# ptt_crawler

### ptt crawler practice

**目標**
- 下載指定看板的最新文章和文章下推文
- 更新已下載文章中的每日推文
- 將資料存入postgresql

**步驟**
0. 記得先修改各個.py中的資料庫連線資訊
1. run create_table.py 建立文章表格和推文表格
2. 在ptt.py 中的BOARD輸入想要爬的看板名稱
3. 運行ptt.py，把指定看板的文章內容和推文存入postgresql
4. run update_pushes.py 看以前存的文章下面有無新的推文

註：儲存資料的時候沒有檢查重複，一天只能存一次要不然會重複存到相同內容(ptt.py & update_pushes.py)
