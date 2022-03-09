import config
import periphery
import telebot
import schedule
from kernel import BotParser
from periphery import *
from threading import Thread
from bot_logging import logger

logger.success("The bot has started working!")
logger.success("Bot version: 3.10 (March 9th)")

bot = telebot.TeleBot(config.TOKEN)
parser = BotParser()

specialization = '0'
course = '0'
week = '0'
table = '0'
on_air = [False]


@logger.catch
@bot.message_handler(commands=['r_start'])
def start(message):
    global on_air
    if parser.driver is not None or on_air[0] is True:
        bot.send_message(message.from_user.id, text='Бот занят, повторите попытку чуть позже (~15 сек.)')
    else:
        on_air[0] = True
        logger.info("R_START")
        check_in_db(message)
        message_id_ = bot.send_message(message.chat.id, "Ожидайте...⏳").message_id
        _spec_, _course_ = get_reg(message)
        if _spec_ is not None and _course_ is not None:
            parser.start()
            parser.login()
            parser.go_to_spec(_spec_)
            parser.go_to_week(str(_course_))
            message_id_1 = bot.send_message(message.chat.id, "Выберите неделю...",
                                            reply_markup=show_week(parser.parse_week())).message_id
            timeout = Thread(target=timeout_func, args=(bot, parser, message, message_id_1, on_air,))
            timeout.start()
        else:
            bot.send_message(message.chat.id, "Вам надо зарегистрироваться! (Воспользуйтесь командой /register)")
            on_air[0] = False
        bot.delete_message(chat_id=message.chat.id, message_id=message_id_)
        periphery.bot_call += 1


@logger.catch
@bot.message_handler(commands=['start'])
def start_message(message):
    global on_air
    if parser.driver is not None or on_air[0] is True:
        bot.send_message(message.from_user.id, text='Бот занят, повторите попытку чуть позже (~15 сек.)')
    else:
        on_air[0] = True
        logger.info("START")
        parser.start()
        check_in_db(message)
        message_id_ = bot.send_message(message.from_user.id, text='Выберите специальность...',
                                       reply_markup=main_buttons()).message_id
        parser.login()
        timeout = Thread(target=timeout_func, args=(bot, parser, message, message_id_, on_air,))
        timeout.start()
        periphery.bot_call += 1


@logger.catch
@bot.message_handler(commands=['plan'])
def curriculum(message):
    global on_air
    if parser.driver is not None or on_air[0] is True:
        bot.send_message(message.from_user.id, text='Бот занят, повторите попытку чуть позже (~15 сек.)')
    else:
        on_air[0] = True
        logger.info("PLAN")
        parser.start()
        check_in_db(message)
        message_id_ = bot.send_message(message.from_user.id, text='Выберите специальность...',
                                       reply_markup=spec_plan_buttons()).message_id
        parser.login_plan()
        timeout = Thread(target=timeout_func, args=(bot, parser, message, message_id_, on_air,))
        timeout.start()
        periphery.bot_call += 1


@logger.catch
@bot.message_handler(commands=['exam'])
def start_message(message):
    global on_air
    if parser.driver is not None or on_air[0] is True:
        bot.send_message(message.from_user.id, text='Бот занят, повторите попытку чуть позже (~15 сек.)')
    else:
        on_air[0] = True
        logger.info("EXAM")
        parser.start()
        check_in_db(message)
        message_id_ = bot.send_message(message.from_user.id, text='Выберите специальность...',
                                       reply_markup=main_buttons()).message_id
        parser.login_ex()
        timeout = Thread(target=timeout_func, args=(bot, parser, message, message_id_, on_air,))
        timeout.start()
        periphery.bot_call += 1


@logger.catch
@bot.message_handler(commands=[config.data])
def statistics_message(message):
    bot.send_message(message.chat.id, "Analytics for " + str(datetime.now().strftime("%H:%M")) + ":\n" +
                     str(periphery.new_user) + " New User\n" +
                     str(periphery.new_registration) + " New Registration\n" +
                     str(periphery.bot_call) + " Bot Calls\n" +
                     str(periphery.successfully_sent) + " Successfully sent")
    bot.send_document(message.chat.id, open(r"log.txt", 'rb'))
    bot.send_document(message.chat.id, open(r"data.db", 'rb'))
    bot.send_document(message.chat.id, open(r"users.db", 'rb'))
    if str(message.chat.id) == config.developer_id:
        logger.success("Statistics and data were sent to developer (@kelv1n9).")
    else:
        logger.success("Statistics and data were sent to " + str(message.chat.id))
        bot.send_message(config.developer_id, "Statistics and data were sent to " + str(message.chat.id))


