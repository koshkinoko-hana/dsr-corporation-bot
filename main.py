import telegram
import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters
from user import check_or_create_user, form_message, start_game, clear_total, get_rating, user_answer, game_not_started, \
    ready_for_congratulations, fill_users

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

token = '5131416625:AAHhnJKY3bLMx54JA_dwMrwP1vKs-J-nsQ8'

bot = telegram.Bot(token)
default_message = 'Чтобы начать игру, введи /game. Чтобы получить поздравление, отправь /congratulation. ' \
                  'Все команды - /commands.'

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Start:\nuser:\n%s\n", user)

    exists = check_or_create_user(user)
    message = '' if exists else 'Привет! Я DSR бот. Предлагаю сыграть в игру! ' \
                                'Если ты наберёшь 10 очков, то получишь персональное поздравление. ' \
                                'Получить правила игры - /rules .'
    message += default_message
    logger.info("Start:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    update.message.reply_html(message)


def get_congratulation(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Get congratulation:\nuser:\n%s\n", user)
    check_or_create_user(user)

    message = form_message(user.id, False)
    logger.info("Get congratulation:\nuser:\n%s,\nresponse: \n%s\n", user, message)
    update.message.reply_html(
        message
    )


def default(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Default:\nuser:\n%s\n", user)

    exists = check_or_create_user(user)
    message = default_message if exists else 'Привет! Я DSR бот. Предлагаю сыграть в игру! ' \
                                'Если ты наберёшь 10 очков, то получишь персональное поздравление. ' \
                                'Получить правила игры - /rules .' + default_message

    if not game_not_started(user.id):
        message = 'Для отправки хода введи латинскую букву и число, ' \
                  'соответсвующие строке и колонке на поле. Или начни новую игру /game. Все команды - /commands'

    logger.info("Default:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    update.message.reply_html(
        message
    )


def game(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Game:\nuser:\n%s\n", user)

    message = start_game(user)
    logger.info("Game:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    update.message.reply_html(
        message
    )


def process_answer(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Process answer:\nuser:\n%s\n", user)

    message = user_answer(user, update.message.text)
    logger.info("Process answer:\nuser:\n%s,\nresponse:\n%s\n", user, message)
    update.message.reply_html(
        message
    )
    if ready_for_congratulations(user.id):
        logger.info("Process answer - personal congrats:\nuser:\n%s\n", user)
        update.message.reply_html(
            'Ты заработал 10 очков! Получи своё персональное поздравление!'
        )
        update.message.reply_html(
            form_message(user.id, True)
        )


def rating(update: Update, context: CallbackContext) -> None:
    update.message.reply_html(
        get_rating()
    )


def clear_process(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("Clear process: user: %s", user)
    clear_total(user.id)
    update.message.reply_html(
        'Достижения обнулены! У вас 0 очков.'
    )


def rules(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        'В игре есть поле 5 на 5. Там спрятаны 10 мин. '
        'У тебя есть 15 ходов, чтобы найти как можно больше мин. Очки между играми суммируются. '
        'Для каждого хода введи букву(строка) и число(колонка). '
        'Можно вводить несколько ходов одновременно, разделяя их запятыми. '
        'Как только ты наберёшь 10 очков, ты получишь персональное поздравление! Для начала игры отправь /game. '
        'Набери как можно больше очков, чтобы попасть в рейтинг!'
    )


def commands(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        '/game - начать новую игру\n'
        '/congratulation - получить поздравление\n'
        '/rules -  правила игры\n'
        '/clear - очистить достижения\n'
        '/rating - топ 10 пользователей в игре\n'
    )

def main() -> None:
    fill_users()
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("congratulation", get_congratulation))
    dispatcher.add_handler(CommandHandler("clear", clear_process))
    dispatcher.add_handler(CommandHandler("game", game))
    dispatcher.add_handler(CommandHandler("rules", rules))
    dispatcher.add_handler(CommandHandler("rating", rating))
    dispatcher.add_handler(CommandHandler("commands", commands))
    dispatcher.add_handler(MessageHandler(Filters.regex('([a-eA-E][1-5][, ]*){1,10}'), process_answer))
    dispatcher.add_handler(MessageHandler(Filters.all, default))

    # Start the Bot
    updater.start_polling()
    updater.idle()


main()
