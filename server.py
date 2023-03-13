from flask import Flask, request
import logging
import random

import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
logging.basicConfig(
    filename='example.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)

sessionStorage = {}
cities = {
    'москва': ['937455/7e163be94522dffaf4e8',
               '937455/261fa113b58c38c866dd'],
    'нью-йорк': ['1533899/c12ecb8ef146b91a0cf1',
                 '1030494/ef21d5236c4ead6e79f6'],
    'париж': ["1030494/62d4615d1365921382f9",
              '1533899/2b2ee27b5a8458675edd']
}


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
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    res['response']['buttons'] = button_help(req, res, user_id)
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        sessionStorage[user_id] = {
            'first_name': None
        }
        return
    if req['session']['command'] == 'Справка':
        res['response']['text'] = f'Игра угадай город\n' \
                                  f'Вы называете город. Если я его знаю, отправляю вам его фотографию.\n'
    elif sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Какой город хочешь увидеть?'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = random.choice(cities[city])
            res['response']['text'] = 'Я угадал!'
        else:
            res['response']['text'] = \
                'Первый раз слышу об этом городе. Попробуй еще разок!'


def button_help(req, res, user_id):
    session = sessionStorage[user_id]
    suggests = [{'title': 'Справка', 'hide': True}]
    return suggests


def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
