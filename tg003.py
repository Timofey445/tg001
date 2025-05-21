from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import os
import asyncio
import sympy as sp


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


API_TOKEN = '7879932904:AAEMNBlZ-M5cMSjuG5Wgg9jRm-ZESfjrfq0'


bot = Bot(API_TOKEN)
router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    buttons = [
        KeyboardButton(text="/help"),
        KeyboardButton(text="/math"),
        KeyboardButton(text="/tasklist")
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
    await message.answer("Добро пожаловать в нашего помощника!\n"
                         "/help — справка\n"
                         "/math — решение математических выражений\n"
                         "/tasklist — список задач",
                         reply_markup=keyboard)


@router.message(F.text.lower() == '/help')
async def help_command(message: Message):
    await message.answer("Доступные команды:\n"
                         "/math <выражение> — решить математическое выражение\n"
                         "/tasklist — показать список задач\n"
                         "/add_task <текст задачи> — добавить новую задачу\n"
                         "/delete_task <id> — удалить задачу")


@router.message(F.text.startswith('/math'))
async def math_command(message: Message):
    expression = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else None
    if not expression:
        return await message.answer("Укажите математическое выражение после команды '/math'. Например: `/math x^2 + 2x + 1`")

    result = sp.sympify(expression)
    answer = f"Ваше выражение: {expression}\nРезультат: {result}"
    await message.answer(answer)


@router.message(F.text.in_(["/tasklist", "/add_task", "/delete_task"]))
async def task_commands(message: Message):
    command = message.text.strip()
    args = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""

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


dp = Dispatcher()
dp.include_router(router)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print("Запускаю бота...")
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        print(e)
    finally:
        loop.close()