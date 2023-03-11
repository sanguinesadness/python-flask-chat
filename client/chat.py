import asyncio
from pyodide.http import pyfetch
from js import document
import json

last_seen_time = ""
# Находим элементы интерфейса по их ID
send_message = document.getElementById("send-message")
connect_user = document.getElementById("connect-user")
sender = document.getElementById("sender")
message_text = document.getElementById("message-text")
chat_window = document.getElementById("chat-window")
user_list = document.getElementById("user-list")

current_user = None

async def fetch(url, method, payload=None):
    kwargs = { "method": method }
    if method == "POST":
        kwargs["body"] = json.dumps(payload)
        kwargs["headers"] = {"Content-Type": "application/json"}
    return await pyfetch(url, **kwargs)

def set_timeout(delay, callback):
    def sync():
        asyncio.get_running_loop().run_until_complete(callback())
    asyncio.get_running_loop().call_later(delay, sync)


def append_message(message):
    item = document.createElement("li")
    item.className = "list-group-item list-group-item--chat"

    message_elements = {
        "sender": f'<span class="me-1">[<b>{message["sender"]}</b>]:</span>',
        "text": f'<span>{message["text"]}</span>',
        "time": f'<span class="badge text-bg-light text-secondary ms-auto">{message["time"]}</span>'
    }
    item.innerHTML = message_elements["sender"] + message_elements["text"] + message_elements["time"]
    chat_window.prepend(item)

def append_user(user):
    item = document.createElement("li")
    item.className = "list-group-item"
    item.innerHTML = user["name"]
    if current_user is not None and current_user["id"] == user["id"]:
      item.className += " active"
    user_list.append(item)

# Вызывается при клике на send_message
async def send_message_click(e):
    # Отправляем запрос
    await fetch(f"/send_message?sender={sender.value}&text={message_text.value}", method="GET")
    # Очищаем поле
    message_text.value = ""

async def connect_user_click(e):
    result = await fetch(f"/connect_user?name={sender.value}", method="GET")
    data = await result.json()
    global current_user
    current_user = data["user"]
    sender.disabled = True
    connect_user.disabled = True
    message_text.disabled = False
    send_message.disabled = False

# Загружает новые сообщения с сервера и отображает их
async def load_fresh_messages():
    sender_id = ""
    if current_user is not None:
        sender_id = current_user["id"]
    result = await fetch(f"/get_messages?sender_id={sender_id}", method="GET")
    chat_window.innerHTML = ""
    data = await result.json()
    all_messages = data["messages"]
    for msg in all_messages:
        append_message(msg)
    set_timeout(1, load_fresh_messages)

async def load_users():
    result = await fetch(f"/get_users", method="GET")
    data = await result.json()
    users = data["users"]
    if len(users) > 0:
      user_list.innerHTML = ""
      for user in users:
        append_user(user)
    set_timeout(2, load_users)

async def load_all_info():
    await load_fresh_messages()
    await load_users()

send_message.onclick = send_message_click
connect_user.onclick = connect_user_click

load_all_info()