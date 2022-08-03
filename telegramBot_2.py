import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
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
    change_students,
    checkUser,
    user_name,
    instructor_surname
)
from config import TOKEN, ms_chat_id

# Стартовая настройка бота

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

Uchenik, Grupa = range(2)
REG, REG2 = range(2)
FIO, NUMBER = range(2)
teoria,vozdenie = 'teoria', 'vozdenie'
CHANGE, NOMER_UCHENIKA, WHAT, FIO_ADD, NUMBER_ADD = range(5)
FIO_MS, CATEGORII, OL, PHOTO, PHOTO2 = range(5)


# Команды и функции бота

def start(update: Update, context: CallbackContext):
    """Справочная команда старт"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Бот для подачи учеников на теорию или вождение, подачи м/с или отчётов")


def reg_user(update, context):
    if checkUser(update, context) == 'Новый пользователь':
        update.message.reply_text('Введите свою фамилию: ')
        return REG
    else:
        update.message.reply_text(checkUser(update, context))
        update.message.reply_text("Я знаю кто ты:"
                                  "{}\n".format(facts_to_str(context)))
        return ConversationHandler.END

def reg_user_surname(update, context):
    context.user_data['Фамилия'] = update.message.text
    update.message.reply_text('Теперь введите своё имя: ')
    return REG2

def reg_user_name(update, context):
    context.user_data['Имя'] = update.message.text
    user_name(ID=update.effective_chat.id, name=context.user_data['Имя'], surname=context.user_data['Фамилия'])
    update.message.reply_text("Теперь я знаю кто ты:"
                              "{}\n".format(facts_to_str(context)))
    return ConversationHandler.END


def facts_to_str(context):
    facts = list()

    for key, value in context.user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])

'''--------------------------------Функции для подачи ученика в список----------------------------------------------'''

def podacha(update: Update, context: CallbackContext):
    """Функция принимает введённую пользователем фамилию инструктора, сохраняет значение по ключу,
    выводит в логах и запрашивает фамилию и имя ученика, отправляет на след. шаг"""
    instructor_surname(update,context)
    logger.info("Фамилия инструктора: %s", context.user_data['Фамилия'])
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
    add_teoria(id=update.message.chat['id'], Instructor=context.user_data['Фамилия'],
               Uchenik=context.user_data[Uchenik], Grupa=context.user_data[Grupa])
    update.message.reply_text(f'''
    Ученик добавлен в список на теорию!\n  
    Вы: {context.user_data['Фамилия']}
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
    add_vozdenie(id=update.message.chat['id'], Instructor=context.user_data['Фамилия'],
                 Uchenik=context.user_data[Uchenik], Grupa=context.user_data[Grupa])
    update.message.reply_text(f'''
    Ученик добавлен в список на вождение!\n  
    Вы: {context.user_data['Фамилия']}
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
def change_what(update: Update, context: CallbackContext):
    button1 = [InlineKeyboardButton("Теория", callback_data=teoria)]
    button2 = [InlineKeyboardButton("Вождение", callback_data=vozdenie)]

    reply_markup = InlineKeyboardMarkup([button1, button2])

    update.message.reply_text(
        "Если хотите отменить изменение введите команду /cancel. \n\n"
        "В какой список требуется внести изменение:",
        reply_markup=reply_markup
    )
    return CHANGE


def change(update: Update, context: CallbackContext):
    """Функция начала беседы бота для изменения данных в базе учеников """
    query = update.callback_query
    query.answer()
    choice = query.data
    # Now u can define what choice ("callback_data") do what like this:
    if choice == 'teoria':
        context.user_data['Spisok'] = 'teoria'

    if choice == 'vozdenie':
        context.user_data['Spisok'] = 'vozdenie'
    query.edit_message_text(text='Если хотите отменить изменение введите команду /cancel. \n\n'
                            'Введите номер ученика в списке: ')
    return NOMER_UCHENIKA


def nomer_uchenika(update: Update, context: CallbackContext):
    """Функция для получения номера ученика в списке.
    Предлагает выбор из кнопок для изменения Фамилии и имени или номера группы ученика"""
    context.user_data['NOMER_UCHENIKA'] = update.message.text
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
    change_students(table=context.user_data['Spisok'],student_id=context.user_data['NOMER_UCHENIKA'],
                    data='Uchenik', value=context.user_data[Uchenik])
    update.message.reply_text(
        f'Ученик {context.user_data[Uchenik]} исправлен в списке на вождение '
        f'под номером {context.user_data["NOMER_UCHENIKA"]}!')
    return ConversationHandler.END


def number_to_base(update, context: CallbackContext):
    """Обновляет в базе выбранного ученика его номер группы, завершает беседу"""
    logger.info("Новый номер группы: %s", update.message.text)
    context.user_data[Grupa] = update.message.text
    change_students(table=context.user_data['Spisok'], student_id=context.user_data['NOMER_UCHENIKA'], data='Grupa', value=context.user_data[Grupa])
    update.message.reply_text(
        f'Номер группы исправлен в списке на вождение под номером {context.user_data["NOMER_UCHENIKA"]}!')
    return ConversationHandler.END



def ms(update: Update, _):
    update.message.reply_text('Если хотите отменить подачу введите команду /cancel. \n\n'
                              'Введите Фамилию Имя Отчество ученика: ')
    return FIO_MS

def fio_ms(update: Update, context: CallbackContext):
    context.user_data['fio_ms'] = update.message.text
    logger.info("ФИО ученика: %s", update.message.text)
    button1 = [InlineKeyboardButton("B,M,B1", callback_data='B')]
    button2 = [InlineKeyboardButton("A,M,A1", callback_data='A')]
    button3 = [InlineKeyboardButton("A,B,M,A1,B1", callback_data='AB')]

    reply_markup = InlineKeyboardMarkup([button1, button2, button3])

    update.message.reply_text(
        "Если хотите отменить изменение введите команду /cancel. \n\n"
        "Какие категории:",
        reply_markup=reply_markup
    )
    return CATEGORII

def categorii(update: Update, context: CallbackContext):
    """Функция начала беседы бота для изменения данных в базе учеников """
    query = update.callback_query
    query.answer()
    choice = query.data
    # Now u can define what choice ("callback_data") do what like this:
    if choice == 'A':
        context.user_data['Categorii'] = 'A,M,A1'

    if choice == 'B':
        context.user_data['Categorii'] = 'B,M,B1'

    if choice == 'AB':
        context.user_data['Categorii'] = 'A,B,M,A1,B1'
    logger.info("Категории ученика: %s", context.user_data['Categorii'])

    button1 = [InlineKeyboardButton("Носит", callback_data='Yes')]
    button2 = [InlineKeyboardButton("Не носит", callback_data='No')]

    reply_markup = InlineKeyboardMarkup([button1, button2])
    query.edit_message_text(text='Носит ли ученик очки/линзы? ', reply_markup=reply_markup)

    return OL

def ol(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice = query.data
    # Now u can define what choice ("callback_data") do what like this:
    if choice == 'Yes':
        context.user_data['Ol'] = 'О/л'

    if choice == 'No':
        context.user_data['Ol'] = 'Б/о'
    query.edit_message_text(text='Последний шаг - прикрепите фото паспорта по одному фото за раз(сначала главный разворот): ')
    return PHOTO

def photo(update: Update, context: CallbackContext):
    """"""
    context.user_data['photo'] = update.message.photo[-1]['file_id']
    update.message.reply_text(
        'Первое фото сохранено. Теперь отправьте второе фото(разворот с пропиской:'
    )

    return PHOTO2

def photo2(update: Update, context: CallbackContext):
    context.user_data['photo2'] = update.message.photo[-1]['file_id']
    update.message.reply_text(
        'Второе фото сохранено'
    )
    list_of_urls = [
        context.user_data['photo'],
        context.user_data['photo2'],
    ]
    media_group = list()
    text = f'ФИО:{context.user_data["fio_ms"]}\nКатегории:{context.user_data["Categorii"]}\n{context.user_data["Ol"]}'
    for number, url in enumerate(list_of_urls):
        media_group.append(InputMediaPhoto(media=url, caption=text if number == 0 else ''))
    context.bot.send_media_group(chat_id=ms_chat_id, media=media_group)
    update.message.reply_text(
        'Данные отправлены'
    )
    return ConversationHandler.END


def unknown(update: Update, context: CallbackContext):
    """Функция для всех других сообщений и команд, которые бот не знает"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Сори, я не понимаю эту команду")

