import os, json, sqlite3, shelve
import pandas as pd
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

DB_DIR_PATH = os.path.join(__location__, ".database")
os.makedirs(DB_DIR_PATH, exist_ok=True)
DB_PATH = os.path.join(DB_DIR_PATH, "crawler321.db")
CRAWLER_TABLE = "crawler_table"
ID_TABLE = "id_table"
SHELVE_PATH = os.path.join(DB_DIR_PATH, "crawler321_object")

def save_objects(key, value):
    with shelve.open(SHELVE_PATH) as db:
        db[key] = value
def load_objects(key):
    with shelve.open(SHELVE_PATH) as db:
        return db.get(key)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {CRAWLER_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT,
            url TEXT UNIQUE,
            strategy TEXT,
            params  TEXT,
            result  TEXT,
            status  INTEGER,
            time    REAL
        )
        '''
    )
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {ID_TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT UNIQUE          
        )
        '''
    )
    conn.commit()
    conn.close()
def check_db():
    if not DB_PATH:
        raise ValueError("crawler321.db is empty or not existing")
def insert_data(identifier: str, url: str, strategy: str, params: str, result: str, status: int, time):
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {CRAWLER_TABLE} 
        (identifier, url, strategy, params, result, status, time)
        VALUES (?, ?, ?, ?, ? ,?, ?)
        ON CONFLICT(url) DO UPDATE SET
        identifier = excluded.identifier,
        strategy = excluded.strategy,
        params = excluded.params,
        result = excluded.result,
        status = excluded.status,
        time = excluded.time
        ''', (identifier, url, strategy, params, result, status, time)
    )
    conn.commit()
    conn.close()

def delete_by_identifier(identifier: str):
    check_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f'''
            DELETE FROM {CRAWLER_TABLE}
            WHERE identifier = ?
        ''', (identifier,)
        )
        cursor.execute(f'''
            DELETE FROM {ID_TABLE}
            WHERE identifier = ?
        ''', (identifier,)
        )
        conn.commit()
        conn.close()
        print(f"[Database] record {identifier} removed successfully!")
    except Exception as e:
        print(f"[Database] Error occurred, {identifier} removed failed: {e}")
        pass
def delete_data_all():
    check_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {CRAWLER_TABLE}')
        cursor.execute(f'DELETE FROM {ID_TABLE}')
        # reset the increment sequence of tables
        cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{CRAWLER_TABLE}"')
        cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{ID_TABLE}"')
        conn.commit()
        conn.close()
        print(f"[Database] all records removed successfully!")
    except Exception as e:
        print(f"[Database] Error occurred records removed failed: {e}")

def delete_tables_all():
    check_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE {CRAWLER_TABLE}')
        cursor.execute(f'DROP TABLE {ID_TABLE}')
        # reset the increment sequence of tables
        conn.commit()
        conn.close()
        print(f"[Database] all tables removed successfully!")
    except Exception as e:
        print(f"[Database] Error occurred tables removed failed: {e}")

def query_by_identifier(identifier: str) -> pd.DataFrame:
    check_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT url, strategy, params, status, time 
            FROM {CRAWLER_TABLE}
            WHERE identifier = ?
        ''',(identifier, )
        )
        # 
        # reset the increment sequence of tables 
        rows = cursor.fetchall()
        colunms = [des[0] for des in cursor.description]
        df = pd.DataFrame(rows, columns=colunms)
        conn.close()
        return df
    except Exception as e:
        print(f"[Database] Error occurred find {identifier} failed: {e}")

def query_and_update(identifier: str, url: str, strategy: str, params: str, time) -> dict:
    check_db()
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
            SELECT id, strategy, params, result, status 
            FROM {CRAWLER_TABLE}
            WHERE url = ?''', (url,)
        )
        records = cursor.fetchall()
        if not records:
            conn.close()
            return {}
    except Exception as e:
        print(f"[Database] {url} query failed: {e}")
    for record in records:
        res_id, res_strategy, res_params, res_result, status= record
        if res_strategy == strategy and res_params == params and status==200:
            try:
                cursor.execute(f'''
                    UPDATE {CRAWLER_TABLE}
                    SET identifier = ?, time = 0
                    WHERE id = ?
                ''', (identifier, res_id)
                )
                conn.commit()
                conn.close()
                return json.loads(res_result)
            except Exception as e:
                print(f"[DataBase] {identifier} update failed: {e}")
        else:
            conn.close()
            return {"id": res_id}
    return {}

def insert_identifier(identifier: str):
    check_db()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute(f'SELECT 1 FROM {ID_TABLE} WHERE identifier = ?', (identifier,))
        res = cursor.fetchone()
        if not cursor.fetchone():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO {ID_TABLE} (identifier) VALUES (?)', (identifier, ))
            conn.commit()
            conn.close()
        return res is not None
    except Exception as e:
        print(f"[Database] Error insert {identifier} failed: {e}")
# if not os.path.exists(DB_PATH):
init_db()
    