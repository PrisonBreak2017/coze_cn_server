import requests
import json

# 替换为你的服务器的公网IP地址和端口
SERVER_URL = "http://47.97.75.154:5000/upload_to_knowledge"

# 替换为你在服务器端设置的API密钥
API_KEY = "YOUR_API_KEY"

# 测试数据
test_data = {
    "content": "这是一个测试内容。它将被上传到知识库中。",
    "file_name": "test_knowledge.txt",
    "action": "添加新知识",
    "title": "测试知识条目",
    "summary": "这是一个用于测试的知识条目摘要。"
}

# 设置请求头，包含API密钥
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_upload_to_knowledge():
    try:
        # 发送POST请求
        response = requests.post(SERVER_URL, json=test_data, headers=headers)
        
        # 检查响应状态码
        if response.status_code == 200:
            print("上传成功！")
            print("响应内容：", json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            print(f"上传失败。状态码：{response.status_code}")
            print("错误信息：", response.text)
    
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    test_upload_to_knowledge()