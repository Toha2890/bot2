import config
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sq
from bs4 import BeautifulSoup

bot = Bot(token=config.token)
dp = Dispatcher(bot)

personal_area_button = KeyboardButton('Данні особистого кабінету')
internet_tariffs_button = KeyboardButton('Тарифи та послуги за інтернет')
tv_tariffs_button = KeyboardButton('Тарифи за телебачення')
close_area = KeyboardButton('Вийти з особистого кабінету')

unauthorized_users_keyboard = (ReplyKeyboardMarkup(resize_keyboard=True).row(
    internet_tariffs_button, tv_tariffs_button
).add(personal_area_button))
authorized_user_keyboard = (ReplyKeyboardMarkup(resize_keyboard=True).row(internet_tariffs_button, tv_tariffs_button)
).add(close_area)

def adding_to_db(id, log, pas):
    try:
        sqlite_connection = sq.connect('users.db')
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                login STRING,
                password STRING)""")
        sqlite_insert_with_param = """INSERT INTO users
                              (tg_id, login, password)
                              VALUES (?, ?, ?);"""

        data_tuple = (id, log, pas)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        print("Переменные Python успешно вставлены в таблицу")

        cursor.close()

    except sq.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

def delete_on_db(tg_id):
    sqlite_connection = sq.connect('users.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("DELETE FROM users WHERE tg_id=?", (tg_id,))
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()