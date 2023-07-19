import requests
import json

api_url = 'http://127.0.0.1:9090/proxies'
headers = {'Content-Type': 'application/json'}
data = {'name': 'New Node Name'}

# 指定代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

response = requests.put(api_url, headers=headers, proxies=proxies)

if response.status_code == 200:
    print('节点修改成功')
else:
    print('节点修改失败:', response.text)