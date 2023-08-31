from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import config
import buton
import logging
import hashlib
import requests
import sqlite3 as sq
from bs4 import BeautifulSoup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.token)
storage = MemoryStorage()
dp = Dispatcher(bot,
                storage=storage)

class Data(StatesGroup):
    login = State()
    password = State()

@dp.message_handler(commands=['start'])
async def process_hi3_command(message: types.Message):
    await message.answer("Привіт! "
                        "\nЯ бот интернет провайдеру Flynet. У майбутньому тут буде більше тексту, поки і так вистачить)"
                        "\nP.s. на усіх кнопках знизу будуть смайли(без них не так весело)", reply_markup=buton.unauthorized_users_keyboard)
@dp.message_handler(Text("Тарифи та послуги за інтернет"))
async def with_puree(message: types.Message):
    await message.answer("Перший тариф 200грн 100 мбіт/с\n"
                         "Другий тариф n грн n мбіт/с\n"
                         "Третій тариф .......\n"
                         "Статичний айпі(білий) - 50грн на місяць\n"
                         "Зняття коштів за інтернет  проводиться в ніч з 9го по 10те число кожного місяця\n")
@dp.message_handler(Text("Тарифи за телебачення"))
async def with_puree(message: types.Message):
    await message.answer("Перший тариф 70грн - 147 каналів\n"
                         "Другий тариф 80грн - 160+- каналів\n"
                         "Третій тариф 100грн - 207 каналів\n"
                         "Сплата за телебачення - першого числа")

@dp.message_handler(Text("Данні особистого кабінету"))
async def user_register(message: types.Message):
    sqlite_connection = sq.connect('users.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("SELECT * FROM users")
    temp =False
    pas_temp = ""
    log_temp = ""
    for user in cursor.fetchall():
        if user[1] == message.from_user.id:
            temp = True
            pas_temp = user[3]
            log_temp = user[2]
            break
    cursor.close()
    sqlite_connection.close()
    if temp == True:
        link = f"http://demo.ubilling.net.ua:9999/billing/userstats/?xmlagent=true&uberlogin={log_temp}&uberpassword={pas_temp}"
        response = requests.get(link).text
        soup = BeautifulSoup(response, 'lxml')
        adress = soup.address
        realname = soup.realname
        cash = soup.cash
        payid = soup.payid
        tariff = soup.tariff
        accountstate = soup.accountstate
        credit = soup.credit
        login = soup.login
        mobile = soup.mobile
        await message.answer(f"Ласкаво просимо, {realname.text}!\n"
                                f"адреса: {adress.text}\n"
                                f"Ваш логін від особистого кабінету: {login.text}\n"
                                f"Ваш пароль від особистого кабінету: {mobile.text}\n"
                                f"Ваш тариф: {tariff.text}\n"
                                f"Ваш баланс: {cash.text}грн\n"
                                f"Ваш кредит: {credit.text}грн\n"
                                f"Ваш рахунок: {accountstate.text}\n"
                                f"Ваш платіжний ID: {payid.text}", reply_markup = buton.authorized_user_keyboard)
    else:
        await message.answer("Введіть логін")
        await Data.login.set()
@dp.message_handler(state=Data.login)
async def get_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введіть пароль: ")
    await Data.next() # либо же UserState.address.set()
@dp.message_handler(state=Data.password)
async def get_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    pas = data['password']
    hash_pass = hashlib.md5(pas.encode())
    link = f"http://demo.ubilling.net.ua:9999/billing/userstats/?xmlagent=true&uberlogin={data['login']}&uberpassword={hash_pass.hexdigest()}"
    response = requests.get(link).text
    soup = BeautifulSoup(response, 'lxml')
    if soup.body.text == "ERROR_WRONG_UBERAUTH":
        await message.answer(
            "Перевірте правильність данних та спробуйте ще раз."
            "\nЯкщо ви забули данні особистого кабінету - зателефонуйте на тех.підтримку)")
        await state.finish()
    else:
        buton.adding_to_db(message.from_user.id, data['login'], hash_pass.hexdigest())
        adress = soup.address
        realname = soup.realname
        cash = soup.cash
        payid = soup.payid
        tariff = soup.tariff
        accountstate = soup.accountstate
        credit = soup.credit
        login = soup.login
        mobile = soup.mobile
        await message.answer(f"Ласкаво просимо, {realname.text}!\n"
                                f"адреса: {adress.text}\n"
                                f"Ваш логін від особистого кабінету: {login.text}\n"
                                f"Ваш пароль від особистого кабінету: {mobile.text}\n"
                                f"Ваш тариф: {tariff.text}\n"
                                f"Ваш баланс: {cash.text}грн\n"
                                f"Ваш кредит: {credit.text}грн\n"
                                f"Ваш рахунок: {accountstate.text}\n"
                                f"Ваш платіжний ID: {payid.text}")
        await state.finish()

@dp.message_handler(Text("Вийти з особистого кабінету"))
async def close(message: types.Message):
    buton.delete_on_db(message.from_user.id)
    await message.answer("Ви успішно вийшли з особистого кабінету", reply_markup = buton.unauthorized_users_keyboard)

@dp.message_handler(commands=['sendall'])
async def send_message(message: types.Message):
    if message.from_user.id == 634254008:
        sqlite_connection = sq.connect('users.db')
        cursor = sqlite_connection.cursor()
        cursor.execute("SELECT * FROM users")
        text = message.text[9:]
        for user in cursor.fetchall():
            try:
                await bot.send_message(user[1], text)
            except:
                pass
        cursor.close()
        sqlite_connection.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)