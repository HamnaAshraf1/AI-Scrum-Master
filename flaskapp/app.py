import _thread
from projmgr.jira import *
from tokens import FLASK_SECRET_KEY
from flask import Flask, request, jsonify


# instantiate the app
flask_app = Flask(__name__)
flask_app.config.from_object(__name__)
flask_app.secret_key = FLASK_SECRET_KEY
flask_app.config['JSON_AS_ASCII'] = False

def conversation2txt(sesssion):
    text = ''
    for user in session.keys():
        text += user
        for sess in session[user]:
            text += sess['content']
        text += '\n'
    return text

@flask_app.route('/data_update', methods=['POST', 'GET'])
def update_data():
    request.get_json()
    return jsonify('OK')


@flask_app.route('/vectorization', methods=['POST', 'GET'])
def vectorization():
    request.get_json()
    return jsonify('pong!')


@flask_app.route('/embedding', methods=['POST', 'GET'])
def embedding():
    req = request.get_json()
    try:
        ollama.embeddings(model='llama3', prompt=req['prrompt'])
    except:
        return jsonify('ERROR')
    return jsonify('OK')


@flask_app.route('/summary', methods=['POST', 'GET'])
def summary():
    request.get_json()
    text = conversation2txt(session)
    text += 'summary the conversation and build a todo list for every member: '
    message = [{'role': 'user', 'content': text}]
    ollama.chat(model='llama3', messages=message)


@flask_app.route('/jira_update', methods=['POST', 'GET'])
def jira_update():
    return jsonify(get_all_issues())


def start_flask_app():
    _thread.start_new_thread(flask_app.run, ('0.0.0.0', 80))

