import asyncio
from pyodide.http import pyfetch
from pyodide import create_proxy
from js import document
import json

send_message = document.getElementById("send-message")
connect_user = document.getElementById("connect-user")
sender = document.getElementById("sender")
message_text = document.getElementById("message-text")
chat_window = document.getElementById("chat-window")
user_list = document.getElementById("user-list")

for_me_btn = document.getElementById("for-me-btn")
for_everyone_btn = document.getElementById("for-everyone-btn")

current_user = None
msg_id_to_delete = None

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
        "sender": f'<span class="me-1">[<b>{message["sender"]["name"]}</b>]:</span>',
        "text": f'<span>{message["text"]}</span>',
        "time": f'<span class="badge text-bg-light text-secondary ms-auto">{message["time"]}</span>',
        "remove_btn": f'<button class="btn btn-danger btn-sm ms-2" data-bs-toggle="modal" data-bs-target="#msg-delete-modal"><i class="bi bi-x-lg"></i></button>'
    }
    item.innerHTML = message_elements["sender"] + message_elements["text"] + message_elements["time"]

    if current_user["id"] == message["sender"]["id"]:
      callback = create_proxy(lambda e: delete_msg_btn_click(message["msg_id"]))

      remove_btn = document.createElement("button")
      remove_btn.className = "msg-remove-btn btn btn-danger btn-sm ms-2"
      remove_btn.setAttribute("data-bs-toggle", "modal")
      remove_btn.setAttribute("data-bs-target", "#msg-delete-modal")
      remove_btn.addEventListener("click", callback)

      remove_btn_icon = document.createElement("i")
      remove_btn_icon.className = "bi bi-x-lg"
      remove_btn.append(remove_btn_icon)

      item.append(remove_btn)

    chat_window.prepend(item)

def append_user(user):
    item = document.createElement("li")
    item.className = "list-group-item"
    item.innerHTML = user["name"]
    if current_user is not None and current_user["id"] == user["id"]:
      item.className += " active"
    user_list.append(item)

async def send_message_click(e):
    if not current_user:
        return
    await fetch(f"/send_message?sender_id={current_user['id']}&text={message_text.value}", method="GET")
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


def delete_msg_btn_click(msg_id):
    global msg_id_to_delete
    print("msg_id", msg_id)
    msg_id_to_delete = msg_id

def for_me_btn_click(e):
    return delete_message(current_user["id"])


def for_everyone_btn_click(e):
    return delete_message("everyone")


async def delete_message(target):
    print("msg_id_to_delete", msg_id_to_delete)
    if not target or not msg_id_to_delete:
        return
    await fetch(f"/delete_message?msg_id={msg_id_to_delete}&target={target}", method="GET")

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
for_me_btn.onclick = for_me_btn_click
for_everyone_btn.onclick = for_everyone_btn_click

load_all_info()