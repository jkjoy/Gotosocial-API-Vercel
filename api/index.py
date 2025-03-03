from flask import Flask, jsonify, request, make_response
import requests
import os

app = Flask(__name__)

@app.route('/api', methods=['GET', 'OPTIONS'])
def get_user_timeline():
    # 创建响应对象
    response = make_response()
    
    # CORS配置
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'

    # 处理预检请求
    if request.method == 'OPTIONS':
        return response

    # 环境变量校验
    HOST = os.environ.get('HOST')
    USER_ID = os.environ.get('USER_ID')
    TOKEN = os.environ.get('TOKEN')
    
    if not all([HOST, USER_ID, TOKEN]):
        error_details = {
            'error': '缺少必要的环境配置',
            'details': {
                'HOST': bool(HOST),
                'USER_ID': bool(USER_ID),
                'TOKEN': bool(TOKEN)
            }
        }
        response.data = jsonify(error_details)
        response.status_code = 400
        response.mimetype = 'application/json'
        return response

    # 构建查询参数
    params = {
        'limit': request.args.get('limit', 1000),
        'exclude_replies': 'true',
        'only_public': 'true',
        'max_id': request.args.get('max_id'),
        'since_id': request.args.get('since_id'),
        'min_id': request.args.get('min_id')
    }

    # 过滤空值参数
    params = {k: v for k, v in params.items() if v is not None}

    try:
        # 发起API请求
        api_response = requests.get(
            url=f"{HOST}/api/v1/accounts/{USER_ID}/statuses",
            params=params,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "Python/Vercel-API",
                "Authorization": f"Bearer {TOKEN}"
            }
        )

        # 转发分页相关headers
        if 'Link' in api_response.headers:
            response.headers['Link'] = api_response.headers['Link']
        if 'X-RateLimit-Limit' in api_response.headers:
            response.headers['X-RateLimit-Limit'] = api_response.headers['X-RateLimit-Limit']
        if 'X-RateLimit-Remaining' in api_response.headers:
            response.headers['X-RateLimit-Remaining'] = api_response.headers['X-RateLimit-Remaining']

        # 设置响应数据
        response.data = api_response.content
        response.status_code = api_response.status_code
        response.mimetype = 'application/json'
        return response

    except requests.exceptions.RequestException as e:
        error_info = {
            'error': '上游服务请求失败',
            'details': str(e)
        }
        response.data = jsonify(error_info)
        response.status_code = 502
        response.mimetype = 'application/json'
        return response
    except Exception as e:
        error_info = {
            'error': '服务器内部错误',
            'details': str(e)
        }
        response.data = jsonify(error_info)
        response.status_code = 500
        response.mimetype = 'application/json'
        return response

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'GoSocial Timeline API',
        'endpoints': {
            '/api': {
                'methods': ['GET'],
                'description': '获取用户时间线',
                'parameters': {
                    'limit': '返回结果数量 (默认: 1000)',
                    'max_id': '获取早于该ID的结果',
                    'since_id': '获取晚于该ID的结果',
                    'min_id': '获取不早于该ID的结果'
                }
            }
        }
    })

def create_app():
    return app

if __name__ == '__main__':
    app.run()
