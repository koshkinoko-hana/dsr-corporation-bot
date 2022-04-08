import datetime
from typing import Optional

from telegram import User

from db.init import query, insert
import db.queries as q
from students_quiz.init import ACTIVITY, ACTIVITY_ITEMS, increase_current_question, current_question


def check_or_create_user(tlg_user: Optional[User]):
    exists = True
    user = query(q.GET_USER_BY_TELEGRAM, [tlg_user.id], True)
    if not user:
        tuple = q.user_insert_tuple(tlg_user, 'STUDENT')
        id = insert(q.INSERT_USER, tuple)
        exists = False
    else:
        id = user[0]
    user_activity = query(q.GET_USER_ACTIVITY, [id, ACTIVITY.get('ACTIVITY_ID')], True)
    if user_activity and user_activity[5]:
        return 'Привет! Благодарим за участие в бета-тестировании бота! ' \
               'К сожалению, ты не сможешь принять участие в квизе. Твои ответы не будут ' \
               'учитываться при составлении рейтинга и определении победителя. Встретимся в офисе DSR :)'
    if not user_activity:
        insert(q.ASSIGN_USER_ACTIVITY, [id, ACTIVITY.get('ACTIVITY_ID'), datetime.datetime.now(), ''])
        exists = False
    return exists


def make_question():
    activity_id = ACTIVITY.get('ACTIVITY_ID')
    increase_current_question()
    current = ACTIVITY_ITEMS[current_question.get('index')]
    if not current:
        return
    ids = query(q.GET_USERS_BY_ACTIVITY, [activity_id])
    return current, [x[0] for x in ids]


def results():
    rating = query(q.GET_BEST_USERS_BY_RESULTS, [])
    max_points = rating[0][0]
    i = 0
    for item in rating:
        i += 1
        if item[0] < max_points:
            break
    if i < 2:
        message = 'Поздравляем! Ты набрал {0} очков и занял первое место в квизе. ' \
                  'Обратись к организаторам для получения приза.'.format(round(max_points, 3))
        return rating[0][4], message
    else:
        return [v[4] for j, v in enumerate(rating) if j < i], False



def user_answer(tlg_user: Optional[User], ans):
    time = datetime.datetime.now().timestamp()
    current = ACTIVITY_ITEMS[current_question.get('index')]
    user = query(q.GET_USER_BY_TELEGRAM, [tlg_user.id], True)
    answer_exists = query(q.GET_ANSWER, [user[0], current.get('id')], True)
    if answer_exists:
        return 'К сожалению, ответ нельзя изменить. Жди следующего вопроса!'
    answer = ans.strip().lower()
    if answer in current.get('answers'):
        spent = time - current.get('time_start').timestamp()
        if spent < 6000:
            bonus = 1.5
        elif spent < 6000 * 2:
            bonus = 1.2
        elif spent < 6000 * 5:
            bonus = 0.8
        elif spent < 6000 * 7:
            bonus = 0.5
        else:
            bonus = 0.2
        points = (1.0 - spent * 1.0 / current_question.get('time_max')) * current.get('multiplier') * bonus
    else:
        points = 0
    insert(q.INSERT_USER_ACTIVITY_ITEM, [user[0], current.get('id'), answer, round(points, 3)])
    return 'Ответ принят! Скоро будет следующий вопрос.'


def get_rating():
    res = 'Топ 10 участников:\n'
    rating = query(q.GET_TOP_USERS_BY_RESULTS, [])
    for item in rating:
        res += '{0} {1} {2}: {3} очков\n'.format(
            item[1] or '',
            item[2] or '',
            '(@'+item[3] + ')' if item[3] else '',
            str(round(item[0], 3))
        )
    return res
