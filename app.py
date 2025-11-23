"""
Flask 메인 애플리케이션
프롬프트 인젝션 방어 시스템 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify, session
from config import Config
from utils.llm_client import llm_client
from utils.logger import logger
from attacks.scenarios import ATTACK_SCENARIOS, get_all_attacks
import uuid

app = Flask(__name__)
app.config.from_object(Config)

@app.before_request
def before_request():
    """세션에 사용자 ID 할당"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    """메인 대시보드"""
    stats = logger.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/vulnerable')
def vulnerable():
    """취약한 챗봇 데모"""
    return render_template('vulnerable.html')

@app.route('/protected')
def protected():
    """방어 적용 챗봇 데모"""
    return render_template('protected.html')

@app.route('/comparison')
def comparison():
    """Before/After 비교 페이지"""
    attacks = get_all_attacks()
    return render_template('comparison.html', attacks=attacks)

@app.route('/logs')
def logs():
    """로그 뷰어"""
    recent_logs = logger.get_recent_logs(limit=100)
    return render_template('logs.html', logs=recent_logs)

@app.route('/attack-simulator')
def attack_simulator():
    """공격 시뮬레이터"""
    return render_template('attack_simulator.html', scenarios=ATTACK_SCENARIOS)

# === API 엔드포인트 ===

@app.route('/api/chat/vulnerable', methods=['POST'])
def api_chat_vulnerable():
    """취약한 챗봇 API"""
    data = request.get_json()
    user_input = data.get('message', '')
    user_id = session.get('user_id', 'anonymous')
    
    if not user_input:
        return jsonify({'success': False, 'error': '메시지를 입력해주세요'}), 400
    
    result = llm_client.get_vulnerable_response(user_input, user_id)
    return jsonify(result)

@app.route('/api/chat/protected', methods=['POST'])
def api_chat_protected():
    """방어 적용 챗봇 API"""
    data = request.get_json()
    user_input = data.get('message', '')
    defense_config = data.get('defense', {
        'layer1': True,
        'layer2': True,
        'layer3': True
    })
    user_id = session.get('user_id', 'anonymous')
    
    if not user_input:
        return jsonify({'success': False, 'error': '메시지를 입력해주세요'}), 400
    
    result = llm_client.get_protected_response(user_input, defense_config, user_id)
    return jsonify(result)

@app.route('/api/comparison', methods=['POST'])
def api_comparison():
    """비교 테스트 API - 동일한 입력에 대해 두 버전 모두 테스트"""
    data = request.get_json()
    user_input = data.get('message', '')
    user_id = session.get('user_id', 'anonymous')
    
    if not user_input:
        return jsonify({'success': False, 'error': '메시지를 입력해주세요'}), 400
    
    # 취약한 버전
    vulnerable_result = llm_client.get_vulnerable_response(user_input, user_id)
    
    # 보호된 버전
    protected_result = llm_client.get_protected_response(
        user_input, 
        {'layer1': True, 'layer2': True, 'layer3': True},
        user_id
    )
    
    return jsonify({
        'success': True,
        'vulnerable': vulnerable_result,
        'protected': protected_result
    })

@app.route('/api/statistics')
def api_statistics():
    """통계 데이터 API"""
    stats = logger.get_statistics()
    return jsonify(stats)

@app.route('/api/logs')
def api_logs():
    """로그 데이터 API"""
    limit = request.args.get('limit', 50, type=int)
    logs = logger.get_recent_logs(limit)
    return jsonify({'logs': logs})

if __name__ == '__main__':
    print("=" * 60)
    print("🛡️  프롬프트 인젝션 방어 시스템 시작")
    print("=" * 60)
    print(f"📍 서버 주소: http://localhost:5000")
    print(f"🔐 비밀 코드: {Config.SECRET_CODE}")
    print("=" * 60)
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)