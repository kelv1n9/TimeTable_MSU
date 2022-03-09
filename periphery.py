from bot_logging import logger
from telebot import types
from datetime import datetime
from datetime import date as ddate
import config
import time
import sqlite3

_spec_reg = None
_course_reg = None
new_user = 0
new_registration = 0
bot_call = 0
successfully_sent = 0


@logger.catch
def register(message):
    global new_registration

    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS data(
                id INTEGER,
                spec TEXT,
                course INTEGER
            )""")
    connect.commit()

    people_id = message.chat.id
    cursor.execute(f"SELECT id FROM data WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO data(id, spec, course) VALUES(?,?,?)",
                       (message.chat.id, _spec_reg, _course_reg,))
        connect.commit()
        logger.info(
            "We have a new registration!\n" + str(_spec_reg) + ' ' + str(_course_reg) + ' ' + str(message.chat.id))
        new_registration += 1
    else:
        cursor.execute(f"UPDATE data SET spec = ?, course = ? WHERE id = ?",
                       (_spec_reg, _course_reg, message.chat.id,))
        connect.commit()


def get_spec_reg(spec):
    global _spec_reg
    _spec_reg = spec


def get_course_reg(spec):
    global _course_reg
    _course_reg = spec


@logger.catch
def get_reg(message):
    connect = sqlite3.connect('data.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT spec, course FROM data WHERE id = {message.chat.id}")
    data = cursor.fetchone()
    if data is None:
        return None, None
    else:
        return data


@logger.catch
def check_in_db(message):
    global new_user

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS data_base(
                id INTEGER,
                username TEXT,
                name TEXT,
                last_name TEXT
            )""")

    connect.commit()

    people_id = message.chat.id
    logger.info("USER ID: " + str(message.chat.id))
    cursor.execute(f"SELECT id FROM data_base WHERE id = {people_id}")
    data = cursor.fetchone()
    if data is None:
        user_id = message.chat.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        cursor.execute("INSERT INTO data_base(id, username, name, last_name) VALUES(?,?,?,?)",
                       (user_id, username, first_name, last_name,))
        connect.commit()
        logger.info(
            "We have a new user!\n" + str(first_name) + ' ' + str(last_name) + '\nUSERNAME: ' + str(
                username) + '\nID: ' + str(user_id))
        new_user += 1


def compare_date(*args):
    start, stop = args[0][0], args[0][1]
    start = ddate(start[0], start[1], start[2])
    stop = ddate(stop[0], stop[1], stop[2])
    if start <= ddate.today() <= stop:
        return True


def get_date(week_):
    _year = int(week_[6] + week_[7] + week_[8] + week_[9])
    year_ = int(week_[19] + week_[20] + week_[21] + week_[22])
    _month = int(week_[3] + week_[4])
    month_ = int(week_[16] + week_[17])
    _day = int(week_[0] + week_[1])
    day_ = int(week_[13] + week_[14])
    return [_year, _month, _day], [year_, month_, day_]


def main_buttons():
    keyboard = types.InlineKeyboardMarkup()

    key_physics = types.InlineKeyboardButton(text='Физика', callback_data='physics')
    keyboard.add(key_physics)
    key_chemistry = types.InlineKeyboardButton(text='Химия', callback_data='chemistry')
    keyboard.add(key_chemistry)
    key_chemistry_f = types.InlineKeyboardButton(text='Химия - Физхимия', callback_data='chemistry_f')
    keyboard.add(key_chemistry_f)
    key_chemistry_nf = types.InlineKeyboardButton(text='Химия - Нефтехимия', callback_data='chemistry_nf')
    keyboard.add(key_chemistry_nf)
    key_chemistry_o = types.InlineKeyboardButton(text='Химия - Органика', callback_data='chemistry_o')
    keyboard.add(key_chemistry_o)
    key_economy = types.InlineKeyboardButton(text='Экономика', callback_data='economy')
    keyboard.add(key_economy)
    key_management = types.InlineKeyboardButton(text='Менеджмент', callback_data='management')
    keyboard.add(key_management)
    key_psy = types.InlineKeyboardButton(text='Психология', callback_data='psychology')
    keyboard.add(key_psy)
    key_math = types.InlineKeyboardButton(text='Математика и компьютерные науки', callback_data='math')
    keyboard.add(key_math)
    key_rus_fil = types.InlineKeyboardButton(text='Филология - Русское отделение', callback_data='rus_fil')
    keyboard.add(key_rus_fil)
    key_rus_fr = types.InlineKeyboardButton(text='Филология - Французское отделение', callback_data='rus_fr')
    keyboard.add(key_rus_fr)
    key_rus_eng = types.InlineKeyboardButton(text='Филология - Английское отделение', callback_data='rus_eng')
    keyboard.add(key_rus_eng)
    key_rus_italy = types.InlineKeyboardButton(text='Филология - Итальянское отделение', callback_data='rus_italy')
    keyboard.add(key_rus_italy)
    key_rus_isp = types.InlineKeyboardButton(text='Филология - Испанское отделение', callback_data='rus_isp')
    keyboard.add(key_rus_isp)

    key_mag = types.InlineKeyboardButton(text='МАГИСТРАТУРА', callback_data='mag_')
    keyboard.add(key_mag)

    return keyboard


