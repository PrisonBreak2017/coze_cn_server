import os
import json
import base64
import tempfile
import requests
import logging
from flask import Flask, request, jsonify

"""
sudo systemctl stop cozecnapi.service
sudo systemctl daemon-reload
sudo systemctl start cozecnapi.service
sudo systemctl enable cozecnapi.service
sudo systemctl status cozecnapi.service

sudo systemctl stop cozecnapi.service && sudo systemctl daemon-reload && sudo systemctl start cozecnapi.service && sudo systemctl enable cozecnapi.service && sudo systemctl status cozecnapi.service
"""

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

def split_text(text, max_length):
    """将文本分割为不超过max_length字符的片段,确保在单词边界处分割."""
    words = text.split()
    split_texts = []
    current_text = ""

    for word in words:
        if len(current_text) + len(word) + 1 > max_length:  # +1 for space
            split_texts.append(current_text.strip())
            current_text = word + " "
        else:
            current_text += word + " "

    if current_text:
        split_texts.append(current_text.strip())

    return split_texts

def upload_to_knowledge_pro(action, title, summary, content, dataset_id, file_name, personal_access_token):
    """上传内容到知识库,确保分割文本不超过1500个字符."""
    logging.info("开始分割文本...")
    split_texts = split_text(content, 1500)
    
    document_infos = []
    
    for text in split_texts:
        # 在每个分割文本前添加summary
        text_with_summary = f"{summary}\n{action}\n{text}"
        
        # 创建临时文件
        logging.info("创建临时文件...")
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
            temp_file.write(text_with_summary)
            temp_file_path = temp_file.name
            logging.debug(f"临时文件路径: {temp_file_path}")

        try:
            # 读取文件并编码为Base64
            logging.info("读取临时文件并编码为Base64...")
            with open(temp_file_path, 'rb') as file:
                file_content = file.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
                logging.debug("文件成功编码为Base64.")

            # 准备请求数据
            url = "https://api.coze.cn/open_api/knowledge/document/create"
            headers = {
                "Authorization": f"Bearer {personal_access_token}",
                "Content-Type": "application/json",
                "Agw-Js-Conv": "str"
            }
            
            payload = {
                "dataset_id": dataset_id,
                "document_bases": [
                    {
                        "name": file_name,
                        "source_info": {
                            "file_base64": file_base64,
                            "file_type": "txt"
                        }
                    }
                ],
                "chunk_strategy": {
                    "separator": "###",
                    "max_tokens": 2000,
                    "remove_extra_spaces": False,
                    "remove_urls_emails": False,
                    "chunk_type": 1
                }
            }
            logging.info("发送请求到API...")
            
            # 发送请求
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # 处理响应
            if response.status_code == 200:
                result = response.json()
                logging.info("接收到响应,处理结果...")
                if result['code'] == 0:
                    logging.info("文件上传成功.")
                    document_infos.extend(result['document_infos'])
                else:
                    logging.error(f"上传失败: {result['msg']}")
            else:
                logging.error(f"请求失败: {response.status_code}")

        finally:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.info(f"临时文件已删除: {temp_file_path}")

    return document_infos

@app.route('/upload_to_knowledge', methods=['POST'])
def api_upload_to_knowledge():
    data = request.json
    content = data.get('content')
    file_name = data.get('file_name', 'coze_knowledge.txt')
    action = data.get('action')
    title = data.get('title')
    summary = data.get('summary')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    # 从环境变量中读取API密钥和知识ID
    coze_knowledge_id = os.getenv('COZE_KNOWLEDGE_ID')
    coze_api_token = os.getenv('COZE_API_TOKEN')

    if not coze_knowledge_id or not coze_api_token:
        return jsonify({"error": "Missing COZE_KNOWLEDGE_ID or COZE_API_TOKEN in .env file"}), 500

    result = upload_to_knowledge_pro(action, title, summary, content, coze_knowledge_id, file_name, coze_api_token)

    if result:
        return jsonify({"message": "Upload successful", "document_infos": result})
    else:
        return jsonify({"error": "Upload failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)