"""
사용 가능한 Gemini 모델 확인
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 사용 가능한 Gemini 모델 목록:\n")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   설명: {model.display_name}")
        print(f"   지원 메서드: {', '.join(model.supported_generation_methods)}")
        print()

print("\n추천 모델:")
print("- gemini-1.5-flash (빠르고 효율적)")
print("- gemini-1.5-pro (더 정확하지만 느림)")