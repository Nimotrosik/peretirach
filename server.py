# This is a chat API built with Flask that allows you to interact with chat using requests.
# It allows you to create the chats, send and receive the messages.
# All chats are temporarily saved in a json file on the server.

# Это API чата, созданный с помощью Flask, который позволяет взаимодействовать с чатом с помощью запросов.
# Он позволяет создавать чаты, отправлять и получать сообщения.
# Все чаты временно сохраняются в json-файле на сервере.
from flask import Flask, render_template, send_file, request
from datetime import datetime
from threading import Thread
import json
import uuid
import os

chats_file = os.path.join('chats.json')
if not os.path.exists(chats_file):
    with open(chats_file, 'w', encoding='utf-8') as database_json:
        json.dump({"": [
            [
                "",
                ""
            ]
        ]
        }, database_json, indent=4)

with open(chats_file, 'r', encoding='utf-8') as database_json:
    chats = json.load(database_json)

app = Flask('')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat')
def chat():
    token = request.args.get('token', 'None')
    if token in chats.keys():
        msg = request.args.get('msg', 'None')
        chats[token].append([msg, str(uuid.uuid4())])
        with open(chats_file, 'w', encoding='utf-8') as databasejson:
            json.dump(chats, databasejson, indent=4, ensure_ascii=False)
        return 'Сообщение отправлено'


@app.route('/take')
def take():
    token = request.args.get('token', 'None')
    if token in chats.keys():
        return {chats[token][-1][1]: chats[token][-1][0]}


@app.route('/take_all')
def take_all():
    token = request.args.get('token', 'None')
    if token in chats.keys():
        msges = []
        for i in chats[token]:
            msges.append(i[0])
        return msges[:-1]


@app.route('/take_name')
def take_name():
    try:
        return send_file('peretirach.svg', mimetype='image/svg+xml')
    except Exception as e:
        return str(e)


@app.route('/take_ico')
def take_ico():
    try:
        return send_file('ico.ico', mimetype='image/ico+xml')
    except Exception as e:
        return str(e)


@app.route('/create_chat')
def create_chat():
    token = request.args.get('token', 'None')
    if token != 'None':
        if token not in chats.keys():
            time = datetime.utcnow().strftime("%H:%M")
            chats[token] = [[f'[{time}] Чат создан', str(uuid.uuid4())]]
            with open(chats_file, 'w', encoding='utf-8') as databasejson:
                json.dump(chats, databasejson, indent=4, ensure_ascii=False)
            return 'Чат создан'
        else:
            return 'Выбери другой токен'


@app.route('/delete_chat')
def delete_chat():
    token = request.args.get('token', 'None')
    if token != 'None':
        if token in chats.keys():
            del chats[token]
            with open(chats_file, 'w', encoding='utf-8') as databasejson:
                json.dump(chats, databasejson, indent=4, ensure_ascii=False)
            return 'Чат удален'
        else:
            return 'Чат не существует'


def run():
    app.run(host='0.0.0.0', port=80)


def keep_alive():
    t = Thread(target=run)
    t.start()


if __name__ == '__main__':
    keep_alive()
