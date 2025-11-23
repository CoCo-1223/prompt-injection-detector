"""
Layer 1: 입력값 필터 (룰 기반 탐지)
사용자 입력에 명백한 공격 패턴이 있는지 검사
"""

import re
import json
from pathlib import Path

def load_patterns():
    """공격 패턴 로드"""
    pattern_file = Path('data/attack_patterns.json')
    if pattern_file.exists():
        with open(pattern_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

PATTERNS = load_patterns()

def check_input_filter(user_input: str) -> dict:
    """
    입력값에 공격 패턴이 있는지 검사
    Returns: {
        'is_blocked': bool,
        'reason': str,
        'matched_pattern': str,
        'category': str
    }
    """
    user_input_lower = user_input.lower()
    
    for category, data in PATTERNS.items():
        for pattern in data['patterns']:
            match = re.search(pattern, user_input_lower, re.IGNORECASE)
            if match:
                return {
                    'is_blocked': data['action'] == 'BLOCK',
                    'reason': f"{data['description']} 감지",
                    'matched_pattern': pattern,
                    'category': category,
                    'risk_level': data['risk_level']
                }
    
    return {
        'is_blocked': False,
        'reason': '',
        'matched_pattern': '',
        'category': ''
    }