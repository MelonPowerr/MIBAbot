from telebot import types
import os
import json


def read_schools_from_file():
    val_arr = []
    with open('schools.json', 'r') as file:
        data = json.load(file)
    for item in data:
        val_arr.append(item['value'])
    return val_arr


def work_for_create_inline_keyboard():
    val_arr = read_schools_from_file()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for value in val_arr:
        button = types.InlineKeyboardButton(text=value, callback_data=value)
        keyboard.add(button)
    return keyboard


def subject_create_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Химия', callback_data='Химия')
    button2 = types.InlineKeyboardButton(text='Математика', callback_data='Математика')
    keyboard.add(button1, button2)
    return keyboard


def save_data_to_file(chat_id, username, work_for, subject):
    file_name = "data.json"
    data = {
        "id": chat_id,
        "username": username,
        "work_for": work_for,
        "subject": subject
    }
    if not os.path.isfile(file_name):
        with open(file_name, 'w') as file:
            file.write('[]')
    # Загрузка существующих данных из файла, если они есть
    with open(file_name, 'r', encoding='utf-8') as file:
        try:
            existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = []

    # Проверка на наличие записи с таким же username
    for i, entry in enumerate(existing_data):
        if entry['id'] == chat_id:
            # Замена записи с таким же username
            existing_data[i] = data
            break
    else:
        # Если совпадение не найдено, добавляем новую запись
        existing_data.append(data)

    # Запись обновленных данных обратно в файл
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)


def class_create_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    button1 = types.InlineKeyboardButton(text='8', callback_data='8 класс')
    button2 = types.InlineKeyboardButton(text='9', callback_data='9 класс')
    button3 = types.InlineKeyboardButton(text='10', callback_data='10 класс')
    button4 = types.InlineKeyboardButton(text='11', callback_data='11 класс')
    keyboard.add(button1, button2, button3, button4)
    return keyboard


def confirmation_create_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(button_yes, button_no)
    return keyboard


def find_user_by_username(chat_id):
    file_name = 'data.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    for user_data in data:
        if user_data['id'] == chat_id:
            work_for = user_data['work_for']
            subject = user_data['subject']
            return work_for, subject

    return None, None
