"""
基于 Flask 的 PDF 压缩 Web 服务
启动后可通过 HTTP 上传 PDF 并下载压缩版本
"""

import os
import tempfile
from flask import Flask, request, send_file, jsonify
from compress import compress_pdf

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/compress', methods=['POST'])
def compress():
    """接收上传的 PDF，返回压缩后的 PDF"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': '只允许 PDF 文件'}), 400
    
    # 保存临时文件
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    
    # 压缩
    output_path = compress_pdf(input_path, garbage=4, deflate=True)
    
    # 返回压缩文件
    return send_file(output_path, as_attachment=True, download_name=f"compressed_{file.filename}")

@app.route('/')
def index():
    return """
    <h2>PDF 压缩服务</h2>
    <form method="post" action="/compress" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf">
        <input type="submit" value="上传并压缩">
    </form>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)