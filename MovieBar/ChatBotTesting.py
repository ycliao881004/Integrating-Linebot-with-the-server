import requests
import json
import time
import threading

# 定义 API 端点
url = "http://140.115.54.38:8150/api/chat_query"


# 定义要发送的查询

while True:
    input_content=input()
    query_data = {
    "query": input_content+"(Douban)",
    "line_id": "29892040="
    }
    
    # 定义重试次数和延迟时间
    max_retries = 5
    retry_delay = 10  # 10 秒

    def print_wait_message(stop_event):
        while not stop_event.is_set():
            time.sleep(1)
            print(f"久等了，持續搜尋中,請稍後...")    

    #主程式
    ## 开始计时
    start_time = time.time()

    ## 创建一个事件对象来控制打印线程
    stop_event = threading.Event()

    ## 创建并启动打印线程
    print_thread = threading.Thread(target=print_wait_message, args=(stop_event,))
    print_thread.start()

    ## 尝试发送请求并处理响应
    response = None
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=query_data)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"请求失败，尝试重试 ({attempt + 1}/{max_retries})...")
        time.sleep(retry_delay)
        
    ## 停止打印线程
    stop_event.set()
    ##确保主线程在 print_thread 线程完成后才继续执行
    print_thread.join() 

    ## 检查响应状态码并解析响应内容
    if response and response.status_code == 200:
        print("请求成功！")
        print("响应内容：")
        
        # dic. type to json
        json_string=json.dumps(response.json())
        # 解析 JSON 字符串
        parsed_json = json.loads(json_string)

        # 获取特定字段的值
        response_text = parsed_json['response']
        print(response_text)
    else:
        if response:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：")
            print(response.text)
        else:
            print("请求失败，未能获得响应。")

    ## 结束计时
    end_time = time.time()

    ## 计算执行时间
    execution_time = end_time - start_time

    ## 打印执行时间
    print(f"程序执行时间: {execution_time} 秒")


