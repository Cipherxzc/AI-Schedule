from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

import interact
import make_schedule

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    prompt = data.get("text")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # 1. 调用 interact.py 中的 generate_schedule 函数
    try:
        interact.generate_schedule(prompt)
    except Exception as e:
        return jsonify({"error": f"Failed to generate schedule: {str(e)}"}), 500

    # 2. 调用 make_schedule.py 中的 make_schedule 函数
    try:
        make_schedule.make_schedule()
    except Exception as e:
        return jsonify({"error": f"Failed to create schedule image: {str(e)}"}), 500

    # 3. 返回生成的图片
    image_path = os.path.join('data', 'schedule.png')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return jsonify({"error": "Schedule image not found"}), 404

if __name__ == "__main__":
    app.run(port=7000, debug=True)
