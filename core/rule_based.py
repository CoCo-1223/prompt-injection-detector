"""
규칙 기반 프롬프트 인젝션 탐지
OWASP LLM01 공격 패턴 기반
"""

import re
import json
from pathlib import Path

class RuleBasedDetector:
    def __init__(self):
        self.patterns = self._load_patterns()
        
    def _load_patterns(self):
        """공격 패턴 JSON에서 로드"""
        pattern_file = Path('data/attack_patterns.json')
        if pattern_file.exists():
            with open(pattern_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_patterns()
    
    def _get_default_patterns(self):
        """기본 공격 패턴 정의"""
        return {
            "direct_injection": {
                "patterns": [
                    r"ignore\s+(previous|all|above|prior)\s+instructions?",
                    r"disregard\s+(previous|all|above|prior)",
                    r"forget\s+(everything|all|previous)",
                    r"new\s+instructions?:",
                    r"you\s+are\s+now",
                    r"pretend\s+(to\s+be|you\s+are)",
                    r"act\s+as",
                    r"roleplay",
                    r"system\s*:",
                    r"assistant\s*:",
                ],
                "risk_level": "HIGH",
                "action": "BLOCK"
            },
            "information_extraction": {
                "patterns": [
                    r"(secret|hidden|private)\s+(code|password|key)",
                    r"reveal\s+(the|your)\s+(secret|code|password)",
                    r"what\s+is\s+(the|your)\s+(secret|code)",
                    r"tell\s+me\s+(the|your)\s+(secret|code)",
                    r"system\s+prompt",
                    r"original\s+instructions",
                    r"비밀\s*코드",
                    r"시스템\s*프롬프트",
                ],
                "risk_level": "HIGH",
                "action": "BLOCK"
            },
            "korean_injection": {
                "patterns": [
                    r"이전\s*(지시|명령|규칙).*무시",
                    r"(무시|잊어|삭제).*이전",
                    r"너는\s*이제",
                    r"~인\s*척",
                    r"역할극",
                    r"비밀.*말해",
                ],
                "risk_level": "HIGH",
                "action": "BLOCK"
            },
            "jailbreak_attempts": {
                "patterns": [
                    r"dan\s+mode",
                    r"developer\s+mode",
                    r"evil\s+mode",
                    r"do\s+anything\s+now",
                    r"opposite\s+mode",
                ],
                "risk_level": "HIGH",
                "action": "BLOCK"
            },
            "prompt_leaking": {
                "patterns": [
                    r"print\s+(your|the)\s+prompt",
                    r"show\s+me\s+(your|the)\s+(prompt|instructions)",
                    r"output\s+(your|the)\s+instructions",
                    r"프롬프트.*출력",
                    r"지시문.*보여",
                ],
                "risk_level": "MEDIUM",
                "action": "WARN"
            }
        }
    
    def check(self, user_input: str) -> dict:
        """
        입력값에 대한 규칙 기반 검사
        """
        user_input_lower = user_input.lower()
        result = {
            'is_malicious': False,
            'risk_score': 0.0,
            'patterns': [],
            'action': 'ALLOW'
        }
        
        max_risk = 0.0
        
        for category, data in self.patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    result['is_malicious'] = True
                    result['patterns'].append({
                        'category': category,
                        'pattern': pattern,
                        'risk_level': data['risk_level']
                    })
                    
                    # 위험도 점수 계산
                    risk_value = {
                        'HIGH': 0.9,
                        'MEDIUM': 0.6,
                        'LOW': 0.3
                    }.get(data['risk_level'], 0.5)
                    
                    max_risk = max(max_risk, risk_value)
                    result['action'] = data['action']
        
        result['risk_score'] = max_risk
        return result