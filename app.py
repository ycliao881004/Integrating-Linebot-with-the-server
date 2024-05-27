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
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import requests
import json

url = "http://140.115.54.38:8150/api/chat_query"


app = Flask(__name__)

configuration = Configuration(access_token='YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        query_data = {
            "query": event.message.text
        }
        response = requests.post(url, json=query_data)
        if response.status_code == 200:
            print("请求成功！")
            print("响应内容：")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：")
            print(response.text)
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=json.dumps(response.json(), indent=4, ensure_ascii=False))] #回覆訊息 修改text
            )
        )

if __name__ == "__main__":
    app.run()
    