@logger.catch
@bot.message_handler(commands=[config.users])
def all_message(message):
    con = sqlite3.connect('users.db')
    with con:
        cur = con.cursor()
        cur.execute("SELECT id FROM data_base")
        sent = 0
        while True:
            row = cur.fetchone()
            if row is None:
                break
            try:
                bot.send_message(row[0], message.text.replace("/" + config.users, ''), )
                time.sleep(10)
                sent += 1
            except telebot.apihelper.ApiException:
                logger.error("Error sending text to user " + str(row[0]))
        logger.success(str(sent) + ' user(s) received the message.')


@logger.catch
@bot.message_handler(commands=['to_developer'])
def dev_message(message):
    send = bot.send_message(message.chat.id, "Напишите ваше сообщение разработчику:")
    bot.register_next_step_handler(send, dev_send)


@logger.catch
def dev_send(message):
    bot.send_message(config.developer_id, message.text.replace('/to_developer', '') + "\n" + "\n" +
                     "From:" +
                     "\n" + "User_id: " + str(message.chat.id) +
                     "\n" + "Name: " + str(message.from_user.first_name) +
                     "\n" + "Last name: " + str(message.from_user.last_name) +
                     "\n" + "UserName: " + str(message.from_user.username))
    bot.send_message(message.chat.id, "Ваше сообщение успешно доставлено разработчику!")
    logger.success("Message to the developer!")


@logger.catch
@bot.message_handler(commands=[config.user])
def get_id(message):
    send = bot.send_message(message.chat.id, "Введите id пользователя")
    bot.register_next_step_handler(send, admin_message)


@logger.catch
def admin_message(message):
    user_id_ = message.text
    send = bot.send_message(message.chat.id, "Введите сообщение пользователю")
    bot.register_next_step_handler(send, user_send, user_id_)


@logger.catch
def user_send(message, user_id_):
    bot.send_message(user_id_, message.text + "\n" + "\n" +
                     "C уважением, разработчик.\n" +
                     "Также Вы можете обратиться сюда: @kelv1n9")
    bot.send_message(message.chat.id, "Ваше сообщение успешно доставлено пользователю!")
    logger.success("Your message has been successfully delivered to the user!")


