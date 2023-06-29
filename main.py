import multiprocessing
import time
import telebot
from dotenv import load_dotenv
from telegram_bot_calendar import DetailedTelegramCalendar
from external_funcs import *

# ПОДГРУЗКА ТОКЕНОВ
###################################
load_dotenv()
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)
###################################

# ВРЕМЕННОЕ ХРАНЕНИЕ ДАННЫХ
###################################
temp_user = {}
index_amount = 10
msg_index = 0
work_for_index = 1
subj_index = 2
class_index = 3
date_index = 4
theme_index = 5
photo_count_index = 6


###################################
@bot.message_handler(commands=['start'])
def hello_msg(message):
    temp_user[message.chat.id] = [None] * index_amount
    msg = f"Здравствуйте!\n" \
          f"Где вы преподаете?"
    msg_save = bot.send_message(chat_id=message.chat.id, text=msg)
    temp_user[message.chat.id][msg_index] = msg_save.message_id
    work_for_msg(message)


def work_for_msg(message):
    chat_id = message.chat.id
    try:
        keyboard = work_for_create_inline_keyboard()
        msg = f"Здравствуйте!\n" \
              f"Где вы преподаете?"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg, reply_markup=keyboard)
    except Exception:
        hello_msg(message)


@bot.callback_query_handler(func=lambda call: call.data in read_schools_from_file())
def handle_work_for_button_click(call):
    chat_id = call.message.chat.id
    try:
        temp_user[chat_id][work_for_index] = call.data
        keyboard = subject_create_inline_keyboard()
        msg = f"Место работы: {call.data}\n" \
              f"Какой предмет вы преподаете?"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg, reply_markup=keyboard)
    except KeyError:
        hello_msg(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ['Химия', 'Математика'])
def handle_subject_button_click(call):
    chat_id = call.message.chat.id
    try:
        temp_user[chat_id][subj_index] = call.data

        chat = chat_id
        username = call.from_user.username
        work_for = temp_user[chat_id][work_for_index]
        subject = temp_user[chat_id][subj_index]

        save_data_to_file(chat, username, work_for, subject)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_yes = types.InlineKeyboardButton(text='Да', callback_data='confirm')
        button_no = types.InlineKeyboardButton(text='Нет', callback_data='reject')
        keyboard.add(button_yes, button_no)

        msg = f"Ваше место работы: {temp_user[chat_id][work_for_index]}\n" \
              f"Ваш предмет: {temp_user[chat_id][subj_index]}\n" \
              f"Все верно?"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg, reply_markup=keyboard)
    except KeyError:
        work_for_msg(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ['confirm', 'reject'])
def handle_confirmation_button_click(call):
    chat_id = call.message.chat.id

    if call.data == 'confirm':
        msg = f"Регистрация окончена. Приятно познакомиться!"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg)
    elif call.data == 'reject':
        work_for_msg(call.message)


@bot.message_handler(commands=['report'])
def report_start(message):
    work, subj = find_user_by_username(message.chat.id)
    if work is not None and subj is not None:
        temp_user[message.chat.id] = [None] * index_amount
        msg = f"У какого класса было проведено занятие?"
        msg_save = bot.send_message(chat_id=message.chat.id, text=msg)
        temp_user[message.chat.id][msg_index] = msg_save.message_id
        class_select(message)
    else:
        hello_msg(message)


def class_select(message):
    chat_id = message.chat.id
    try:
        keyboard = class_create_inline_keyboard()
        msg = f"У какого класса было проведено занятие?"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg, reply_markup=keyboard)
    except KeyError:
        report_start(message)


@bot.callback_query_handler(func=lambda call: call.data in ['8 класс', '9 класс', '10 класс', '11 класс'])
def handle_class_select_button_click(call):
    chat_id = call.message.chat.id
    try:
        temp_user[chat_id][class_index] = call.data
        calendar, step = DetailedTelegramCalendar().build()
        msg = f"Занятие проведено у {call.data}а\n" \
              f"Укажите дату проведенного занятия"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index],
                              text=msg, reply_markup=calendar)
    except Exception:
        class_select(call.message)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(call):
    chat_id = call.message.chat.id
    try:
        result, key, step = DetailedTelegramCalendar().process(call.data)
        if not result and key:
            bot.edit_message_text(f"Укажите дату проведенного занятия", call.message.chat.id,
                                  temp_user[chat_id][msg_index],
                                  reply_markup=key)
        elif result:
            try:
                temp_user[chat_id][date_index] = str(result)
                theme_input(call.message)
                # msg = f"{result} было проведено занятие у {temp_user[chat_id][class_index]}а\n" \
                #       f"Впишите номер темы занятия"
                # temp_user[chat_id][date_index] = str(result)
                # bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=msg)
                #
                # print(temp_user[chat_id])
                #
                # bot.register_next_step_handler(call.message, handle_theme_input)
            except KeyError:
                report_start(call.message)

    except telebot.apihelper.ApiTelegramException:
        msg = f"Спам алерт!"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)
        time.sleep(2)
        class_select(call.message)


def theme_input(message):
    chat_id = message.chat.id

    msg = f"{temp_user[chat_id][date_index]} было проведено занятие у {temp_user[chat_id][class_index]}а\n" \
          f"Впишите тему в формате 'номер:название темы'"
    bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)

    print(temp_user[chat_id])

    bot.register_next_step_handler(message, handle_theme_input)


