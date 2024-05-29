from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import requests
import json
import time
import threading

url = "http://140.115.54.38:8150/api/chat_query"

app = Flask(__name__)

configuration = Configuration(access_token='yGbN8FQaIgzE32mBH7tPEDlnYcqngTehcmZvE8HAHXmPcP67jri/rezI7Iwalh99tM7WHAHtlTLC9t7BbGUNgGf5/lbro0y/QdaE4Uix22GPJ61jdrbZgUAExAy72dknXgoWnAKDngvlqOsnmyOW3AdB04t89/1O/w1cDnyilFU=') #YOUR_CHANNEL_ACCESS_TOKEN
handler = WebhookHandler('ceb6486da9889024c692886ecd3ab341') #YOUR_CHANNEL_SECRET

# 定义重试次数和延迟时间
max_retries = 1
retry_delay = 10  # 10 秒

# 标志变量，指示是否正在处理中
is_processing = False

@app.route("/callback", methods=['POST'])
def callback():
    # 获取 X-Line-Signature 头部的值
    signature = request.headers['X-Line-Signature']

    # 获取请求体
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 处理 webhook 主体
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global is_processing

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        if is_processing:
            line_bot_api.push_message_with_http_info(
                PushMessageRequest(
                    to=event.source.user_id,
                    messages=[TextMessage(text=f"系统正在处理您的上一个请求，请稍后再试。{query_data}")]
                )
            )
            return

        is_processing = True

        def print_wait_message(stop_event):
            while not stop_event.is_set():
                time.sleep(10)
                '''
                line_bot_api.push_message_with_http_info(
                    PushMessageRequest(
                        to=event.source.user_id,
                        messages=[TextMessage(text=f"久等了，持续搜寻中，请稍后...{query_data}")]
                    )
                )
                '''

        # 开始计时
        start_time = time.time()
        query_data = {
            "query": event.message.text
        }
        # 创建一个事件对象来控制打印线程
        stop_event = threading.Event()

        # 创建并启动打印线程
        print_thread = threading.Thread(target=print_wait_message, args=(stop_event,))
        print_thread.start()

        # 尝试发送请求并处理响应
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=query_data)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException as e:
                '''
                line_bot_api.push_message_with_http_info(
                    PushMessageRequest(
                        to=event.source.user_id,
                        messages=[TextMessage(text=f"搜索失败，尝试重试 ({attempt + 1}/{max_retries})...")]
                    )
                )
                '''
            time.sleep(retry_delay)

        # 停止打印线程
        stop_event.set()
        # 确保主线程在 print_thread 线程完成后才继续执行
        print_thread.join()

        # 检查响应状态码并解析响应内容
        messages = []
        if response and response.status_code == 200:
            # dic. type to json
            json_string=json.dumps(response.json())
            # 解析 JSON 字符串
            parsed_json = json.loads(json_string)

            # 获取特定字段的值
            response_text = parsed_json["response"]
            messages.append(TextMessage(text=response_text))
        else:
            messages.append(TextMessage(text=f"搜索失败，状态码为{response.status_code}"))
            #messages.append(TextMessage(text=f"响应内容，{response.text}"))

        # 结束计时
        end_time = time.time()
        execution_time = end_time - start_time
        #messages.append(TextMessage(text=f"搜索时间，{execution_time}秒"))

        # 依次发送所有消息
        for msg in messages:
            line_bot_api.push_message_with_http_info(
                PushMessageRequest(
                    to=event.source.user_id,
                    messages=[msg]
                )
            )
            time.sleep(3)  # 间隔3秒发送下一条消息

        # 处理完成，重置标志
        is_processing = False

if __name__ == "__main__":
    app.run()
