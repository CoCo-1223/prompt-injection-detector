"""
사용자 행동 패턴 분석
연속적인 공격 시도 탐지
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta

class BehaviorAnalyzer:
    def __init__(self, time_window=60, max_attempts=5):
        self.user_history = defaultdict(lambda: deque(maxlen=20))
        self.time_window = time_window  # 초
        self.max_attempts = max_attempts
        
    def analyze(self, user_id: str, user_input: str) -> dict:
        """
        사용자의 최근 행동 패턴 분석
        """
        current_time = datetime.now()
        
        # 사용자 기록 업데이트
        self.user_history[user_id].append({
            'input': user_input,
            'timestamp': current_time
        })
        
        # 최근 시간 윈도우 내의 요청만 확인
        recent_requests = [
            req for req in self.user_history[user_id]
            if current_time - req['timestamp'] <= timedelta(seconds=self.time_window)
        ]
        
        # 의심스러운 패턴 확인
        suspicious = False
        risk_score = 0.0
        
        # 1. 짧은 시간에 너무 많은 요청
        if len(recent_requests) > self.max_attempts:
            suspicious = True
            risk_score = 0.7
            
        # 2. 유사한 패턴의 반복 시도
        if self._check_repetitive_attempts(recent_requests):
            suspicious = True
            risk_score = max(risk_score, 0.8)
        
        return {
            'suspicious': suspicious,
            'risk_score': risk_score,
            'recent_count': len(recent_requests)
        }
    
    def _check_repetitive_attempts(self, requests) -> bool:
        """유사한 입력의 반복 확인"""
        if len(requests) < 3:
            return False
            
        keywords = ['ignore', 'secret', 'code', 'prompt', '무시', '비밀']
        recent_inputs = [req['input'].lower() for req in requests[-5:]]
        
        matches = sum(
            1 for inp in recent_inputs 
            if any(kw in inp for kw in keywords)
        )
        
        return matches >= 3