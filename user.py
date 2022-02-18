import json
import random

from sapper import init_sapper, answer

users_list = {}

greetings_file = open('greetings_list.json')
greetings = json.load(greetings_file)


def fill_users():
    users_file = open('users_list.json')
    global users_list
    users_list = json.load(users_file)
    print(users_list)
    users_file.close()


def check_or_create_user(user):
    print(user)
    if str(user.id) in users_list:
        return True
    else:
        users_list.update({
            str(user.id): {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'greetings_count': 0,
                'game_greeting': False
            }
        })

        with open('users_list.json', 'w') as f:
            json.dump(users_list, f)
            f.close()
        return False


def game_not_started(user_id):
    user = users_list[str(user_id)]
    print(user)
    if 'game' not in user or user['game']['touched_count'] == 15:
        return 'Чтобы начать новую игру, введи /game .'


def start_game(u):
    check_or_create_user(u)
    user = users_list.get(str(u.id))
    res = init_sapper(user)
    with open('users_list.json', 'w') as f:
        json.dump(users_list, f)
        f.close()
    return res


def form_message(user_id):
    user = users_list.get(str(user_id))
    count = user['greetings_count']
    if count < 3:
        user['greetings_count'] += 1
        with open('users_list.json', 'w') as f:
            json.dump(users_list, f)
            f.close()
        greeting_index = random.randint(0, len(greetings)-1)
        message = '{0} {1}!\n'.format(user['first_name'], user['last_name'])
        message += greetings[greeting_index]['message'] + '\n'
        message += greetings[greeting_index]['author']
        return message
    else:
        return 'Желаем, желаем, желаем... Одной фразы не хватит, ' \
               'чтобы выразить наши чувства, но мы попробуем:\nМы вас любим!'


def user_answer(user, ans):
    check_or_create_user(user)
    no_game = game_not_started(str(user.id))
    if not no_game:
        msg = answer(users_list.get(str(user.id)), ans)
        with open('users_list.json', 'w') as f:
            json.dump(users_list, f)
            f.close()
        return msg
    else:
        return no_game


def clear_total(user_id):
    user = users_list.get(str(user_id))
    if 'game' in user:
        user['game']['total'] = 0
        with open('users_list.json', 'w') as f:
            json.dump(users_list, f)
            f.close()


def get_rating():
    res = 'Топ 10 пользователей:\n'
    i = 0
    played_list = dict((k, v) for(k, v) in users_list.items() if 'game' in v)
    rating = sorted(played_list.values(), key=lambda user: user['game']['total'], reverse=True)
    for item in rating:
        res += '{0} {1} (@{2}): {3} очков\n'.format(
            item['first_name'],
            item['last_name'],
            item['username'],
            str(item['game']['total'])
        )
        i += 1
        if i == 10:
            return res
    return res


def ready_for_congratulations(user_id):
    user = users_list.get(str(user_id))
    if 'game' in user:
        if user['game']['total'] > 9 and not user['game_greeting']:
            user['game_greeting'] = True
            with open('users_list.json', 'w') as f:
                json.dump(users_list, f)
                f.close()
            return True
    return False
