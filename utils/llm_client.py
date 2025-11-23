"""
Google Gemini API 클라이언트
취약한 버전 vs 보호된 버전
"""

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ google-generativeai 패키지가 설치되지 않았습니다.")
    print("pip install google-generativeai 를 실행하세요.")
    raise

from config import Config
from core.detector import PromptInjectionDetector

# defense 모듈 import를 함수 내부로 이동하여 순환 참조 방지
def get_defense_layers():
    """방어 레이어 동적 import"""
    try:
        from defense.layer1_filter import check_input_filter
        from defense.layer2_restructure import restructure_prompt
        from defense.layer3_output_filter import check_output_filter
        return check_input_filter, restructure_prompt, check_output_filter
    except ImportError as e:
        print(f"⚠️ 방어 모듈 import 오류: {e}")
        raise

from utils.logger import log_detection

# API 설정
try:
    genai.configure(api_key=Config.GEMINI_API_KEY)
except Exception as e:
    print(f"⚠️ Gemini API 설정 오류: {e}")
    print("GEMINI_API_KEY를 .env 파일에 설정했는지 확인하세요.")

class LLMClient:
    def __init__(self):
        try:
            # 최신 Gemini 2.5 Flash 모델 사용
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.detector = PromptInjectionDetector()
            print("✅ Gemini 모델 초기화 성공: gemini-2.5-flash")
        except Exception as e:
            print(f"⚠️ gemini-2.5-flash 초기화 오류: {e}")
            print("대체 모델을 시도합니다...")
            try:
                # 대체 모델 1: gemini-2.0-flash
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.detector = PromptInjectionDetector()
                print("✅ Gemini 모델 초기화 성공: gemini-2.0-flash")
            except Exception as e2:
                print(f"⚠️ gemini-2.0-flash 초기화 오류: {e2}")
                try:
                    # 대체 모델 2: gemini-flash-latest
                    self.model = genai.GenerativeModel('gemini-flash-latest')
                    self.detector = PromptInjectionDetector()
                    print("✅ Gemini 모델 초기화 성공: gemini-flash-latest")
                except Exception as e3:
                    print(f"❌ 모든 모델 초기화 실패: {e3}")
                    raise
    
    def get_vulnerable_response(self, user_input: str, user_id: str = 'anonymous'):
        """
        방어 기능 없는 취약한 LLM 호출
        공격이 그대로 통하는 버전
        """
        # 취약한 방식: 시스템 프롬프트 + 사용자 입력 직접 연결
        prompt = f"{Config.SYSTEM_PROMPT}\n\n사용자: {user_input}\n봇:"
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # 로깅 (취약 모드)
            detection_result = self.detector.detect(user_input, user_id)
            log_detection(user_input, detection_result, response_text, is_vulnerable=True, user_id=user_id)
            
            return {
                'success': True,
                'response': response_text,
                'is_blocked': False
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API 오류 (취약 모드): {error_msg}")
            return {
                'success': False,
                'error': f"API 오류: {error_msg}",
                'is_blocked': False
            }
    
    def get_protected_response(self, user_input: str, defense_config: dict, user_id: str = 'anonymous'):
        """
        3단계 방어가 적용된 안전한 LLM 호출
        """
        # 방어 레이어 동적 로드
        check_input_filter, restructure_prompt, check_output_filter = get_defense_layers()
        
        detection_result = self.detector.detect(user_input, user_id)
        
        # Layer 1: 입력 필터링
        if defense_config.get('layer1', True):
            rule_result = check_input_filter(user_input)
            if rule_result['is_blocked']:
                response_text = f"🚫 **차단됨**: {rule_result['reason']}\n\n이 요청은 프롬프트 인젝션 공격으로 의심되어 차단되었습니다."
                log_detection(user_input, detection_result, response_text, is_vulnerable=False, user_id=user_id)
                return {
                    'success': True,
                    'response': response_text,
                    'is_blocked': True,
                    'block_reason': rule_result['reason'],
                    'detection': detection_result
                }
        
        # Layer 2: 프롬프트 재구성
        if defense_config.get('layer2', True):
            safe_prompt = restructure_prompt(user_input)
        else:
            safe_prompt = f"{Config.SYSTEM_PROMPT}\n\n사용자: {user_input}\n봇:"
        
        try:
            response = self.model.generate_content(safe_prompt)
            response_text = response.text
            
            # Layer 3: 출력 필터링
            if defense_config.get('layer3', True):
                is_leaked, filtered_response = check_output_filter(response_text)
                if is_leaked:
                    response_text = filtered_response
            
            # 로깅 (보호 모드)
            log_detection(user_input, detection_result, response_text, is_vulnerable=False, user_id=user_id)
            
            return {
                'success': True,
                'response': response_text,
                'is_blocked': False,
                'detection': detection_result
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API 오류 (보호 모드): {error_msg}")
            return {
                'success': False,
                'error': f"API 오류: {error_msg}",
                'is_blocked': False
            }

# 전역 클라이언트 인스턴스
try:
    llm_client = LLMClient()
except Exception as e:
    print(f"⚠️ LLM 클라이언트 생성 실패: {e}")
    llm_client = None