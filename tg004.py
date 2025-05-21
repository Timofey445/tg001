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

# Настройка базового журнала для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение базы данных SQLite
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

# Токен API Телеграм бота (используйте ваш собственный токен!)
API_TOKEN = '7879932904:AAEMNBlZ-M5cMSjuG5Wgg9jRm-ZESfjrfq0'

# Инициализация объекта бота и роутера
bot = Bot(token=API_TOKEN)
router = Router()

# Медиафайлы (пример изображений и аудиофайлов)
audio_file_path = "./music/welcome.mp3"

# Функция отправки приветственного сообщения с клавиатурой
@router.message(CommandStart())
async def start_command(message: Message):
    # Создание кнопочной панели с командами
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

    # Отправляем сообщение с мультимедиа-файлами
    pass

    await message.answer("Привет! Я твой помощник.\n"
                         "Используй кнопки ниже для навигации.",
                         reply_markup=keyboard)

# Команда помощи с описанием функций
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

# Обработка выражения с Sympy
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

# Получаем список всех задач
@router.message(F.text.startswith('/tasklist'))
async def task_list(message: Message):
    cursor.execute("SELECT * FROM tasks ORDER BY deadline ASC;")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("У вас пока нет активных задач.")
    else:
        output = '\n'.join([f'{row[0]}. {row[1]} (Срок: {row[2]})' for row in rows])
        await message.answer(f"<b>Список ваших задач:</b>\n{output}", parse_mode='HTML')

# Добавляем новую задачу
@router.message(F.text.startswith('/add_task'))
async def add_task(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3 or not parts[2]:
        await message.answer("Формат добавления задачи неправильный.\nПример: /add_task Название_задачи Дата")
        return

    task_name = parts[1]
    deadline = parts[2]

    # Пробуем вывести полученные значения для анализа
    await message.answer(f"Название задачи: {task_name}, Срок: {deadline}")

    try:
        date_obj = datetime.strptime(deadline, "%Y-%m-%d").date()
        cursor.execute("INSERT INTO tasks(task, deadline) VALUES (?, ?)", (task_name, str(date_obj)))
        conn.commit()
        await message.answer(f"Твоя задача \"{task_name}\" успешно добавлена на {deadline}.")
    except ValueError as e:
        await message.answer(f"Некорректная дата: {e}. Используйте формат ГГГГ-ММ-ДД.")


# Удаляем задачу по её идентификатору
@router.message(F.text.startswith('/delete_task'))
async def delete_task(message: Message):
    try:
        task_id = int(message.text.split()[1])
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        await message.answer(f"Задача #{task_id} была успешно удалена.")
    except (ValueError, IndexError):
        await message.answer("Неправильный формат удаления задачи. Пример: /delete_task 1")

# Загрузка файла
@router.message(F.text.contains("📎"))
async def upload_files(message: Message):
    await message.answer("Отправьте файл для сохранения.")

# Прием и обработка входящего документа
@router.message(F.content_type == types.ContentType.DOCUMENT)
async def handle_document(message: Message):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    # Имя файла и местоположение для сохранения
    filename = message.document.file_name
    path_to_save = os.path.join('./uploads/', filename)

    # Проверяем, существует ли директория для сохранения файлов
    if not os.path.exists("./uploads/"):
        os.makedirs("./uploads/")

    # Сохраняем полученный файл локально
    with open(path_to_save, 'wb') as new_file:
        new_file.write(downloaded_file.read())

    await message.reply(f"Файл сохранён как {filename}")
# Отправка звукового файла
@router.message(F.text.contains("♫️"))
async def send_audio(message: Message):
    audio = FSInputFile(audio_file_path)
    await bot.send_audio(chat_id=message.chat.id, audio=audio)

# Регистрация обработчиков
dp = Dispatcher()
dp.include_router(router)

# Запуск бот-пуллинга
if __name__ == "__main__":
    async def main():
        try:
            # Удаляем любые действующие вебхуки
            await bot.delete_webhook(drop_pending_updates=True)

            # Запускаем процесс поллинга
            async with bot:
                await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("Прервано пользователем.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    # Запуск главного корутина с помощью asyncio.run()
    asyncio.run(main())