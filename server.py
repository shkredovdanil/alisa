from flask import Flask, request
import logging

import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
logging.basicConfig(
    filename='example.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.DEBUG
)

sessionStorage = {}
object = 'слон'


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    print(response)
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    global object
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {object}а!'
        res['response']['buttons'] = get_suggests(user_id, object)
        return
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        if object != 'слон':
            res['response']['text'] = f'Кролика можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
            object = 'слон'
        else:
            res['response']['text'] = f'Слона можно найти на Яндекс.Маркете!\n' \
                                      f'А теперь купи кролика'

            object = 'кролик'
            sessionStorage[user_id] = {
                'suggests': [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ]
            }
            res['response']['buttons'] = get_suggests(user_id, object)
        return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {object}а!"
    res['response']['buttons'] = get_suggests(user_id, object)


def get_suggests(user_id, object):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={object}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
