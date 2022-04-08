import datetime
from pytz import timezone
import random

import telegram
import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters, JobQueue
from students_quiz.user import check_or_create_user, make_question, user_answer, get_rating, results, get_my_result
from students_quiz.init import ACTIVITY, current_question, init_quiz
from students_quiz.stickers import stickers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

token = '5131416625:AAHhnJKY3bLMx54JA_dwMrwP1vKs-J-nsQ8'

bot = telegram.Bot(token)

jobQueue = JobQueue()

rules_message = 'Правила квиза «Угадай язык программирования» \n\n' \
                '1. После получения вопроса твоё первое сообщение будет засчитано за ответ. ' \
                'Чем быстрее ты ответишь, тем больше баллов получишь. ' \
                'Убедись, что уверен в своём ответе и написал его без ошибок. \n\n' \
                '2. Ответ можно написать на русском или английском, без знаков препинания. Регистр не учитывается\n\n' \
                '3. Сообщения, отправленные после ответа, ботом не учитываются.\n\n' \
                '4. Вопросы, помеченные подмигивающим медведем — повышенной сложности. ' \
                'За правильный ответ на них ты получишь больше очков.\n\n' \
                'Вызвать правила можно в любой момент командой /rules\n\nУдачи!'

default_message_before = 'Наш квиз «Угадай язык программирования» начнётся в 12:00 и завершится в 14:00. ' \
                         'Тебя ждут 12 вопросов. На каждый ответ отводится 10 минут. \n\n' \
                         'Чем быстрее ты ответишь, тем выше шанс победить. Скоро ты получишь первый вопрос. \n\n' \
                         'Не забудь подписаться на наш Telegram-канал с новостями, анонсами бесплатных курсов и ' \
                         'горящими вакансиями: https://t.me/dsr_news \n\n'

default_message = 'Не спеши! Следующий вопрос на подходе :)'

logger = logging.getLogger(__name__)


def send_sticker(user_id) -> None:
    sticker = random.choice(stickers)
    bot.send_sticker(user_id, sticker=sticker)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Start:\nuser:\n%s\n", user)

    exists = check_or_create_user(user)
    if isinstance(exists, str):
        update.message.reply_html(exists)
        return

    message = '' if exists else 'Привет! Я DSR бот.  '

    if ACTIVITY.get('START_DATE') > datetime.datetime.now().astimezone(timezone('Europe/Volgograd')):
        message += default_message_before
    elif not exists:
        message += 'Квиз уже начался. Скоро ты получишь следующий вопрос. '
    elif exists:
        message += default_message
    message += '' if exists else rules_message

    logger.info("Start:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    update.message.reply_html(message)
    send_sticker(user.id)


def rating(update: Update, context: CallbackContext) -> None:
    send_sticker(update.effective_user.id)
    update.message.reply_html(
        get_rating()
    )


def my_result(update: Update, context: CallbackContext) -> None:
    send_sticker(update.effective_user.id)

    if not current_question.get('winner_exists'):
        update.message.reply_html(
            'Функция станет доступна по окончанию квиза.'
        )
    else:
        update.message.reply_html(
            get_my_result(update.effective_user.id)
        )


def rules(update: Update, context: CallbackContext) -> None:
    update.message.reply_html(rules_message)


def commands(update: Update, context: CallbackContext) -> None:
    update.message.reply_html(
        '/rules -  правила\n'
        '/rating - топ 10 пользователей на данный момент\n'
    )


def process_message(update: Update, context: CallbackContext) -> None:
    if current_question.get('winner_exists'):
        update.message.reply_html('Победитель определён! Спасибо за участие :)')
    user = update.effective_user
    answer = update.message.text
    logger.info("Process answer:\nuser:\n%s\nanswer:\n%s", user, update.message)

    (message, winner) = user_answer(user, answer)
    logger.info("Process answer response:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    send_sticker(user.id)
    update.message.reply_html(message)

    if winner:
        (a, ids) = make_question()

        for id in ids:
            bot.send_message(id, 'Победитель определён! Спасибо за участие. Для получения рейтинга отправь /rating. '
                                 'Для получения своего результата отправь /myresult')
            send_sticker(id)


def run_question(*args) -> None:
    (question, ids) = make_question()

    logger.info("run_question:\nquestion:\n%s,\nto users:\n%s\n", question, ids)
    message = 'Внимание! Первый ребус:' if question.get('name') == 'Вопрос 1' else 'Внимание! Следующий ребус: '
    if question.get('name') == 'Вопрос 13':
        (winner, mess) = results()
        if mess:
            bot.send_message(winner, mess)
            current_question.update({'winner_exists': True})
            for id in ids:
                bot.send_message(id, 'Победитель определён! Спасибо за участие. Для получения рейтинга отправь /rating. '
                                     'Для получения своего результата отправь /myresult')
            return
        else:
            message = 'Внимание! У нас несколько претендентов на победу. Финальный вопрос решит схватку: '
            ids = winner
            current_question.update({'pretenders': ids})
            logger.info("FINAL BATTLE:\nquestion:\n%s,\nto users:\n%s\n", question, ids)

    next_time = question.get('time_start') + datetime.timedelta(minutes=4, seconds=58)

    for id in ids:
        bot.send_message(id, message)
        bot.send_photo(id, photo=open('./students_quiz/questions/' + question.get('description'), 'rb'))

    jobQueue.run_once(callback=run_question, when=next_time)


def main() -> None:
    init_quiz()
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    jobQueue.set_dispatcher(dispatcher)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("rules", rules))
    dispatcher.add_handler(CommandHandler("rating", rating))
    dispatcher.add_handler(CommandHandler("myresult", my_result))
    dispatcher.add_handler(CommandHandler("commands", commands))
    dispatcher.add_handler(MessageHandler(Filters.all, process_message))

    # Start the Bot
    updater.start_polling()

    jobQueue.run_once(callback=run_question, when=ACTIVITY.get('START_DATE'))
    jobQueue.start()
