from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import sys

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'Agentic Code Agent is running!', 
        'version': '1.0',
        'endpoints': {
            'health': 'GET /',
            'execute': 'POST /api/agent'
        },
        'supported_languages': ['python']
    })

@app.route('/api/agent', methods=['POST', 'OPTIONS'])
def handle_request():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        tool_name = data.get('tool')
        parameters = data.get('parameters', {})

        if tool_name == 'executeCode':
            return execute_code(parameters)
        else:
            return jsonify({'error': f'Unknown tool: {tool_name}'}), 400

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def execute_code(params):
    code = params.get('code', '')
    language = params.get('language', 'python')

    if not code.strip():
        return jsonify({
            'success': False,
            'data': {
                'text': '',
                'error': 'No code provided',
                'logs': {'stdout': [], 'stderr': ['No code provided']}
            }
        })

    if language.lower() == 'python':
        return execute_python(code)
    else:
        return jsonify({
            'success': False,
            'data': {
                'text': '',
                'error': f'Language {language} not supported',
                'logs': {'stdout': [], 'stderr': [f'Unsupported language: {language}']}
            }
        })

def execute_python(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_file], 
            capture_output=True, 
            text=True, 
            timeout=30
        )

        return jsonify({
            'success': result.returncode == 0,
            'data': {
                'text': result.stdout,
                'error': result.stderr if result.stderr else None,
                'logs': {
                    'stdout': result.stdout.split('\n') if result.stdout else [],
                    'stderr': result.stderr.split('\n') if result.stderr else []
                }
            }
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'data': {
                'text': '',
                'error': 'Code execution timeout (30s limit)',
                'logs': {'stdout': [], 'stderr': ['Timeout after 30 seconds']}
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {
                'text': '',
                'error': str(e),
                'logs': {'stdout': [], 'stderr': [str(e)]}
            }
        })
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
