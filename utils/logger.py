"""
탐지 결과 로깅 및 분석
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json
from config import Config

class DetectionLogger:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """데이터베이스 초기화"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                user_input TEXT,
                is_malicious BOOLEAN,
                risk_score REAL,
                detected_patterns TEXT,
                detection_method TEXT,
                recommendation TEXT,
                response TEXT,
                is_vulnerable_mode BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_requests INTEGER DEFAULT 0,
                blocked_requests INTEGER DEFAULT 0,
                warned_requests INTEGER DEFAULT 0,
                false_positives INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log(self, user_input, detection_result, response='', is_vulnerable=False, user_id='anonymous'):
        """탐지 결과 로깅"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO detection_logs 
            (user_id, user_input, is_malicious, risk_score, detected_patterns, 
             detection_method, recommendation, response, is_vulnerable_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            user_input,
            detection_result['is_malicious'],
            detection_result['risk_score'],
            json.dumps(detection_result['detected_patterns'], ensure_ascii=False),
            detection_result['detection_method'],
            detection_result['recommendation'],
            response,
            is_vulnerable
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_logs(self, limit=50):
        """최근 로그 조회"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM detection_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self):
        """통계 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_malicious = 1 THEN 1 ELSE 0 END) as malicious,
                AVG(risk_score) as avg_risk,
                SUM(CASE WHEN recommendation = 'BLOCK' THEN 1 ELSE 0 END) as blocked,
                SUM(CASE WHEN recommendation = 'WARN' THEN 1 ELSE 0 END) as warned
            FROM detection_logs
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'total_requests': stats[0],
            'malicious_requests': stats[1],
            'avg_risk_score': round(stats[2] or 0, 2),
            'blocked_count': stats[3],
            'warned_count': stats[4],
            'success_rate': round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 1)
        }

# 전역 로거 인스턴스
logger = DetectionLogger()

def log_detection(user_input, result, response='', is_vulnerable=False, user_id='anonymous'):
    """로깅 헬퍼 함수"""
    logger.log(user_input, result, response, is_vulnerable, user_id)