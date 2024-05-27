import logging
import random
import datetime
import telebot
from telebot import types
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '6668250527:AAFINq_6I0cTjxIfAW51J0NDCKP3fP8zZDA'
QUIZ_LENGTH = 10
QUESTIONS_FILE = 'questions.csv'

bot = telebot.TeleBot(BOT_TOKEN)

bot_messages = {
    'help': {
        'intro': '\nБот складається з 10 питань, кожне з них має 4 варіанти відповіді. '
                 'Після проходження тесту ви дізнаєтесь результат: кількість відповідей та час проходження.',
        'start_quiz': '\t\nРозпочати опитування: /start'
    },
    'start': {
        'intro': "Ну що, готовий перевірити свої знання?\n"
                 "Тема: Python!\n\n",
        'instructions': "Жми /stop щоб завершити\n"
                        "Щоб отримати більш детальну інформацію натисніть /help"
    },
}

class QuizBot:
    def __init__(self, bot):
        self.bot = bot
        self.quiz = None

    def start(self):
        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            self.send_help_message(message)

        @self.bot.message_handler(commands=['start'])
        def start_quiz(message):
            self.start_new_quiz(message)

        @self.bot.callback_query_handler(func=lambda callback: True)
        def handle_button_click(callback):
            self.process_answer(callback)

        self.bot.polling(none_stop=True)

    def send_help_message(self, message):
        logger.info("User requested help")
        intro = bot_messages['help']['intro']
        start_quiz = bot_messages['help']['start_quiz']
        self.bot.send_message(message.chat.id, f"{intro}{start_quiz}")

    def start_new_quiz(self, message):
        logger.info("User started the bot")
        intro = bot_messages['start']['intro']
        instructions = bot_messages['start']['instructions']
        self.bot.send_message(message.chat.id, f"{intro}{instructions}")

        self.quiz = Quiz()
        self.quiz.ask_question(self.bot, message)
        self.quiz.startTime = datetime.datetime.now()

    def process_answer(self, callback):
    number_of_user_answer = int(callback.data.split('_')[1])
    current_question_index = self.quiz.current_question_number - 1
    question_data = self.quiz.questions[current_question_index]
    user_answer = question_data['options'][number_of_user_answer - 1]

    correct_answer = self.quiz.know_correct_answer()
    logger.info(f"User answer: {user_answer}, Correct answer: {correct_answer}")

    is_answer_correct = self.check_answer(user_answer, correct_answer)
    self.bot.send_message(callback.message.chat.id, f"Відповідь: '{is_answer_correct}'")

    if self.quiz.current_question_number < QUIZ_LENGTH:
        self.quiz.ask_question(self.bot, callback.message)
    else:
        end_time = datetime.datetime.now()
        self.quiz.end_quiz(self.bot, callback.message, end_time)

    def check_answer(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.quiz.increment_number_of_correct_answers(user_answer, correct_answer)
            return "Правильна"
        else:
            return "Неправильна"


class Quiz:
    def __init__(self):
        self.questions = self.load_and_shuffle_questions()
        self.number_of_correct_answers = 0
        self.current_question_number = 0
        self.start_time = None

    def load_and_shuffle_questions(self):
        questions = self.load_questions_from_file(QUESTIONS_FILE)
        random.shuffle(questions)
        return questions

    def load_questions_from_file(self, file_path):
        questions = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    question = {
                        'question': row['Question'],
                        'options': [row['Option 1'], row['Option 2'], row['Option 3'], row['Option 4']],
                        'correct_option': int(row['Correct Option'])
                    }
                    questions.append(question)
        except FileNotFoundError:
            logger.error(f"Файл {file_path} не знайдено.")
        except Exception as e:
            logger.error(f"Помилка при завантаженні питань: {e}")
        return questions

    def ask_question(self, bot, message):
        if self.current_question_number < QUIZ_LENGTH:
            self.send_question(bot, message)
            self.current_question_number += 1
        else:
            self.end_quiz(bot, message)

    def send_question(self, bot, message):
        question_data = self.questions[self.current_question_number]
        markup = self.create_question_markup(question_data['options'])
        question_text = question_data['question']
        bot.send_message(message.chat.id, question_text, reply_markup=markup)

    def create_question_markup(self, options):
        markup = types.InlineKeyboardMarkup()
        for i, option in enumerate(options, start=1):
            callback_data = f"answer_{i}"
            button = types.InlineKeyboardButton(text=f"{i}. {option}", callback_data=callback_data)
            markup.add(button)
        return markup

    def know_correct_answer(self):
        correct_option_index = self.questions[self.current_question_number - 1]['correct_option'] - 1
        return self.questions[self.current_question_number - 1]['options'][correct_option_index]

    def increment_number_of_correct_answers(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.number_of_correct_answers += 1

    def end_quiz(self, bot, message):
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        duration_formatted = self.format_duration(duration)
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.send_quiz_summary(bot, message, duration_formatted, formatted_end_time)

    def format_duration(self, duration):
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def send_quiz_summary(self, bot, message, duration_formatted, formatted_end_time):
        summary = (f"Тест завершено!\n"
                   f"Кількість правильних відповідей: {self.number_of_correct_answers}\n"
                   f"Дата та час завершення: {formatted_end_time}\n"
                   f"Тривалість проходження тесту: {duration_formatted}\n")
        bot.send_message(message.chat.id, summary)
        bot.send_message(message.chat.id, "Для початку нового тесту введіть /start")


if __name__ == "__main__":
    quiz_bot = QuizBot(bot)
    quiz_bot.start()
