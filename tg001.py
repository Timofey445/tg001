import telebot

botTimeWeb = telebot.TeleBot('7278832191:AAEf5wP3WvW9jEGUDaVwGMu1PhrTn1g1Zpc')

from telebot import types


@botTimeWeb.message_handler(commands=['start'])
def startBot(message):
    first_mess = (f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!"
                  f"\nХочешь узнать что-то новое?")
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text = 'Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text = 'Нет', callback_data='no')
    markup.add(button_yes, button_no)
    botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)


@botTimeWeb.callback_query_handler(func=lambda call:True)
def response(function_call):
    if function_call.message:
        if function_call.data == "yes":
            second_mess = "Тогда нажимай на кнопку!"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Сюда",
                                                  url="https://youtube.com/watch?v=6_hl8AB7Uf0"))
            botTimeWeb.send_message(function_call.message.chat.id, second_mess, reply_markup=markup)
            botTimeWeb.answer_callback_query(function_call.id)
        elif function_call.data == "no":
            second_mess = "Тогда пошёл отсюда!"
            botTimeWeb.send_message(function_call.message.chat.id, second_mess)


botTimeWeb.infinity_polling()