import os
import shelve
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class CrawlerDatabase:
    """爬虫数据库服务 (独立于RunCrawler) """
    
    def __init__(self, db_path: str = None, objects_path: str = None):
        """外部创建数据库实例"""
        self.db_path = db_path or os.path.join(
            os.path.dirname(__file__), 
            ".database", 
            "crawler321.db"
        )
        self.objects_path = objects_path or os.path.join(
            os.path.dirname(__file__),
            ".database",
            "crawler321_object"
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 爬虫请求表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crawler_id TEXT NOT NULL,
                url TEXT NOT NULL,
                method TEXT DEFAULT 'GET',
                status_code INTEGER,
                strategy TEXT,
                params TEXT,
                elapsed_time REAL,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                cache_hit BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 缓存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                keywords TEXT,
                description TEXT,
                author TEXT,
                source TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        # 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_id ON crawl_requests(crawler_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON crawl_requests(url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_data(cache_key)')
        conn.commit()
        conn.close()
    
    def insert_crawl_result(self, data: Dict[str, Any]) -> int:
        """插入爬取结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crawl_requests 
            (crawler_id, url, method, status_code, 
             strategy, params, elapsed_time, success, 
             error_message, cache_hit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('crawler_id'),
            data.get('url'),
            data.get('method', 'GET'),
            data.get('status_code'),
            data.get('strategy'),
            data.get('params'),
            data.get('elapsed_time'),
            data.get('success', True),
            data.get('error_message'),
            data.get('cache_hit', False)
        ))
        conn.commit()
        rowid = cursor.lastrowid
        conn.close()
        return rowid
    
    def get_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT url, title, keywords, description, author, source, content, expires_at
            FROM cache_data 
            WHERE cache_key = ?
        ''', (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # 检查是否过期
            if row['expires_at']:
                expires_at = datetime.fromisoformat(row['expires_at'])
                if datetime.now() > expires_at:
                    self.delete_cache(cache_key)
                    return None
            
            return dict(row)
        return None
    
    def set_cache(self, cache_key: str, data: Dict[str, Any], ttl: int = 3600):
        """设置缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        expires_at = None
        if ttl > 0:
            expires_at = datetime.now().timestamp() + ttl
        cursor.execute('''
            INSERT OR REPLACE INTO cache_data 
            (cache_key, url, title, keywords, description, author, source, content, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            cache_key,
            data.get('url'),
            data.get('title'),
            data.get('keywords'),
            data.get('description'),
            data.get('author'),
            data.get('source'),
            data.get('content'),
            expires_at
        ))
        conn.commit()
        conn.close()
    
    def get_crawler_data(self, crawler_id: str) -> pd.DataFrame:
        """获取指定爬虫的数据"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT * FROM crawl_requests 
            WHERE crawler_id = ?
            ORDER BY created_at DESC
        '''
        try:
            df = pd.read_sql_query(query, conn, params=(crawler_id,))
            return df
        except Exception as e:
            logger.error(f"获取爬虫数据失败: {str(e)}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def clear_crawler_data(self, crawler_id: str):
        """清除指定爬虫的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM crawl_requests WHERE crawler_id = ?', (crawler_id,))
        conn.commit()
        conn.close()
        logger.info(f"已清除爬虫 {crawler_id} 的数据")
    
    def get_statistics(self, crawler_id: str) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT 
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests,
                SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                AVG(elapsed_time) as avg_response_time
            FROM crawl_requests 
            WHERE crawler_id = ?
        '''
        try:
            df = pd.read_sql_query(query, conn, params=(crawler_id,))
            if not df.empty:
                return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
        finally:
            conn.close()
        return {}
    
    def delete_cache(self, cache_key: str):
        """删除缓存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache_data WHERE cache_key = ?', (cache_key,))
        conn.commit()
        conn.close()
    def get_crawler_id(self):
        with shelve.open(self.objects_path) as db:
            return db.get("crawler_id")
    def update_crawler_id(self, id: str):
        with shelve.open(self.objects_path) as db:
            db["crawler_id"] = id

# 全局数据库实例（可选）
_db_instance = None

def get_database(db_path: str = None) -> CrawlerDatabase:
    """获取数据库实例（单例模式）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = CrawlerDatabase(db_path)
    return _db_instance