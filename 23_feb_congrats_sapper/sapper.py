#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import copy


sapper_field = '''π΅π΅π΅π΅π΅
π΅π΅π΅π΅π΅
π΅π΅π΅π΅π΅
π΅π΅π΅π΅π΅
π΅π΅π΅π΅π΅'''

row_names = ['a', 'b', 'c', 'd', 'e']

empty_answer = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]


def generate():
    ans_list = random.sample(range(25), 10)
    res = copy.deepcopy(empty_answer)
    for i in ans_list:
        res[i // 5][i % 5] = 1
    return res


def init_sapper(user):
    new_game = generate()
    if 'game' in user:
        game = user['game']
        game['current'] = new_game
        game['touched_count'] = 0
        game['answer'] = copy.deepcopy(empty_answer)
    else:
        user.update({
            'game': {
                'current': new_game,
                'touched_count': 0,
                'total': 0,
                'answer': copy.deepcopy(empty_answer)
            }
        })
    field = '<CODE>_ 1 2 3 4 5\n'
    rows = sapper_field.split('\n')
    for i in range(len(rows)):
        field += row_names[i] + rows[i] + '\n'
    field += '</CODE>'
    return field


def reformat_answer(game, ans):
    answer_list = ans.split(',')
    dif = game['touched_count'] + len(answer_list) - 15
    if dif > 0:
        game['touched_count'] = 15
    else:
        game['touched_count'] += len(answer_list)

    for a in range(len(answer_list) - (dif if dif > 0 else 0)):
        item = answer_list[a].strip().lower()
        i = row_names.index(item[0])
        j = int(item[1]) - 1
        game['answer'][i][j] = 1

        if game['current'][i][j] == 1:
            game['total'] += 1


def answer(user, ans):
    if 'game' not in user or user['game']['touched_count'] == 15:
        return 'Π§ΡΠΎΠ±Ρ Π½Π°ΡΠ°ΡΡ Π½ΠΎΠ²ΡΡ ΠΈΠ³ΡΡ, Π²Π²Π΅Π΄ΠΈ /game .'
    res_field = '<CODE>_ 1 2 3 4 5\n'
    game = user['game']

    reformat_answer(game, ans)
    final = game['touched_count'] == 15
    for i in range(5):
        res_field += row_names[i]
        for j in range(5):
            if game['answer'][i][j] and game['current'][i][j]:
                res_field += 'π’'
            elif game['answer'][i][j]:
                res_field += 'βͺοΈ'
            elif final and game['current'][i][j]:
                res_field += 'π΄'
            else:
                res_field += 'π΅'
        res_field += '\n'
    res_field += '</CODE>'
    before = 'Π₯ΠΎΠ΄Ρ Π·Π°ΠΊΠΎΠ½ΡΠΈΠ»ΠΈΡΡ! Π€ΠΈΠ½Π°Π»ΡΠ½ΠΎΠ΅ ΠΏΠΎΠ»Π΅:\n' if final \
        else 'ΠΡΡΠ°Π»ΠΎΡΡ {0} ΡΠΎΠ΄ΠΎΠ²:\n'.format(15 - game['touched_count'])
    after = 'Π£ ΡΠ΅Π±Ρ {0} ΠΎΡΠΊΠΎΠ².\n'.format(game['total'])
    if game['touched_count'] == 15:
        after += 'Π§ΡΠΎΠ±Ρ Π½Π°ΡΠ°ΡΡ Π½ΠΎΠ²ΡΡ ΠΈΠ³ΡΡ, Π²Π²Π΅Π΄ΠΈ /game. ' \
                 'Π§ΡΠΎΠ±Ρ ΠΎΠ±Π½ΡΠ»ΠΈΡΡ Π΄ΠΎΡΡΠΈΠΆΠ΅Π½ΠΈΡ, Π²Π²Π΅Π΄ΠΈ /clear. ΠΡΠ°Π²ΠΈΠ»Π° ΠΈΠ³ΡΡ - /rules. ' \
                 'ΠΠΎΠ»ΡΡΠΈΡΡ ΠΏΠΎΠ·Π΄ΡΠ°Π²Π»Π΅Π½ΠΈΠ΅ - /congratulation. ΠΡΠ΅ ΠΊΠΎΠΌΠ°Π½Π΄Ρ - /commands.'
    return before + res_field + after
