import telebot

botTimeWeb = telebot.TeleBot('7278832191:AAEf5wP3WvW9jEGUDaVwGMu1PhrTn1g1Zpc')

from telebot import types


@botTimeWeb.message_handler(commands=['start'])
def startBot(message):
    first_mess = (f"<b>{message.from_user.first_name}</b>, привет!"
                  f"\nХочешь узнать что-то новое?")
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text = 'Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text = 'Нет', callback_data='no')
    button_idkn = types.InlineKeyboardButton(text = 'Я не знаю', callback_data='i dont know')
    button_echo = types.InlineKeyboardButton(text = 'Эхо-бот', callback_data='echo-bot')
    markup.add(button_yes, button_no, button_idkn, button_echo)
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
        elif function_call.data == "i dont know":
            second_mess = "Тогда подумай и нажит на кнопку!"
            botTimeWeb.send_message(function_call.message.chat.id, second_mess)
        elif function_call.data == "echo-bot":
            second_mess = "Тогда напиши мне что-нибудь!"
            botTimeWeb.send_message(function_call.message.chat.id, second_mess)
            botTimeWeb.register_next_step_handler(function_call.message, echo)

def echo(message):
    try:
        mess = message.text
        botTimeWeb.send_message(message.chat.id, mess)
        botTimeWeb.register_next_step_handler(message, echo)
    except:
        botTimeWeb.send_message(message.chat.id, "Ты чего-то не понял!")
        botTimeWeb.register_next_step_handler(message, echo)



botTimeWeb.infinity_polling()