def reg_c_buttons():
    keyboard = types.InlineKeyboardMarkup()

    key_physics = types.InlineKeyboardButton(text='Физика', callback_data='physics_reg')
    keyboard.add(key_physics)
    key_chemistry = types.InlineKeyboardButton(text='Химия', callback_data='chemistry_reg')
    keyboard.add(key_chemistry)
    key_chemistry_f = types.InlineKeyboardButton(text='Химия - Физхимия', callback_data='chemistry_f_reg')
    keyboard.add(key_chemistry_f)
    key_chemistry_nf = types.InlineKeyboardButton(text='Химия - Нефтехимия', callback_data='chemistry_nf_reg')
    keyboard.add(key_chemistry_nf)
    key_chemistry_o = types.InlineKeyboardButton(text='Химия - Органика', callback_data='chemistry_o_reg')
    keyboard.add(key_chemistry_o)
    key_economy = types.InlineKeyboardButton(text='Экономика', callback_data='economy_reg')
    keyboard.add(key_economy)
    key_management = types.InlineKeyboardButton(text='Менеджмент', callback_data='management_reg')
    keyboard.add(key_management)
    key_psy = types.InlineKeyboardButton(text='Психология', callback_data='psychology_reg')
    keyboard.add(key_psy)
    key_math = types.InlineKeyboardButton(text='Математика и компьютерные науки', callback_data='math_reg')
    keyboard.add(key_math)
    key_rus_fil = types.InlineKeyboardButton(text='Филология - Русское отделение', callback_data='rus_fil_reg')
    keyboard.add(key_rus_fil)
    key_rus_fr = types.InlineKeyboardButton(text='Филология - Французское отделение', callback_data='rus_fr_reg')
    keyboard.add(key_rus_fr)
    key_rus_eng = types.InlineKeyboardButton(text='Филология - Английское отделение', callback_data='rus_eng_reg')
    keyboard.add(key_rus_eng)
    key_rus_italy = types.InlineKeyboardButton(text='Филология - Итальянское отделение', callback_data='rus_italy_reg')
    keyboard.add(key_rus_italy)
    key_rus_isp = types.InlineKeyboardButton(text='Филология - Испанское отделение', callback_data='rus_isp_reg')
    keyboard.add(key_rus_isp)

    key_mag = types.InlineKeyboardButton(text='МАГИСТРАТУРА', callback_data='mag_reg')
    keyboard.add(key_mag)

    return keyboard


def reg_s_buttons():
    keyboard = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(text='1', callback_data='1_r')
    keyboard.add(key_1)
    key_2 = types.InlineKeyboardButton(text='2', callback_data='2_r')
    keyboard.add(key_2)
    key_3 = types.InlineKeyboardButton(text='3', callback_data='3_r')
    keyboard.add(key_3)
    key_4 = types.InlineKeyboardButton(text='4', callback_data='4_r')
    keyboard.add(key_4)

    return keyboard


