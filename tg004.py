# @Project_YandexLMS_Bot
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputFile
from aiogram import F, types
from aiogram.types import Message
import sqlite3
import os
import asyncio
import sympy as sp
import logging
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = sqlite3.connect('tasks.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    deadline DATE DEFAULT NULL
);
''')
conn.commit()


class Task:
    def __init__(self, task_id=None, task=None, deadline=None):
        self.task_id = task_id
        self.task = task
        self.deadline = deadline

    @classmethod
    def create(cls, task, deadline):
        """Создает новую запись задачи"""
        cursor.execute("INSERT INTO tasks(task, deadline) VALUES (?, ?)",
                       (task, deadline))
        conn.commit()
        return cls(cursor.lastrowid, task, deadline)

    @classmethod
    def all(cls):
        """Получает все задачи из БД"""
        cursor.execute("SELECT * FROM tasks ORDER BY deadline ASC;")
        rows = cursor.fetchall()
        return [cls(row[0], row[1], row[2]) for row in rows]

    @classmethod
    def find_by_id(cls, task_id):
        """Ищет задачу по ID"""
        cursor.execute("SELECT * FROM tasks WHERE id=?;", (task_id,))
        row = cursor.fetchone()
        if row:
            return cls(row[0], row[1], row[2])
        return None

    def update(self, task=None, deadline=None):
        """Обновляет данные задачи"""
        updates = []
        params = []
        if task is not None:
            updates.append("task=?")
            params.append(task)
        if deadline is not None:
            updates.append("deadline=?")
            params.append(deadline)
        params.append(self.task_id)
        sql_query = f"UPDATE tasks SET {','.join(updates)} WHERE id=?"
        cursor.execute(sql_query, tuple(params))
        conn.commit()

    def delete(self):
        """Удаляет задачу из БД"""
        cursor.execute("DELETE FROM tasks WHERE id=?", (self.task_id,))
        conn.commit()


API_TOKEN = '7879932904:AAEMNBlZ-M5cMSjuG5Wgg9jRm-ZESfjrfq0'

# Инициализация объекта бота и роутера
bot = Bot(token=API_TOKEN)
router = Router()


audio_file_path = "musics/welcome.mp3"


@router.message(CommandStart())
async def start_command(message: Message):
    buttons = [
        KeyboardButton(text="Справка /help"),
        KeyboardButton(text="Математика /math"),
        KeyboardButton(text="Список задач /tasklist"),
        KeyboardButton(text="Загрузить файл 📎"),
        KeyboardButton(text="Прослушать музыку ♫️")
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons],
        resize_keyboard=True
    )


    pass

    await message.answer("Привет! Я твой помощник.\n"
                         "Используй кнопки ниже для навигации.\n"
                         "Используй команду /help, чтобы получить список доступных команд.",
                         reply_markup=keyboard)


@router.message(F.text.contains("/help"))
async def help_command(message: Message):
    await message.answer("Доступные команды:\n"
                         "- Справка (/help)\n"
                         "- Решение математики (/math)\n"
                         "- Список задач (/tasklist)\n"
                         "- Добавление новой задачи (/add_task)\n"
                         "- Удаление задачи (/delete_task)\n"
                         "- Загрузка файлов 📎\n"
                         "- Прослушивание музыки ♫️")


@router.message(F.text.startswith('/math'))
async def math_command(message: Message):
    try:
        expression = message.text.split(maxsplit=1)[1].strip()
        if not expression:
            raise ValueError("Выражение отсутствует")

        result = sp.sympify(expression).evalf()
        await message.answer(f"Решение уравнения `{expression}` равно `{result}`")
    except Exception as err:
        logger.error(err)
        await message.answer("Ошибка вычисления выражения.")


@router.message(F.text.startswith('/tasklist'))
async def task_list(message: Message):
    tasks = Task.all()
    if not tasks:
        await message.answer("У вас пока нет активных задач.")
    else:
        output = '\n'.join([f'{t.task_id}. {t.task} (Срок: {t.deadline})' for t in tasks])
        await message.answer(f"<b>Список ваших задач:</b>\n{output}", parse_mode='HTML')


@router.message(F.text.startswith('/add_task'))
async def add_task(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3 or not parts[2]:
        await message.answer("Формат добавления задачи неправильный.\nПример: /add_task Название_задачи Дата")
        return

    task_name = parts[1]
    deadline = parts[2]


    await message.answer(f"Название задачи: {task_name}, Срок: {deadline}")

    try:
        date_obj = datetime.strptime(deadline, "%Y-%m-%d").date()
        Task.create(task_name, str(date_obj))
        await message.answer(f"Твоя задача \"{task_name}\" успешно добавлена на {deadline}.")
    except ValueError as e:
        await message.answer(f"Некорректная дата: {e}. Используйте формат ГГГГ-ММ-ДД.")


@router.message(F.text.startswith('/delete_task'))
async def delete_task(message: Message):
    try:
        task_id = int(message.text.split()[1])
        task = Task.find_by_id(task_id)
        if task:
            task.delete()
            await message.answer(f"Задача №{task_id}: '{task.task}' была успешно удалена.")
        else:
            await message.answer(f"Задача с номером {task_id} не найдена.")
    except (ValueError, IndexError):
        await message.answer("Неправильный формат удаления задачи. Пример: /delete_task 1")


@router.message(F.text.contains("📎"))
async def upload_files(message: Message):
    await message.answer("Отправьте файл для сохранения.")


@router.message(F.content_type == types.ContentType.DOCUMENT)
async def handle_document(message: Message):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    filename = message.document.file_name
    path_to_save = os.path.join('./uploads/', filename)

    if not os.path.exists("./uploads/"):
        os.makedirs("./uploads/")

    with open(path_to_save, 'wb') as new_file:
        new_file.write(downloaded_file.read())

    await message.reply(f"Файл сохранён как {filename}")


@router.message(F.text.contains("♫️"))
async def send_audio(message: Message):
    audio = FSInputFile(audio_file_path)
    await bot.send_audio(chat_id=message.chat.id, audio=audio)

dp = Dispatcher()
dp.include_router(router)

if __name__ == "__main__":
    async def main():
        try:
            await bot.delete_webhook(drop_pending_updates=True)

            async with bot:
                await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("Прервано пользователем.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    asyncio.run(main())