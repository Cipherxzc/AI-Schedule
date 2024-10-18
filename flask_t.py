from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os

import interact
import make_schedule

app = Flask(__name__)
CORS(app)  # 允许跨域请求

#路由：URL到python函数的映射。当用户访问特定URL时，
# Flask会调用对应相对应的视图函数来处理请求
@app.route('/query', methods=['POST'])
def query():#视图函数，处理并返回对应的python函数。
    #通常接受请求对象作为参数，并返回响应对象或其他内容
    
    #请求对象包含客户端发送的请求信息，包括，请求方法
    #URL，请求头，表单数据等，Flask提供request对象来访问这些信息
    data = request.json#request为请求对象
    prompt = data.get("text")

    # 调用 Python 程序并传递输入
    with open('temp_input.txt', 'w') as f:
        f.write(query_text)

    # 假设 test.py 会生成一张图片
    subprocess.run(['python', 'test.py'], check=True)

    # 假设图片文件名为 output.png
    image_path = '1.jpg'

    # 检查图片文件是否存在
    if os.path.exists(image_path):
        # 清理临时文件
        os.remove('temp_input.txt')

        # 返回图片文件
        return send_file(image_path, mimetype='image/jpg')
    else:
        # 如果图片文件不存在，返回错误信息
        return jsonify({'error': 'Image not found'}), 404

if __name__ == "__main__":
    app.run(port=7000, debug=True)