def mag_buttons():
    keyboard_m = types.InlineKeyboardMarkup()

    key_physics_m = types.InlineKeyboardButton(text='Физика М.', callback_data='physics_m')
    keyboard_m.add(key_physics_m)
    key_physics_n_m = types.InlineKeyboardButton(text='Физика - Физика наночастиц  М.', callback_data='physics_n_m')
    keyboard_m.add(key_physics_n_m)
    key_physics_bs_m = types.InlineKeyboardButton(text='Физика - Физика биол. систем  М.', callback_data='phy_bs_m')
    keyboard_m.add(key_physics_bs_m)
    key_chemistry_m = types.InlineKeyboardButton(text='Химия М.', callback_data='chemistry_m')
    keyboard_m.add(key_chemistry_m)
    key_chemistry_f_m = types.InlineKeyboardButton(text='Химия - Физическая химия М.', callback_data='chem_f_m')
    keyboard_m.add(key_chemistry_f_m)
    key_chemistry_nf_m = types.InlineKeyboardButton(text='Химия - Нефтехимия М.', callback_data='chemistry_nf_m')
    keyboard_m.add(key_chemistry_nf_m)
    key_chemistry_o_m = types.InlineKeyboardButton(text='Химия - Органическая химия М.', callback_data='chem_o_m')
    keyboard_m.add(key_chemistry_o_m)
    key_management_m = types.InlineKeyboardButton(text='Менеджмент М.', callback_data='management_m')
    keyboard_m.add(key_management_m)
    key_psy_kpr_m = types.InlineKeyboardButton(text='Психология М - КП реабилитация', callback_data='psy_kpr_m')
    keyboard_m.add(key_psy_kpr_m)
    key_psy_s_m = types.InlineKeyboardButton(text='Психология М. - Соц. психология', callback_data='psychology_s_m')
    keyboard_m.add(key_psy_s_m)
    key_psy_r_m = types.InlineKeyboardButton(text='Психология М. - Психология развития', callback_data='psy_r_m')
    keyboard_m.add(key_psy_r_m)
    key_math_m = types.InlineKeyboardButton(text='Математика и компьютерные науки М.', callback_data='math_m')
    keyboard_m.add(key_math_m)
    key_rus_fil_m = types.InlineKeyboardButton(text='Филология  - Русское отделение М.', callback_data='rus_fil_m')
    keyboard_m.add(key_rus_fil_m)
    key_rus_fr_m = types.InlineKeyboardButton(text='Филология - Французское отделение М.', callback_data='rus_fr_m')
    keyboard_m.add(key_rus_fr_m)
    key_rus_eng_m = types.InlineKeyboardButton(text='Филология - Английское отделение М.', callback_data='ru_eng_m')
    keyboard_m.add(key_rus_eng_m)
    key_rus_ita_m = types.InlineKeyboardButton(text='Филология - Итальянское отделение М.', callback_data='ru_it_m')
    keyboard_m.add(key_rus_ita_m)
    key_rus_isp_m = types.InlineKeyboardButton(text='Филология - Испанское отделение М.', callback_data='rus_isp_m')
    keyboard_m.add(key_rus_isp_m)

    return keyboard_m


