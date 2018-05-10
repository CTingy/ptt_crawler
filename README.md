# ptt_crawler

### ptt crawler practice

Dependencies:
- `pip install -r requirements.txt`

- 或是手動安裝
```
python3 -m pip install lxml
python3 -m pip install beautifulsoup4
python3 -m pip install psycopg2
``` 

目標：

- 下載指定看板的當日文章和文章下推文
- 更新已下載文章中的當日推文
- 將資料存入postgresql

步驟：

0. 先修改 `conn_info.py` 中的資料庫連線資訊
2. 執行 `create_table.py` 建立文章表格和推文表格
3. 在 `ptt.py` 中的`BOARD`串列中輸入想要爬的看板名稱
4. 運行`ptt.py`，把指定看板的文章內容和推文存入postgresql
5. 若要更新推文，執行`update_pushes.py` 看以前存的文章下面有無當日新推文

說明：

- 儲存文章和推文時是以當天日期做識別，沒有檢查資料是否有重複，一天只要run一次`ptt.py` & `update_pushes.py`就好了，要不然會重複存到相同內容
- `conn_info.py` & `ptt.py`會被`import`到其他`.py`中，若要更改路徑請注意
- 表格有兩個，分別是文章`article`與推文`push`，其中`article`的primary key:`article_id`為`push`的 foreign key
- PTT網頁板格式時常跑掉，若該網頁格式不符，則會印出錯誤訊息：`Wrong format on this page: url`