# def handle_theme_input(message):
#     chat_id = message.chat.id
#     try:
#         temp_user[chat_id][theme_index] = message.text
#
#         print(temp_user[chat_id])
#
#         bot.delete_message(chat_id=chat_id, message_id=message.message_id)
#         msg = f"{temp_user[chat_id][date_index]} было проведено занятие у {temp_user[chat_id][class_index]}а\n" \
#               f"Номер темы занятия: {temp_user[chat_id][theme_index]}\n" \
#               f"Верно?"
#         keyboard = confirmation_create_inline_keyboard()
#         bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg,
#                               reply_markup=keyboard)
#     except Exception:
#         class_select(message)
def handle_theme_input(message):
    chat_id = message.chat.id
    try:
        parts = message.text.split(':', 1)
        parts[0] = parts[0].strip()
        if len(parts) == 2 and parts[0].isdigit():
            temp_user[chat_id][theme_index] = message.text

            print(temp_user[chat_id])

            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            msg = f"{temp_user[chat_id][date_index]} было проведено занятие у {temp_user[chat_id][class_index]}а\n" \
                  f"Тема: {temp_user[chat_id][theme_index]}\n" \
                  f"Верно?"
            keyboard = confirmation_create_inline_keyboard()
            bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg,
                                  reply_markup=keyboard)
        else:
            msg = f"Тема введена неправильно...\n"
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)
            time.sleep(0.5)
            theme_input(message)

    except Exception:
        class_select(message)


@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
def handle_YesOrNo_button_click(call):
    chat_id = call.message.chat.id
    try:
        if call.data == 'yes':
            msg = f"Класс: {temp_user[chat_id][class_index]}\n" \
                  f"Дата: {temp_user[chat_id][date_index]}\n" \
                  f"Тема: {temp_user[chat_id][theme_index]}\n" \
                  f"Прикрепите пожалуйста фотоотчет"
            bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)
            bot.register_next_step_handler(call.message, handle_photo_input)

            temp_user[chat_id][photo_count_index] = 0
            print(temp_user[chat_id])

        elif call.data == 'no':
            class_select(call.message)
    except Exception:
        class_select(call.message)


from ya_test import *


@bot.message_handler(content_types=['photo', 'document'])
def handle_photo_input(message):
    mendeleev_disk_path = ""

    chat_id = message.chat.id

    work_for, subject = find_user_by_username(chat_id)

    save_folder = f"Отчеты/{work_for}/{subject}/{temp_user[chat_id][class_index]}/{temp_user[chat_id][theme_index]}/"
    os.makedirs(save_folder, exist_ok=True)

    # disk_save_folder = mendeleev_disk_path + save_folder
    # if disk_save_folder[0] == '/':
    #     disk_save_folder = disk_save_folder[1:]
    # ya_create_folder_tree(disk_save_folder)

    try:
        if message.content_type == 'photo' and temp_user[chat_id][theme_index] is not None:
            # Обработка фотографии
            max_width = 0
            max_height = 0
            max_photo = None

            for photo in message.photo:
                if photo.width > max_width and photo.height > max_height:
                    max_width = photo.width
                    max_height = photo.height
                    max_photo = photo

            if max_photo is not None:
                file_name = f"{temp_user[chat_id][date_index]}_{message.message_id}.jpg"
                file_path = os.path.join(save_folder, file_name)

                file_info = bot.get_file(max_photo.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open(file_path, 'wb') as file:
                    file.write(downloaded_file)
                    # выгрузка на Ядиск жутко тормозит процесс обработки тут или оставить как есть или разбираться с
                    # асинхронной библиотекой или раз в определенное время синхронизировать папку локальной с
                    # яндексовской, но тогда может быть большая нагрузка единомоментно или с помощью subprocess
                    # запустить фоновый файл, который раз в сколько-то времени сканит папку и синхронизирует ее

                    # disk_file_path = os.path.join(disk_save_folder, file_name)
                    # ya_upload(file_path, disk_file_path)
                    # save_process = multiprocessing.Process(target=ya_upload(file_path, disk_file_path))
                    # save_process.start()
                    # save_process.join()

                    print(f"{message.from_user.username} - Прикрепил фотографию: {file_path}")
                    temp_user[chat_id][photo_count_index] += 1

                    msg = f"Фотографии приняты!\nБлагодарим за кооперацию (+{temp_user[chat_id][photo_count_index]})"
                    bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)

        elif message.content_type == 'document' and temp_user[chat_id][theme_index] is not None:
            # Обработка документа

            file_name = f"{temp_user[chat_id][date_index]}_{message.message_id}_{message.document.file_name}"
            file_path = os.path.join(save_folder, file_name)

            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_path, 'wb') as file:
                file.write(downloaded_file)
                print(f"{message.from_user.username} - Прикрепил документ: {file_path}")
                temp_user[chat_id][photo_count_index] += 1

            msg = f"Фотографии приняты!\n" \
                  f"Благодарим за кооперацию (+{temp_user[chat_id][photo_count_index]})"
            bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)

    except TypeError or AttributeError:
        msg = "Что-то пошло не так... Начнем сначала"
        bot.edit_message_text(chat_id=chat_id, message_id=temp_user[chat_id][msg_index], text=msg)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        time.sleep(1)
        class_select(message)
    except KeyError:
        report_start(message)
    except Exception:
        report_start(message)


@bot.message_handler(commands=['help'])
def help_msg(message):
    msg = f"Тут будет справка че делает бот и зачем\n" \
          f"/help справка о доступных командах и возможностях бота\n" \
          f"/useful  полезные материалы\n" \
          "/report отправка отчета\n"
    bot.send_message(chat_id=message.chat.id, text=msg)


@bot.message_handler(commands=['useful'])
def useful_msg(message):
    # todo сюда нужно будет засунуть ссылки и чтобы они были разными в зависимости от chatid
    msg = f"Тут будут полезные ссылки\n"
    bot.send_message(chat_id=message.chat.id, text=msg)


while True:
    try:
        bot.polling(none_stop=True)
    except:
        print('сдох')
        time.sleep(3)
