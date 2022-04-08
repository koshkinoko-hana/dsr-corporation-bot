from datetime import datetime
from pytz import timezone

from db.init import query, insert
import db.queries as q

ACTIVITY = {
    'ACTIVITY_ID': 0,
    'ACTIVITY_NAME': 'Students quiz 10.04.2022',
    'DESCRIPTION': 'Quiz for students on Careeer Date 10.04.2022',
    'FOR_USER_TYPE': 'STUDENT',
    'ACTIVITY_TYPE': 'QUIZ',
    'START_DATE': datetime(2022, 4, 7, 19, 40).astimezone(timezone('Europe/Volgograd')), #datetime(2022, 4, 9, 12),
    'END_DATE': datetime(2022, 4, 7, 18).astimezone(timezone('Europe/Volgograd')) #datetime(2022, 4, 9, 14, 10)
}

current_question = {
    'index': -1,
    'time_max': 600000,
    'winner_exists': False
}

ACTIVITY_ITEMS = [
    {
        'name': 'Вопрос 1',
        'description': '1.jpg',
        'answers': ['scala', 'скала'],
        'time_start': datetime(2022, 4, 7, 16, 0),#datetime(2022, 4, 9, 12),
        'multiplier': 1,
        'id': 2
    },
    {
        'name': 'Вопрос 2',
        'description': '2.png',
        'answers': ['swift', 'свифт'],
        'time_start': datetime(2022, 4, 7, 16, 1),#datetime(2022, 4, 9, 12, 10),
        'multiplier': 1,
        'id': 3
    },
    {
        'name': 'Вопрос 3',
        'description': '3_hard.png',
        'answers': ['эликсир', 'elixir'],
        'time_start': datetime(2022, 4, 7, 16, 2),#datetime(2022, 4, 9, 12, 20),
        'multiplier': 2,
        'id': 4
    },
    {
        'name': 'Вопрос 4',
        'description': '4.png',
        'answers': ['ада', 'ada'],
        'time_start': datetime(2022, 4, 7, 16, 3),#datetime(2022, 4, 9, 12, 30),
        'multiplier': 1,
        'id': 5
    },
    {
        'name': 'Вопрос 5',
        'description': '5.png',
        'answers': ['c++', 'с++'],
        'time_start': datetime(2022, 4, 7, 16, 4),#datetime(2022, 4, 9, 12, 40),
        'multiplier': 1,
        'id': 6
    },
    {
        'name': 'Вопрос 6',
        'description': '6_hard.png',
        'answers': ['алгол', 'algol'],
        'time_start': datetime(2022, 4, 7, 16, 5),#datetime(2022, 4, 9, 12, 50),
        'multiplier': 2,
        'id': 7
    },
    {
        'name': 'Вопрос 7',
        'description': '7.png',
        'answers': ['rust', 'раст'],
        'time_start': datetime(2022, 4, 7, 16, 6),#datetime(2022, 4, 9, 13),
        'multiplier': 1,
        'id': 8
    },
    {
        'name': 'Вопрос 8',
        'description': '8.jpg',
        'answers': ['dart', 'дарт'],
        'time_start': datetime(2022, 4, 7, 16, 7),#datetime(2022, 4, 9, 13, 10),
        'multiplier': 1,
        'id': 9
    },
    {
        'name': 'Вопрос 9',
        'description': '9_hard.png',
        'answers': ['haskell', 'хаскель', 'хаскел', 'хаскелл', 'хаскэл'],
        'time_start': datetime(2022, 4, 7, 16, 8),#datetime(2022, 4, 9, 13, 20),
        'multiplier': 2,
        'id': 10
    },
    {
        'name': 'Вопрос 10',
        'description': '10.jpg',
        'answers': ['фортран', 'fortran'],
        'time_start': datetime(2022, 4, 7, 16, 9),#datetime(2022, 4, 9, 13, 30),
        'multiplier': 1,
        'id': 11
    },
    {
        'name': 'Вопрос 11',
        'description': '11.png',
        'answers': ['coffeescript', 'javascript', 'джаваскрипт', 'кофескрипт'],
        'time_start': datetime(2022, 4, 7, 16, 10),#datetime(2022, 4, 9, 13, 40),
        'multiplier': 2,
        'id': 12
    },
    {
        'name': 'Вопрос 12',
        'description': '12_hard.jpg',
        'answers': ['pascal', 'паскаль'],
        'time_start': datetime(2022, 4, 7, 16, 11),#datetime(2022, 4, 9, 13, 50),
        'multiplier': 2,
        'id': 13
    },
    {
        'name': 'Вопрос 13',
        'description': '13_very_hard.jpg',
        'answers': ['Matlab', 'Матлаб'],
        'time_start': datetime(2022, 4, 7, 16, 12),#datetime(2022, 4, 9, 14),
        'multiplier': 4,
        'id': 14
    }
]

def init_quiz():
    activity = query(q.GET_ACTIVITY_BY_NAME, [ACTIVITY.get('ACTIVITY_NAME')], True)
    if activity:
        ACTIVITY.update({'ACTIVITY_ID': activity[0]})
    if not activity:
        id = insert(q.INSERT_ACTIVITY, [ACTIVITY.get('ACTIVITY_NAME'), ACTIVITY.get('DESCRIPTION'),
                                        ACTIVITY.get('ACTIVITY_TYPE'), ACTIVITY.get('FOR_USER_TYPE'),
                                        datetime.now(), datetime.now(), ACTIVITY.get('START_DATE'),
                                        ACTIVITY.get('END_DATE')])

        ACTIVITY.update({'ACTIVITY_ID': id})
        for i in range(len(ACTIVITY_ITEMS)):
            id = insert(q.INSERT_ACTIVITY_ITEM, [ACTIVITY.get('ACTIVITY_ID'),
                                                 ACTIVITY_ITEMS[i].get('name'), ACTIVITY_ITEMS[i].get('description'),
                                                 datetime.now(), datetime.now()])
            ACTIVITY_ITEMS[i].update({'id': id})


def increase_current_question():
    current_question['index'] += 1