@logger.catch
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Вы вызвали пояснительную бригаду.')
    bot.send_message(
        message.chat.id,
        'Нажмие "/start" для получения расписания, "/exam" для экзаменов, "/plan" для учебного плана;\n\n' +
        'Выберите специальность;\n' +
        'Выберите курс;\n' +
        'Выбереите неделю.\n\n' +
        'Вы можете зарегистрироваться, вам не нужно будет вбивать свой факультет и курс.\n' +
        'Для этого выполните команду "/register" и зарегистрируйтесь.\n' +
        'Для перезаписи данных выполните эту команду снова.\n\n' +
        'Если вы зарегистрированы, используйте команду "/r_start".\n\n' +
        'В случае ошибки (>10 сек) выполните команду снова для перезапуска.\n\n' +
        'Все основные команды находятся в меню.\n\n' +
        'Для благодарности или новой идеи нажмите "/to_developer", далее следуйте инструкциям\n' +
        '(Ваше сообщение увидит только разработчик).')
    logger.success('Someone called for help!')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global specialization, course, table, parser, on_air

    keyboard = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(text='1', callback_data='1')
    keyboard.add(key_1)
    key_2 = types.InlineKeyboardButton(text='2', callback_data='2')
    keyboard.add(key_2)
    key_3 = types.InlineKeyboardButton(text='3', callback_data='3')
    keyboard.add(key_3)
    key_4 = types.InlineKeyboardButton(text='4', callback_data='4')
    keyboard.add(key_4)

    if call.data == 'physics':
        specialization = 'Физика'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == 'physics_m':
        specialization = 'Физика М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == 'physics_n_m':
        specialization = 'Физика - Физика наночастиц  М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == 'phy_bs_m':
        specialization = 'Физика - Физика биологических систем  М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry":
        specialization = 'Химия'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry_m":
        specialization = 'Химия М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chem_f_m":
        specialization = 'Химия - Физическая химия М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry_f":
        specialization = 'Химия - Физхимия'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry_nf":
        specialization = 'Химия - Нефтехимия'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry_nf_m":
        specialization = 'Химия - Нефтехимия М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chemistry_o":
        specialization = 'Химия - Органика'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "chem_o_m":
        specialization = 'Химия - Органическая химия М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == 'economy':
        specialization = 'Экономика'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "management":
        specialization = 'Менеджмент'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "management_m":
        specialization = 'Менеджмент М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "psychology":
        specialization = 'Психология'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "psy_kpr_m":
        specialization = 'Психология М - Клинико-психологическая реабилитация'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "psychology_s_m":
        specialization = 'Психология М. - Социальная психология'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "psy_r_m":
        specialization = 'Психология М. - Психология развития'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "math":
        specialization = 'Математика и компьютерные науки'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "math_m":
        specialization = 'Математика и компьютерные науки М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_fil":
        specialization = 'Филология - Русское отделение'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_fil_m":
        specialization = 'Филология - Русское отделение М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_fr":
        specialization = 'Филология - Французское отделение'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_fr_m":
        specialization = 'Филология - Французское отделение М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_eng":
        specialization = 'Филология - Английское отделение'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "ru_eng_m":
        specialization = 'Филология - Английское отделение М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_italy":
        specialization = 'Филология - Итальянское отделение'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "ru_it_m":
        specialization = 'Филология - Итальянское отделение М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_isp":
        specialization = 'Филология - Испанское отделение'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)
    elif call.data == "rus_isp_m":
        specialization = 'Филология - Испанское отделение М.'
        bot.edit_message_text('Вы выбрали ' + specialization + '\nВыберите курс...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=keyboard)
        parser.go_to_spec(specialization)

    if call.data == 'mag_':
        bot.edit_message_text('Выберите специальность...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=mag_buttons())

    if call.data == '1':
        course = '1'

        bot.edit_message_text('Вы выбрали 1 курс, ожидайте...⏳',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

        parser.go_to_week(course)
        bot.edit_message_text('Выберите неделю...', chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=show_week(parser.parse_week()))

    elif call.data == '2':
        course = '2'

        bot.edit_message_text('Вы выбрали 2 курс, ожидайте...⏳',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

        parser.go_to_week(course)
        bot.edit_message_text('Выберите неделю...', chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=show_week(parser.parse_week()))

    elif call.data == '3':
        course = '3'

        bot.edit_message_text('Вы выбрали 3 курс, ожидайте...⏳',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

        parser.go_to_week(course)
        bot.edit_message_text('Выберите неделю...', chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=show_week(parser.parse_week()))

    elif call.data == '4':
        course = '4'

        bot.edit_message_text('Вы выбрали 4 курс, ожидайте...⏳',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

        parser.go_to_week(course)
        bot.edit_message_text('Выберите неделю...', chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=show_week(parser.parse_week()))

    if "-" in call.data:
        logger.info(str(call.data))
        try:
            bot.edit_message_text("Ожидайте, ваш запрос выполняется... ⏳", chat_id=call.message.chat.id,
                                  message_id=call.message.id)
            parser.go_to_table(call.data)
            bot.send_photo(chat_id=call.message.chat.id, photo=parser.screenshot(), caption="Удачного дня! 😉")
            periphery.successfully_sent += 1
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            logger.success("Successfully sent!")
        except Exception:
            logger.error("Failed sending.")

    if call.data == "physics_reg":
        specialization = 'Физика'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_reg":
        specialization = 'Химия'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_reg":
        specialization = 'Химия'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_f_reg":
        specialization = 'Химия - Физхимия'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_nf_reg":
        specialization = 'Химия - Нефтехимия'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_o_reg":
        specialization = 'Химия - Органика'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == 'economy_reg':
        specialization = 'Экономика'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "management_reg":
        specialization = 'Менеджмент'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "psychology_reg":
        specialization = 'Психология'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "math_reg":
        specialization = 'Математика и компьютерные науки'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_fil_reg":
        specialization = 'Филология - Русское отделение'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_fr_reg":
        specialization = 'Филология - Французское отделение'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_eng_reg":
        specialization = 'Филология - Английское отделение'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_italy_reg":
        specialization = 'Филология - Итальянское отделение'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_isp_reg":
        specialization = 'Филология - Испанское отделение'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())

    if call.data == "physics_m_reg":
        specialization = 'Физика М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "physics_n_m_reg":
        specialization = 'Физика - Физика наночастиц  М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "phy_bs_m_reg":
        specialization = 'Физика - Физика биологических систем  М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_m_reg":
        specialization = 'Химия М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chem_f_m_reg":
        specialization = 'Химия - Физическая химия М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chemistry_nf_m_reg":
        specialization = 'Химия - Нефтехимия М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "chem_o_m_reg":
        specialization = 'Химия - Органическая химия М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "management_m_reg":
        specialization = 'Менеджмент М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "psy_kpr_m_reg":
        specialization = 'Психология М - Клинико-психологическая реабилитация'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "psychology_s_m_reg":
        specialization = 'Психология М. - Социальная психология'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "psy_r_m_reg":
        specialization = 'Психология М. - Психология развития'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "math_m_reg":
        specialization = 'Математика и компьютерные науки М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_fil_m_reg":
        specialization = 'Филология - Русское отделение М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_fr_m_reg":
        specialization = 'Филология - Французское отделение М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "ru_eng_m_reg":
        specialization = 'Филология - Английское отделение М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "ru_it_m_reg":
        specialization = 'Филология - Итальянское отделение М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())
    elif call.data == "rus_isp_m_reg":
        specialization = 'Филология - Испанское отделение М.'
        get_spec_reg(specialization)
        bot.edit_message_text("Выберите ваш курс:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=reg_s_buttons())

    if call.data == "1_r":
        course = '1'
        get_course_reg(course)
        register(call.message)
        bot.edit_message_text("Вы успешно зарегистрировались!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

    if call.data == "2_r":
        course = '2'
        get_course_reg(course)
        register(call.message)
        bot.edit_message_text("Вы успешно зарегистрировались!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

    if call.data == "3_r":
        course = '3'
        get_course_reg(course)
        register(call.message)
        bot.edit_message_text("Вы успешно зарегистрировались!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

    if call.data == "4_r":
        course = '4'
        get_course_reg(course)
        register(call.message)
        bot.edit_message_text("Вы успешно зарегистрировались!",
                              chat_id=call.message.chat.id,
                              message_id=call.message.id)

    if call.data == 'mag_reg':
        bot.edit_message_text('Выберите специальность...',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=mag_reg_buttons())

    if "/" in call.data:
        try:
            bot.edit_message_text("Ожидайте, ваш запрос выполняется... ⏳", chat_id=call.message.chat.id,
                                  message_id=call.message.id)
            parser.go_to_year_cur(call.data)
            bot.send_photo(chat_id=call.message.chat.id, photo=parser.screenshot(), caption="Удачного дня! 😉")
            periphery.successfully_sent += 1
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            logger.success("Successfully sent!")
        except Exception:
            logger.error("Failed sending.")

    if call.data == 'list_error':
        eggs = ['(>^_^)>', '<(^_^<)', '(>_<)', '(o)_(o)', '(^*o*)^', 'ヾ(⌐■_■)ノ♪', 'ᕦ(ò_óˇ)ᕤ', '(☞ﾟ∀ﾟ)☞', "\ (•◡•) /"]
        for n in eggs:
            bot.edit_message_text(n,
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.id)
            time.sleep(0.3)
        logger.debug('Someone found an egg! :)')

    for k, v in config.specialties.items():
        if call.data == v:
            keyboard_term = types.InlineKeyboardMarkup()
            for kk, vv in config.term.items():
                key_term = types.InlineKeyboardButton(text=vv, callback_data=str(kk) + "_cur")
                keyboard_term.add(key_term)
            bot.edit_message_text('Выберите семестр...',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.id, reply_markup=keyboard_term)
            parser.go_to_spec_cur(k)

    for kt, vt in config.term.items():
        if call.data == vt + "_cur":
            logger.info(vt)
            bot.edit_message_text("Выберите год...", chat_id=call.message.chat.id,
                                  message_id=call.message.id, reply_markup=show_week(parser.parse_year()))
            parser.go_to_term_cur(vt)


@logger.catch
@bot.message_handler(commands=['register'])
def reg_spec(message):
    bot.send_message(message.chat.id, "Выберите вашу специальность:", reply_markup=reg_c_buttons())


schedule.every().day.at(config.sending_time).do(scheduled_dispatch, bot)  # UTC+0


def shed():
    while True:
        schedule.run_pending()
        time.sleep(1)


def init():
    bot.infinity_polling()


thread1 = Thread(target=init)  # Поток 1
thread1.start()

thread2 = Thread(target=shed)  # Поток 2
thread2.start()
