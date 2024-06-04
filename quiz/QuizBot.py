import datetime
from typing import Dict
from .Messages import Messages
from .functions import (
    send_help_message,
    start_new_quiz,
    process_answer,
    check_answer
)

class QuizBot:
    def __init__(self, bot, quiz):
        self.bot = bot
        self.quiz = quiz

    def start(self):
        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            send_help_message(self.bot, message, Messages)

        @self.bot.message_handler(commands=['start'])
        def start_quiz(message):
            start_new_quiz(self, message, Messages)

        @self.bot.callback_query_handler(func=lambda callback: True)
        def handle_button_click(callback):
            process_answer(self, callback)

        self.bot.polling(none_stop=True)

    def process_answer(self, callback):
        process_answer(self, callback)

    def check_answer(self, user_answer, correct_answer):
        return check_answer(self.quiz, user_answer, correct_answer)
