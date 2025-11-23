"""
에러 수정을 위한 스크립트
"""

import os
from pathlib import Path

def create_init_files():
    """__init__.py 파일 생성"""
    modules = {
        'core': [
            'from .detector import PromptInjectionDetector',
            'from .rule_based import RuleBasedDetector',
            '',
            '__all__ = ["PromptInjectionDetector", "RuleBasedDetector"]'
        ],
        'defense': [
            'from .layer1_filter import check_input_filter',
            'from .layer2_restructure import restructure_prompt',
            'from .layer3_output_filter import check_output_filter',
            '',
            '__all__ = ["check_input_filter", "restructure_prompt", "check_output_filter"]'
        ],
        'utils': [
            'from .logger import DetectionLogger, log_detection',
            '',
            '__all__ = ["DetectionLogger", "log_detection"]'
        ],
        'attacks': [
            'from .scenarios import ATTACK_SCENARIOS, get_all_attacks',
            '',
            '__all__ = ["ATTACK_SCENARIOS", "get_all_attacks"]'
        ]
    }
    
    for module, content in modules.items():
        init_file = Path(module) / '__init__.py'
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"✅ Created/Updated {init_file}")

def check_dependencies():
    """필요한 패키지 확인"""
    try:
        import google.generativeai
        print("✅ google-generativeai 설치됨")
    except ImportError:
        print("❌ google-generativeai 미설치")
        print("   실행: pip install google-generativeai")
    
    try:
        import flask
        print("✅ flask 설치됨")
    except ImportError:
        print("❌ flask 미설치")
        print("   실행: pip install flask")

def main():
    print("=" * 50)
    print("에러 수정 스크립트 실행")
    print("=" * 50)
    
    print("\n1. __init__.py 파일 생성/업데이트")
    create_init_files()
    
    print("\n2. 의존성 패키지 확인")
    check_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ 수정 완료!")
    print("=" * 50)

if __name__ == '__main__':
    main()