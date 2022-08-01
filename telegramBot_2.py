import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from base_bot import (
    add_teoria,
    add_vozdenie,
    check_students_teoria,
    check_students_vozdenie,
    change_students
)
from config import TOKEN

# Стартовая настройка бота

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

Instructor, Uchenik, Grupa = range(3)
FIO, NUMBER = range(2)
NOMER_UCHENIKA, WHAT, FIO_ADD, NUMBER_ADD = range(4)


# Команды и функции бота

def start(update: Update, context: CallbackContext):
    """Справочная команда старт"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Бот для подачи учеников на теорию или вождение, подачи м/с или отчётов")

'''--------------------------------Функции для подачи ученика в список----------------------------------------------'''

def podacha(update: Update, _):
    """Функция для начала подачи ученика на теорию или вождение,
    которая запрашивает фамилию инструктора и отправляет на следующий шаг(фамилию и имя ученика)"""
    update.message.reply_text('Если хотите отменить подачу введите команду /cancel. \n\n'
                              'Введите свою фамилию: ')
    return Instructor


def instructor(update: Update, context: CallbackContext):
    """Функция принимает введённую пользователем фамилию инструктора, сохраняет значение по ключу,
    выводит в логах и запрашивает фамилию и имя ученика, отправляет на след. шаг"""
    user = update.message.from_user
    context.user_data[Instructor] = update.message.text
    logger.info("Фамилия инструктора(%s): %s", user.first_name, update.message.text)
    update.message.reply_text('Теперь введите Фамилию и Имя ученика: ')
    return Uchenik


def uchenik(update, context: CallbackContext):
    """Функция принимает введённую пользователем фамилию и имя ученика, сохраняет значение по ключу,
    выводит в логах и запрашивает номер группы ученика, отправляет на след. шаг"""
    logger.info("Фамилия и Имя ученика: %s", update.message.text)
    context.user_data[Uchenik] = update.message.text
    update.message.reply_text('Введите номер группы: ')
    return Grupa

'''-------------------------------------------------------------------------------------------------------------'''

def grupa_teoria(update, context: CallbackContext):
    """Финальный шаг для подачи на теорию.
    Функция принимает введённую пользователем группу ученика, сохраняет значение по ключу,
    добавляет данные в базу и выводит ответное сообщение пользователю """
    logger.info("Группа ученика: %s", update.message.text)
    context.user_data[Grupa] = update.message.text
    add_teoria(id=update.message.chat['id'], Instructor=context.user_data[Instructor],
               Uchenik=context.user_data[Uchenik], Grupa=context.user_data[Grupa])
    update.message.reply_text(f'''
    Ученик добавлен в список на теорию!\n  
    Вы: {context.user_data[Instructor]}
    Ученик: {context.user_data[Uchenik]}
    Группа: {context.user_data[Grupa]} 
    ''')
    return ConversationHandler.END

'''-------------------------------------------------------------------------------------------------------------'''

def grupa_vozdenie(update, context: CallbackContext):
    """Финальный шаг для подачи на вождение.
    Функция принимает введённую пользователем группу ученика, сохраняет значение по ключу,
    добавляет данные в базу и выводит ответное сообщение пользователю """
    logger.info("Группа ученика: %s", update.message.text)
    context.user_data[Grupa] = update.message.text
    add_vozdenie(id=update.message.chat['id'], Instructor=context.user_data[Instructor],
                 Uchenik=context.user_data[Uchenik], Grupa=context.user_data[Grupa])
    update.message.reply_text(f'''
    Ученик добавлен в список на вождение!\n  
    Вы: {context.user_data[Instructor]}
    Ученик: {context.user_data[Uchenik]}
    Группа: {context.user_data[Grupa]} 
    ''')
    return ConversationHandler.END


def cancel(update, _):
    """Функция для досрочного выхода из подачи ученика"""
    user = update.message.from_user
    logger.info("Пользователь %s отменил подачу.", user.first_name)
    update.message.reply_text('Подача отменена')
    return ConversationHandler.END

'''----------------------------------Функции для проверки учеников в списках-----------------------------------------'''

def check_teoria(update: Update, context: CallbackContext):
    """Функция для проверки в базе поданных на теорию учеников
    (отправляет обратно список только для id данного чата)"""
    students = check_students_teoria(update.message.chat['id'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=students)


def check_vozdenie(update: Update, context: CallbackContext):
    """Функция для проверки в базе поданных на вождение учеников
    (отправляет обратно список только для id данного чата)"""
    students = check_students_vozdenie(update.message.chat['id'])
    context.bot.send_message(chat_id=update.effective_chat.id, text=students)

'''---------------------------------------Функции для изменения информации об ученике--------------------------------'''

def change(update: Update, _):
    """Функция начала беседы бота для изменения данных в базе учеников """
    update.message.reply_text('Если хотите отменить изменение введите команду /cancel. \n\n'
                              'Введите номер ученика в списке: ')
    return NOMER_UCHENIKA


def nomer_uchenika(update: Update, context: CallbackContext):
    """Функция для получения номера ученика в списке.
    Предлагает выбор из кнопок для изменения Фамилии и имени или номера группы ученика"""
    context.user_data[NOMER_UCHENIKA] = update.message.text
    button1 = [InlineKeyboardButton("Фамилию и Имя", callback_data=str(FIO))]
    button2 = [InlineKeyboardButton("Номер группы", callback_data=str(NUMBER))]
    # create reply markup
    reply_markup = InlineKeyboardMarkup([button1, button2])
    # send message with text and appended inline keyboarde
    update.message.reply_text(
        "Выберите что вы хотите изменить:",
        reply_markup=reply_markup
    )
    return WHAT


def fio(update: Update, _):
    """Запускается при выборе изменения Фамилии и Имени ученика и запрашивает их у пользователя"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Теперь введите Фамилию и Имя ученика: "
    )
    return FIO_ADD


