#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from predict_model import Predictor

from skimage.io import imread
import skimage

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

predictor = Predictor("deep_dream_model")

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'Анонимус'
    update.message.reply_text('Hi, {}!'.format(name))


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Ohh, you need my help. Alright.')
    update.message.reply_text('I was made for changing your photo, so send me one and I will
      make it look stranger.
      Also you can tell me, which filter you want me to use.')
    upate.message.reply_text('Also I can make echo, huh')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def action(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Здесь будет экшн')
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def get_photo(update, context):
    """Echo the user message."""
    user = update.message.from_user
    # get photo file
    photo_file = update.message.photo[-1].get_file()
    # save photo
    photo_file = Image.fromarray(skimage.img_as_ubyte(photo_file)).resize((512, 512))
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Gorgeous! Got your photo')
   

    # load saved photo
    new_photo = open('result.jpg', 'w')

    # send photo
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=new_photo)

def main():
    """Start the bot."""
    print('Start')
    updater = Updater("730845793:AAEarTNpZrkhXBZCpTddizfQwKpKTLJSO64", use_context=True)
        # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("action", action))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.photo, get_photo))

    # on noncommand i.e message - echo the message on Telegram
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()
    print('Finish')

if __name__ == '__main__':
    main()