def mag_reg_buttons():
    keyboard_m = types.InlineKeyboardMarkup()

    key_physics_m = types.InlineKeyboardButton(text='Физика М.', callback_data='physics_m_reg')
    keyboard_m.add(key_physics_m)
    key_physics_n_m = types.InlineKeyboardButton(text='Физика - Физика наночастиц  М.', callback_data='physics_n_m_reg')
    keyboard_m.add(key_physics_n_m)
    key_physics_bs_m = types.InlineKeyboardButton(text='Физика - Физика биол. систем  М.', callback_data='phy_bs_m_reg')
    keyboard_m.add(key_physics_bs_m)
    key_chemistry_m = types.InlineKeyboardButton(text='Химия М.', callback_data='chemistry_m_reg')
    keyboard_m.add(key_chemistry_m)
    key_chemistry_f_m = types.InlineKeyboardButton(text='Химия - Физическая химия М.', callback_data='chem_f_m_reg')
    keyboard_m.add(key_chemistry_f_m)
    key_chemistry_nf_m = types.InlineKeyboardButton(text='Химия - Нефтехимия М.', callback_data='chemistry_nf_m_reg')
    keyboard_m.add(key_chemistry_nf_m)
    key_chemistry_o_m = types.InlineKeyboardButton(text='Химия - Органическая химия М.', callback_data='chem_o_m_reg')
    keyboard_m.add(key_chemistry_o_m)
    key_management_m = types.InlineKeyboardButton(text='Менеджмент М.', callback_data='management_m_reg')
    keyboard_m.add(key_management_m)
    key_psy_kpr_m = types.InlineKeyboardButton(text='Психология М - КП реабилитация', callback_data='psy_kpr_m_reg')
    keyboard_m.add(key_psy_kpr_m)
    key_psy_s_m = types.InlineKeyboardButton(text='Психология М. - Соц. психология', callback_data='psychology_s_m_reg')
    keyboard_m.add(key_psy_s_m)
    key_psy_r_m = types.InlineKeyboardButton(text='Психология М. - Психология развития', callback_data='psy_r_m_reg')
    keyboard_m.add(key_psy_r_m)
    key_math_m = types.InlineKeyboardButton(text='Математика и компьютерные науки М.', callback_data='math_m_reg')
    keyboard_m.add(key_math_m)
    key_rus_fil_m = types.InlineKeyboardButton(text='Филология  - Русское отделение М.', callback_data='rus_fil_m_reg')
    keyboard_m.add(key_rus_fil_m)
    key_rus_fr_m = types.InlineKeyboardButton(text='Филология - Французское отделение М.', callback_data='rus_fr_m_reg')
    keyboard_m.add(key_rus_fr_m)
    key_rus_eng_m = types.InlineKeyboardButton(text='Филология - Английское отделение М.', callback_data='ru_eng_m_reg')
    keyboard_m.add(key_rus_eng_m)
    key_rus_ita_m = types.InlineKeyboardButton(text='Филология - Итальянское отделение М.', callback_data='ru_it_m_reg')
    keyboard_m.add(key_rus_ita_m)
    key_rus_isp_m = types.InlineKeyboardButton(text='Филология - Испанское отделение М.', callback_data='rus_isp_m_reg')
    keyboard_m.add(key_rus_isp_m)

    return keyboard_m

def spec_plan_buttons():
    keyboard_spec = types.InlineKeyboardMarkup()
    for n in config.specialties:
        key_spec = types.InlineKeyboardButton(text=config.specialties[n], callback_data=config.specialties[n])
        keyboard_spec.add(key_spec)

    return keyboard_spec


@logger.catch
def show_week(list_):
    keyboard = types.InlineKeyboardMarkup()

    if len(list_) == 1 and list_[0] == '- - -':
        key_error = types.InlineKeyboardButton(text="Список пуст", callback_data="list_error")
        keyboard.add(key_error)
        logger.warning("Empty list...")

    else:
        if "/" in list_[1]:
            for n in range(len(list_[1:])):
                years = list_[1:]
                key_year = types.InlineKeyboardButton(text=(years[n]), callback_data=years[n])
                keyboard.add(key_year)
            return keyboard
        else:
            for n in range(len(list_[1:])):
                weeks_ = list_[1:]
                if compare_date(get_date(weeks_[n])):
                    key_week = types.InlineKeyboardButton(text=("➡ " + weeks_[n] + " ⬅"), callback_data=weeks_[n])

                else:
                    key_week = types.InlineKeyboardButton(text=("❌ " + weeks_[n] + " ❌"), callback_data=weeks_[n])

                keyboard.add(key_week)

    return keyboard


@logger.catch
def scheduled_dispatch(bot):
    bot.send_message(config.developer_id, "Analytics for today:\n" +
                     str(new_user) + " New User\n" +
                     str(new_registration) + " New Registration\n" +
                     str(bot_call) + " Bot Calls\n" +
                     str(successfully_sent) + " Successfully sent")
    bot.send_document(config.developer_id, open(r"log.txt", 'rb'))
    if new_user or new_registration > 0:
        bot.send_document(config.developer_id, open(r"data.db", 'rb'))
        bot.send_document(config.developer_id, open(r"users.db", 'rb'))
    logger.info("Analytics for today were automatic sent to developer\n" +
                str(new_user) + " New User, " + str(new_registration) + " New Registration, "
                + str(bot_call) + " Bot Calls, " + str(successfully_sent) + " Successfully sent")


@logger.catch
def timeout_func(bot, parser_, message_, message_id_, on_air):
    time.sleep(config.standby)
    if parser_.driver is not None:
        try:
            bot.edit_message_text(chat_id=message_.chat.id, message_id=message_id_,
                                  text='Время ожидания истекло.\n'
                                       'Повторите попытку.')
        except Exception:
            pass
        parser_.exit()
        on_air[0] = False
        logger.info("Standby time is out, exiting the thread and closing the browser...\n")