def number(update: Update, _):
    """Запускается при выборе изменения Номера группы и запрашивает их у пользователя"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Теперь введите Номер группы ученика: "
    )
    return NUMBER_ADD


def fio_to_base(update, context: CallbackContext):
    """Обновляет в базе выбранного ученика его имя и фамилию, завершает беседу"""
    logger.info("Новые Фамилия и Имя: %s", update.message.text)
    context.user_data[Uchenik] = update.message.text
    change_students(student_id=context.user_data[NOMER_UCHENIKA], data='Uchenik', value=context.user_data[Uchenik])
    update.message.reply_text(
        f'Ученик {context.user_data[Uchenik]} исправлен в списке на вождение '
        f'под номером {context.user_data[NOMER_UCHENIKA]}!')
    return ConversationHandler.END


def number_to_base(update, context: CallbackContext):
    """Обновляет в базе выбранного ученика его номер группы, завершает беседу"""
    logger.info("Новый номер группы: %s", update.message.text)
    context.user_data[Grupa] = update.message.text
    change_students(student_id=context.user_data[NOMER_UCHENIKA], data='Grupa', value=context.user_data[Grupa])
    update.message.reply_text(
        f'Номер группы исправлен в списке на вождение под номером {context.user_data[NOMER_UCHENIKA]}!')
    return ConversationHandler.END


def unknown(update: Update, context: CallbackContext):
    """Функция для всех других сообщений и команд, которые бот не знает"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сори, я не понимаю эту команду")

'''---------------------------------------Главная программа для запуска бота-----------------------------------------'''

def main():
    updater = Updater(token=TOKEN, use_context=True)
    print("Соединение с телеграмм установлено! Запуск бота:")
    dispatcher = updater.dispatcher

    # Добавление хэндлеров и диспетчера
    '''-----------------------------------------------------------------------------------------------------------'''
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    teoria_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('teoria', podacha)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            Instructor: [MessageHandler(Filters.text & ~Filters.command, instructor, pass_user_data=True)],
            Uchenik: [MessageHandler(Filters.text & ~Filters.command, uchenik, pass_user_data=True)],
            Grupa: [MessageHandler(Filters.text & ~Filters.command, grupa_teoria, pass_user_data=True)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(teoria_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    vozdenie_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('vozdenie', podacha)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            Instructor: [MessageHandler(Filters.text & ~Filters.command, instructor, pass_user_data=True)],
            Uchenik: [MessageHandler(Filters.text & ~Filters.command, uchenik, pass_user_data=True)],
            Grupa: [MessageHandler(Filters.text & ~Filters.command, grupa_vozdenie, pass_user_data=True)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(vozdenie_handler)

    change_handler = ConversationHandler(
        entry_points=[CommandHandler(command='change', callback=change)],
        states={
            NOMER_UCHENIKA: [MessageHandler(Filters.text & ~Filters.command, nomer_uchenika, pass_user_data=True)],
            WHAT: [CallbackQueryHandler(fio, pattern='^' + str(FIO) + '$'),
                   CallbackQueryHandler(number, pattern='^' + str(NUMBER) + '$')],
            FIO_ADD: [MessageHandler(Filters.text & ~Filters.command, fio_to_base, pass_user_data=True)],
            NUMBER_ADD: [MessageHandler(Filters.text & ~Filters.command, number_to_base, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(change_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    check_teoria_handler = CommandHandler('check_teoria', check_teoria)
    dispatcher.add_handler(check_teoria_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    check_vozdenie_handler = CommandHandler('check_vozdenie', check_vozdenie)
    dispatcher.add_handler(check_vozdenie_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    unknown_handler = MessageHandler(Filters.text & (~Filters.command), unknown)
    dispatcher.add_handler(unknown_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    # Запуск бота

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
