"""
Layer 3: 출력값 필터 (유출 방지)
AI 응답에 민감 정보가 포함되어 있는지 검사
"""

import re
from config import Config

# 민감 키워드 정의
SENSITIVE_KEYWORDS = [
    Config.SECRET_CODE,
    "CBNU_SECURE",
    "비밀 코드",
    "secret code",
    "비밀관리자",
    "관리자 코드",
]

# AI 시스템 노출 키워드
SYSTEM_EXPOSURE_KEYWORDS = [
    "Gemini",
    "Google AI",
    "AI 모델",
    "시스템 프롬프트",
    "system prompt",
    "original instructions",
    "원래 지시",
]

def check_output_filter(response_text: str) -> tuple:
    """
    응답에 민감 정보가 포함되어 있는지 검사
    Returns: (is_leaked: bool, filtered_response: str)
    """
    response_lower = response_text.lower()
    
    # 민감 정보 체크
    for keyword in SENSITIVE_KEYWORDS:
        if keyword.lower() in response_lower:
            return True, f"""🚨 **민감 정보 유출 차단**

응답에 민감 정보가 포함되어 있어 차단되었습니다.
- 탐지된 키워드: {keyword}
- 원본 응답은 보안상의 이유로 표시되지 않습니다.

✅ Layer 3 방어가 성공적으로 작동했습니다."""
    
    # 시스템 노출 체크
    for keyword in SYSTEM_EXPOSURE_KEYWORDS:
        if keyword.lower() in response_lower:
            # 경고만 표시하고 응답은 허용 (덜 심각)
            return True, f"""⚠️ **시스템 정보 노출 감지**

응답에 AI 시스템 정보가 포함되어 있어 필터링되었습니다.

[필터링된 응답]"""
    
    return False, response_text