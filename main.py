from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__, static_folder="./client", template_folder="./client")  # Настройки приложения

msg_id = 1
user_id = 1
all_messages = []
connected_users = []

@app.route("/chat")
def chat_page():
    return render_template("chat.html")


def add_message(sender, text):
    global msg_id
    new_message = {
        "sender": sender,
        "text": text,
        "time": datetime.now().strftime("%H:%M"),
        "msg_id": msg_id
    }
    msg_id += 1
    all_messages.append(new_message)


def add_user(name):
    global user_id
    new_user = {
        "id": user_id,
        "name": name
    }
    user_id += 1
    connected_users.append(new_user)
    return new_user


@app.route("/get_messages")
def get_messages():
    return {"messages": all_messages}


@app.route("/get_users")
def get_users():
    return { "users": connected_users }


@app.route("/send_message")
def send_message():
    sender = request.args["sender"]
    text = request.args["text"]
    add_message(sender, text)
    return { "result": True }


@app.route("/connect_user")
def connect_user():
    name = request.args["name"]
    return { "user": add_user(name) }


@app.route("/")
def hello_page():
    return "New text goes here"


app.run()
