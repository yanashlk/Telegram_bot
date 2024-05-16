import random
import datetime
import telebot
from telebot import types
import csv

bot = telebot.TeleBot('6668250527:AAFINq_6I0cTjxIfAW51J0NDCKP3fP8zZDA')
quiz = None

@bot.message_handler(commands=['start'])
def start_quiz(message):
    global quiz
    quiz = Quiz()
    quiz.ask_question(message)
    quiz.startTime = datetime.datetime.now()

@bot.callback_query_handler(func=lambda callback: True)
def handle_button_click(callback):
    number_of_user_answer = int(callback.data.split('_')[1])
    question_data = quiz.questions[quiz.current_question_number - 1]
    answers = question_data['options']
    user_answer = answers[number_of_user_answer - 1]

    correct_answer = quiz.know_correct_answer()
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    current_question = quiz.current_question_number
    if(current_question != 10):
        if correct_answer == user_answer:
            is_answer_correct = "Вірна"
        else:
            is_answer_correct = "Неправильна"
        bot.send_message(callback.message.chat.id, f"Відповідь: '{is_answer_correct}'")
    quiz.increment_number_of_correct_answers(correct_answer, user_answer)
    quiz.ask_question(callback.message)

class Quiz:
    def __init__(self):
        self.questions = self.load_questions()
        random.shuffle(self.questions)
        self.number_of_correct_answers = 0
        self.current_question_number = 0
        self.test_duration = None
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
        if(self.current_question_number == 0):
            self.number_of_correct_answers = 0

        if (self.current_question_number < 10):
            bot.delete_message(message.chat.id, message.message_id-1)
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
            bot.delete_message(message.chat.id, message.message_id - 1)
            end_time = datetime.datetime.now()
            self.end_quiz(message, end_time)

    def know_correct_answer(self):
        question_data = self.questions[self.current_question_number - 1]
        correct_option = question_data['correct_option']
        answers = question_data['options']
        correct_answer = answers[correct_option - 1]
        return correct_answer

    def increment_number_of_correct_answers(self, user_answer, correct_answer):
        if(user_answer == correct_answer): self.number_of_correct_answers += 1

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
