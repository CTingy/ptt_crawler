# ptt_crawler

### PTT crawler practice

Dependencies:
- `pip install -r requirements.txt`

- Or install manually:
    ```
    python3 -m pip install lxml
    python3 -m pip install beautifulsoup4
    python3 -m pip install psycopg2
    ```

Goals:

- Download all posts from a specified board for the current day, including their comments (pushes)
- Update new comments from the current day for already downloaded posts
- Store the data in PostgreSQL or save it as JSON files

Steps:

0. Update the database connection settings in `conn_info.py`
2. Run `create_table.py` to create the article and push tables
3. In `ptt.py`, add the board names you want to crawl to the `BOARD` list
4. Run `ptt.py` to save posts and their comments from the specified boards into PostgreSQL
5. To update comments, run `update_pushes.py` to check whether there are new comments for previously stored posts on the current day

Notes:

- Articles and comments are identified by the current date when being stored. There is no duplicate check, so you should only run `ptt.py` and `update_pushes.py` once per day. Otherwise, duplicate data will be inserted.
- `conn_info.py` and `ptt.py` are imported by other `.py` files. Be careful if you change their paths.
- There are two tables: `article` and `push`. The primary key `article_id` in `article` is used as the foreign key in `push`.
- The HTML structure of PTT boards often changes. If a page does not match the expected format, the following error message will be printed: `Wrong format on this page: url`
- If you only want to download posts and comments from the current day and save them as JSON files, simply run `pttjson.py`. However,
