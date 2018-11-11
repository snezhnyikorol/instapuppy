#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import cherrypy
from config import TOKEN, GROUP_ID


WEBHOOK_HOST = 'puppybot.ddns.net'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше
WEBHOOK_SSL_CERT = '.\webhookinsta_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = '.\webhookinsta_pkey.pem'  # Путь к приватному ключу
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)


bot = telebot.TeleBot(TOKEN)


# Наш вебхук-сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


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


bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',                   #pyopenssl
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})


cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})

# if __name__ == '__main__':
#     main()
