import telebot
from config import TOKEN, GROUP_ID


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda message: message.entities is not None and message.chat.id == GROUP_ID)
def delete_links(message):
    for entity in message.entities:  # Пройдёмся по всем entities в поисках ссылок
        # url - обычная ссылка, text_link - ссылка, скрытая под текстом
        if entity.type in ['url', 'text_link']:
            # Мы можем не проверять chat.id, он проверяется ещё в хэндлере
            bot.delete_message(message.chat.id, message.message_id)
        else:
            return


@bot.message_handler(func=lambda message: message.text == 'hello' and message.chat.id == GROUP_ID)
def repeat_links(message):
    bot.send_message(message.chat.id, 'Hello')


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text == '/start'
                        and message.chat.id != GROUP_ID)
def start(message):
    bot.send_message(message.chat.id, 'Введите свой ник в Instagram: ')


def main():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
