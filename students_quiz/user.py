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

    ids = query(q.GET_USERS_BY_ACTIVITY, [activity_id])
    if current_question.get('index') == len(ACTIVITY_ITEMS):
        return None, [x[0] for x in ids]

    current = ACTIVITY_ITEMS[current_question.get('index')]
    return current, [x[0] for x in ids]


def results():
    rating = query(q.GET_BEST_USERS_BY_RESULTS, [])
    max_points = round(rating[0][0], 3)
    i = -1
    for item in rating:
        i += 1
        if round(item[0], 3) < max_points:
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
        return 'К сожалению, ответ нельзя изменить. Жди следующего вопроса!', False

    answer = ans.strip().lower()
    if answer in current.get('answers'):
        spent = time - current.get('time_start').timestamp()
        if spent < 60000:
            bonus = 1.5
        elif spent < 60000 * 2:
            bonus = 1.2
        elif spent < 60000 * 5:
            bonus = 0.8
        elif spent < 60000 * 7:
            bonus = 0.5
        else:
            bonus = 0.2
        points = (10.0 - (spent * 10.0 / current_question.get('time_max'))) * current.get('multiplier') * bonus
    else:
        points = 0

    insert(q.INSERT_USER_ACTIVITY_ITEM, [user[0], current.get('id'), answer, points])

    if current.get('name') == 'Вопрос 13':
        if str(tlg_user.id) not in current_question.get('pretenders'):
            return 'К сожалению, ответ нельзя изменить. Жди следующего вопроса!', False
        if points:
            current_question.update({'winner_exists': True})
            return 'Поздравляем с победой! ' + get_my_result(tlg_user.id), True
        else:
            return 'Ответ неверный! Попробуй ещё раз. В этот раз можно отвечать более одного раза.', False

    if current.get('name') == 'Вопрос 12':
        return 'Ответ принят! Это был последний вопрос. Для получения списка лучших отправь /rating.', False
    return 'Ответ принят! Скоро будет следующий вопрос.', False


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


def get_my_result(tlg_id):
    res = 'Очки за ответы:\n'
    answers = query(q.GET_USER_RESULTS, [tlg_id])
    i = 0
    total = 0
    for item in ACTIVITY_ITEMS:
        if item.get('name') == 'Вопрос 13':
            break

        if i < len(answers) and item.get('id') == answers[i][0]:
            res += '{0}: \nВаш ответ: {1}. \nПравильный ответ: {2}. \n{3} очков\n\n'.format(
                item.get('name'),
                answers[i][1],
                ", ".join(item.get('answers')),
                str(round(answers[i][2], 3))
            )
            total += answers[i][2]
            i += 1
        else:
            res += '{0}: \nОтвет не дан. \nПравильный ответ: {1}. \n0 очков\n\n'.format(
                item.get('name'),
                ", ".join(item.get('answers')),
            )
    res += 'Всего набрано {0} очков.'.format(str(round(total, 3)))
    return res
