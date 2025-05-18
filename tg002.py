# Универсальный Telegram-бот с двумя основными возможностями:
# 1. Математика (решение уравнений и выражений)
# 2. Организатор задач (добавление и удаление задач)

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import os
import asyncio
import sympy as sp

# Подключаемся к базе данных SQLite
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    deadline DATE DEFAULT NULL
);
''')
conn.commit()

# Настройка API-токена Telegram
API_TOKEN = '7879932904:AAEMNBlZ-M5cMSjuG5Wgg9jRm-ZESfjrfq0'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Здесь больше не передаётся аргумент bot

# Основная команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('/help'),
        KeyboardButton('/math'),
        KeyboardButton('/tasklist')
    )
    await message.answer("Добро пожаловать в нашего помощника!\n"
                         "/help — справка\n"
                         "/math — решение математических выражений\n"
                         "/tasklist — список задач",
                         reply_markup=keyboard)

# Команда помощи
@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("Доступные команды:\n"
                         "/math <выражение> — решить математическое выражение\n"
                         "/tasklist — показать список задач\n"
                         "/add_task <текст задачи> — добавить новую задачу\n"
                         "/delete_task <id> — удалить задачу")

# Решатель математических выражений
@dp.message_handler(commands=['math'])
async def math_command(message: types.Message):
    expression = message.get_args().strip() if len(message.get_args()) > 0 else None
    if not expression:
        return await message.answer("Укажите математическое выражение после команды '/math'. Например: `/math x^2 + 2x + 1`")

    result = sp.sympify(expression)
    answer = f"Ваше выражение: {expression}\nРезультат: {result}"
    await message.answer(answer)

# Управление задачами
@dp.message_handler(commands=['tasklist', 'add_task', 'delete_task'])
async def task_commands(message: types.Message):
    command = message.get_command()
    args = message.get_args().strip()

    if command == '/tasklist':
        cursor.execute("SELECT * FROM tasks;")
        rows = cursor.fetchall()

        if not rows:
            await message.answer("Нет текущих задач!")
        else:
            response = "\n".join([f"{row[0]} | {row[1]} | Срок сдачи: {row[2]}" for row in rows])
            await message.answer(f"Список задач:\n{response}")

    elif command == '/add_task':
        if not args:
            return await message.answer("Напишите задачу после команды '/add_task'")
        cursor.execute("INSERT INTO tasks(task) VALUES (?)", (args,))
        conn.commit()
        await message.answer(f"Задача '{args}' добавлена!")

    elif command == '/delete_task':
        if not args.isdigit():
            return await message.answer("Неверный ID задачи. Убедитесь, что указали число.")
        cursor.execute("DELETE FROM tasks WHERE id=?", (args,))
        conn.commit()
        await message.answer(f"Задача №{args} удалена!")

# Запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        loop.close()