'''---------------------------------------Главная программа для запуска бота-----------------------------------------'''

def main():
    updater = Updater(token=TOKEN, use_context=True)
    print("Соединение с телеграмм установлено! Запуск бота")
    dispatcher = updater.dispatcher

    # Добавление хэндлеров и диспетчера
    '''-----------------------------------------------------------------------------------------------------------'''
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    reg_user_handler = ConversationHandler(
        entry_points=[CommandHandler('reg', reg_user)],
        states={
            REG: [MessageHandler(Filters.text & ~Filters.command, reg_user_surname, pass_user_data=True)],
            REG2: [MessageHandler(Filters.text & ~Filters.command, reg_user_name, pass_user_data=True)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(reg_user_handler)
    '''-----------------------------------------------------------------------------------------------------------'''
    teoria_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[CommandHandler('teoria', podacha)],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
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
            Uchenik: [MessageHandler(Filters.text & ~Filters.command, uchenik, pass_user_data=True)],
            Grupa: [MessageHandler(Filters.text & ~Filters.command, grupa_vozdenie, pass_user_data=True)],
        },
        # точка выхода из разговора
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(vozdenie_handler)

    change_handler = ConversationHandler(
        entry_points=[CommandHandler(command='change', callback=change_what)],
        states={
            CHANGE: [CallbackQueryHandler(change, pattern='^' + str(teoria) + '$'),
                   CallbackQueryHandler(change, pattern='^' + str(vozdenie) + '$')],
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

    ms_handler = ConversationHandler(
        entry_points=[CommandHandler(command='ms', callback=ms)],
        states={
            FIO_MS: [MessageHandler(Filters.text & ~Filters.command, fio_ms, pass_user_data=True)],
            CATEGORII: [CallbackQueryHandler(categorii, pattern='^' + 'A' + '$'),
                        CallbackQueryHandler(categorii, pattern='^' + 'B' + '$'),
                        CallbackQueryHandler(categorii, pattern='^' + 'AB' + '$')],
            OL: [CallbackQueryHandler(ol, pattern='^' + 'Yes' + '$'),
                 CallbackQueryHandler(ol, pattern='^' + 'No' + '$')],
            PHOTO: [MessageHandler(Filters.photo, photo, pass_user_data=True)],
            PHOTO2: [MessageHandler(Filters.photo, photo2, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(ms_handler)

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
