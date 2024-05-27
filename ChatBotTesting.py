import requests
import json
import time

# 定义 API 端点
url = "http://140.115.54.38:8150/api/chat_query"

# 定义要发送的查询
query_data = {
    "query": "推薦2024火熱電影"
}

# 定义重试次数和延迟时间
max_retries = 5
retry_delay = 10  # 10 秒

for attempt in range(max_retries):
    response = requests.post(url, json=query_data)

    if response.status_code == 200:
        print("请求成功！")
        print("响应内容：")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        break
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：")
        print(response.text)

        if response.status_code == 500 and "You are sending too many messages. Try again later." in response.text:
            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print("已达到最大重试次数，停止重试。")
        else:
            break
