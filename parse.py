import requests

TOKEN = 'AQAAAAAjMqD7AAYckfzXl_YWK03diPOpRfNOuvI'


def homework():
    date = {'from_date': 1609525993}
    headers = {'Authorization': f'OAuth {TOKEN}'}
    response = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/', params=date, headers=headers).json()
    print(response)

homework()