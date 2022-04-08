import datetime
from typing import Optional

from telegram import User

GET_USERS = 'SELECT * from users'

GET_USER = 'SELECT * from users where id=%s'

GET_USER_BY_TELEGRAM = 'SELECT * from users where telegram_id=%s'

GET_ANSWER = 'SELECT uai.id answer from user_activity_items uai where user_id=%s and item_id=%s'

GET_USERS_RATING_10 = 'SELECT u.telegram_username, u.first_name, u.last_name, SUM(uai.points) total_points ' \
                      'from users u INNER JOIN user_activity_items uai on u.id = uai.user_id order by total_points ' \
                      'DESC limit 10'

INSERT_USER = 'INSERT into users (first_name, last_name, telegram_id, telegram_username, type, created_at, ' \
              'updated_at)  VALUE (%s, %s, %s, %s, %s, %s, %s)'


def user_insert_tuple(tlg_user: Optional[User], type: str):
    date = datetime.datetime.now()
    return [tlg_user.first_name, tlg_user.last_name, tlg_user.id,
            tlg_user.username, type, date, date]


GET_ACTIVITY_BY_NAME = 'SELECT * from activities where name = %s'

INSERT_ACTIVITY = 'INSERT into activities (name, description, activity_type, for_user_type, created_at, ' \
                  'updated_at, start_date, end_date) ' \
                  'VALUE (%s, %s, %s, %s, %s, %s, %s, %s)'

INSERT_ACTIVITY_ITEM = 'INSERT into activity_items (activity_id, name, description, created_at, updated_at)' \
                       ' VALUE (%s, %s, %s, %s, %s)'

ASSIGN_USER_ACTIVITY = 'INSERT into user_activities (user_id, activity_id, assigned_date, assigned_info) ' \
                       'VALUE (%s, %s, %s, %s)'

GET_USER_ACTIVITY = 'SELECT * from user_activities where user_id = %s and activity_id = %s'

GET_USERS_BY_ACTIVITY = "SELECT u.telegram_id id from users u inner join user_activities ua " \
                        "on u.id = ua.user_id where ua.activity_id = %s and (blocked is null or blocked = '0')"

INSERT_USER_ACTIVITY_ITEM = 'INSERT into user_activity_items (user_id, item_id, response, points) ' \
                            'VALUE (%s, %s, %s, %s)'

GET_TOP_USERS_BY_RESULTS = 'SELECT SUM(uai.points) total, u.first_name fn, u.last_name ln, ' \
                           'u.telegram_username un ' \
                           'from users u inner join user_activity_items uai on u.id = uai.user_id ' \
                           'inner join user_activities ua on u.id = ua.user_id ' \
                           'where (ua.blocked is null or ua.blocked = 0) ' \
                           'group by u.id order by total desc limit 10'

GET_BEST_USERS_BY_RESULTS = 'SELECT SUM(uai.points) total, u.first_name fn, u.last_name ln, ' \
                            'u.telegram_username un, u.telegram_id tid ' \
                            'from users u inner join user_activity_items uai on u.id = uai.user_id ' \
                            'inner join user_activities ua on u.id = ua.user_id ' \
                            'where(ua.blocked is null or ua.blocked = 0) ' \
                            'group by u.id order by total desc limit 10'
