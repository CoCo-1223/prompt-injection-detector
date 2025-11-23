"""
통합 프롬프트 인젝션 탐지 엔진
규칙 기반 + ML 기반 + 행동 분석을 통합
"""

from typing import Dict, Tuple
from .rule_based import RuleBasedDetector
from .behavior_analyzer import BehaviorAnalyzer
from utils.logger import log_detection

class PromptInjectionDetector:
    def __init__(self):
        self.rule_detector = RuleBasedDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        
    def detect(self, user_input: str, user_id: str = None) -> Dict:
        """
        통합 탐지 수행
        Returns: {
            'is_malicious': bool,
            'risk_score': float (0-1),
            'detected_patterns': list,
            'detection_method': str,
            'recommendation': str
        }
        """
        result = {
            'is_malicious': False,
            'risk_score': 0.0,
            'detected_patterns': [],
            'detection_method': None,
            'recommendation': 'ALLOW'
        }
        
        # 1. 규칙 기반 탐지
        rule_result = self.rule_detector.check(user_input)
        
        if rule_result['is_malicious']:
            result['is_malicious'] = True
            result['risk_score'] = rule_result['risk_score']
            result['detected_patterns'] = rule_result['patterns']
            result['detection_method'] = 'RULE_BASED'
            result['recommendation'] = rule_result['action']
            
        # 2. 행동 패턴 분석 (연속 시도 탐지)
        if user_id:
            behavior_result = self.behavior_analyzer.analyze(user_id, user_input)
            if behavior_result['suspicious']:
                result['is_malicious'] = True
                result['risk_score'] = max(result['risk_score'], behavior_result['risk_score'])
                result['detected_patterns'].append('SUSPICIOUS_BEHAVIOR')
                result['detection_method'] = 'BEHAVIOR_ANALYSIS'
        
        # 3. 로그 기록
        log_detection(user_input, result)
        
        return result