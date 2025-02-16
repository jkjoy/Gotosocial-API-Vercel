from flask import Flask, jsonify, request, make_response
import requests
import os

app = Flask(__name__)

@app.route('/api', methods=['GET', 'OPTIONS'])
def get_user_timeline():
    # 创建一个响应对象，用于精确控制头部
    response = make_response()

    # CORS 配置
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'

    # 处理预检请求
    if request.method == 'OPTIONS':
        response.status_code = 204
        return response

    # 从环境变量获取配置
    HOST = os.environ.get('HOST')
    USER_ID = os.environ.get('USER_ID')
    TOKEN = os.environ.get('TOKEN')

    # 检查环境变量是否完整
    if not all([HOST, USER_ID, TOKEN]):
        response.data = jsonify({
            'error': '缺少必要的环境配置',
            'details': {
                'HOST': bool(HOST),
                'USER_ID': bool(USER_ID),
                'TOKEN': bool(TOKEN)
            }
        }).get_data()
        response.status_code = 400
        response.mimetype = 'application/json'
        return response

    # 构建 API URL
    url = f"{HOST}/api/v1/accounts/{USER_ID}/statuses"
    
    # 查询参数
    params = {
        'limit': request.args.get('limit', 1000),
        'exclude_replies': 'true',
        'only_public': 'true'
    }

    # 请求头
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "User-Agent": "Python/Vercel-API",
        "Authorization": f"Bearer {TOKEN}"
    }

    try:
        # 发起请求
        api_response = requests.get(url, params=params, headers=headers)
        
        # 检查响应状态
        if api_response.status_code != 200:
            response.data = jsonify({
                'error': '获取时间线失败',
                'status_code': api_response.status_code,
                'message': api_response.text
            }).get_data()
            response.status_code = 400
            response.mimetype = 'application/json'
            return response

        # 直接返回源数据结构
        response.data = api_response.content
        response.status_code = 200
        response.mimetype = 'application/json'
        return response

    except Exception as e:
        response.data = jsonify({
            'error': str(e)
        }).get_data()
        response.status_code = 500
        response.mimetype = 'application/json'
        return response

@app.route('/', methods=['GET'])
def index():
    response = make_response(jsonify({
        'message': 'Gotosocial Timeline API',
        'endpoints': [
            '/api - Get user timeline'
        ]
    }))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Vercel 部署需要
def create_app():
    return app