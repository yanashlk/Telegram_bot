import logging
import random
import datetime
import telebot
from telebot import types
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_API_KEY')
quiz = None

bot_messages = {
    'help': {
        'intro': '\nБот складається з 10 питань, кожне з них має 4 варіанти відповіді. '
                 'Після проходження тесту ви дізнаєтесь результат: кількість відповідей та час проходження.',
        'start_quiz': '\t\nРозпочати опитування: /start'
    },
    'start': {
        'intro': "Ну що, готовий перевірити свої знання?\n"
                 "Тема: Python!\n\n",
        'instructions': "Жми /start якщо продовжуєш або /stop щоб завершити\n"
                        "Щоб отримати більш детальну інформацію натисніть /help"
    },
}

good_responses = ["Молодець!", "Чудово!", "Так тримати!", "Ти супер мозок!"]
bad_responses = ["Відповідь не правильна!", "Будь уважніше!", "Спробуй ще!"]

@bot.message_handler(commands=['help'])
def handle_help(message):
    logger.info("User requested help")
    intro = bot_messages['help']['intro']
    start_quiz = bot_messages['help']['start_quiz']
    bot.send_message(message.chat.id, f"{intro}{start_quiz}")

@bot.message_handler(commands=['start'])
def start_quiz(message):
    global quiz
    logger.info("User started the bot")
    intro = bot_messages['start']['intro']
    instructions = bot_messages['start']['instructions']
    bot.send_message(message.chat.id, f"{intro}{instructions}")
    
    quiz = Quiz()
    quiz.ask_question(message)
    quiz.startTime = datetime.datetime.now()

@bot.callback_query_handler(func=lambda callback: True)
def handle_button_click(callback):
    global quiz
    number_of_user_answer = int(callback.data.split('_')[1])
    question_data = quiz.questions[quiz.current_question_number - 1]
    answers = question_data['options']
    user_answer = answers[number_of_user_answer - 1]

    correct_answer = quiz.know_correct_answer()
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    current_question = quiz.current_question_number

    if current_question != 10:
        if correct_answer == user_answer:
            is_answer_correct = "Вірна"
            response = random.choice(good_responses)
            quiz.increment_number_of_correct_answers(user_answer, correct_answer)
        else:
            is_answer_correct = "Неправильна"
            response = random.choice(bad_responses)
        bot.send_message(callback.message.chat.id, f"Відповідь: '{is_answer_correct}' - {response}")
        quiz.ask_question(callback.message)
    else:
        end_time = datetime.datetime.now()
        quiz.end_quiz(callback.message, end_time)

class Quiz:
    def __init__(self):
        self.questions = self.load_questions()
        random.shuffle(self.questions)
        self.number_of_correct_answers = 0
        self.current_question_number = 0
        self.startTime = None

    def load_questions(self):
        questions = []
        with open('questions.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = {
                    'question': row['Question'],
                    'options': [row['Option 1'], row['Option 2'], row['Option 3'], row['Option 4']],
                    'correct_option': int(row['Correct Option'])
                }
                questions.append(question)
        return questions

    def ask_question(self, message):
        if self.current_question_number == 0:
            self.number_of_correct_answers = 0

        if self.current_question_number < 10:
            bot.delete_message(message.chat.id, message.message_id - 1)
            question_data = self.questions[self.current_question_number]
            markup = types.InlineKeyboardMarkup()
            question_text = question_data['question']
            options = question_data['options']
            for i, option in enumerate(options, start=1):
                callback_data = f"answer_{i}"
                button = types.InlineKeyboardButton(text=f"{i}. {option}", callback_data=callback_data)
                markup.add(button)

            bot.send_message(message.chat.id, f"{question_text}", reply_markup=markup)
            self.current_question_number += 1
        else:
            end_time = datetime.datetime.now()
            self.end_quiz(message, end_time)

    def know_correct_answer(self):
        question_data = self.questions[self.current_question_number - 1]
        correct_option = question_data['correct_option']
        answers = question_data['options']
        correct_answer = answers[correct_option - 1]
        return correct_answer

    def increment_number_of_correct_answers(self, user_answer, correct_answer):
        if user_answer == correct_answer:
            self.number_of_correct_answers += 1

    def end_quiz(self, message, end_time):
        duration = end_time - self.startTime
        duration_formatted = "{:0>2}:{:0>2}:{:0>2}".format(int(duration.seconds // 3600),
                                                           int((duration.seconds // 60) % 60),
                                                           int(duration.seconds % 60))
        formatted_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        bot.send_message(message.chat.id,
                         f"Тест завершено!\nКількість правильних відповідей: {self.number_of_correct_answers}\n"
                         f"Дата та час завершення: {formatted_end_time}\n"                                 
                         f"Тривалість проходження тесту: {duration_formatted}\n")
        bot.send_message(message.chat.id, "Для початку нового тесту введіть /start")

bot.polling(none_stop=True)
