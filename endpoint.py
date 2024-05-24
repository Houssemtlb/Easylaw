from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run-scraping', methods=['GET'])
def run_script():
    try:
        result = subprocess.run(['python', 'MAIN_SCRIPT.py'], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({
                'status': 'error',
                'message': 'Script execution failed',
                'error': result.stderr
            }), 500

        return jsonify({
            'status': 'success',
            'message': 'Script executed successfully',
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
