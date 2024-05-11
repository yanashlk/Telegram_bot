import telebot
from telebot import types
import random
import time
import csv

bot = telebot.TeleBot('6719567455:AAFnnVotReWuMb848dN7A-IlamMjQDU4Fas')

start_time = None

with open('questions.csv', 'r', encoding='utf-8') as csvfile:
    questions_reader = csv.reader(csvfile)
    questions = []
    questions = [row for row in questions_reader]
    #print(questions[1])
    random.shuffle(questions)


good = ["Молодець!", "Чудово!", "Так тримати!", "Ти супер мозок!"]
randomGood = random.choices(good)
random1 = randomGood[0] or randomGood[1] or randomGood[2] or randomGood[3]

bad = ["Відповідь не правильна!", "Будь уважніше!", "Спробуй ще!"]
randomBad = random.choices(bad)
random2 = randomBad[0] or randomBad[1] or randomBad[2]

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Ну що, готовий перевірити свої знання?\n"
                                      "Тема: Python!\n\n"
                                      "Жми /go якщо продовжуєш або /stop щоб завершити\n"
                                      "Щоб отримати більш детальну інформацію натисніть /help")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '\nБот складається з 5 питань, кожне з них має 4 варіанти відповіді. '
                                      'Після проходження тесту ви дізнаєтесь результат: кількість відповідей та час проходження.'
                                      '\t\nРозпочати опитування: /go')

@bot.message_handler(commands=['go'])
def handle_go(message):
    points = 0
    start_time = time.time()
    current_question_index = 0
    def send_question():
        nonlocal current_question_index
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        current_question = questions[current_question_index]

        # Iterate over answer options and add them to the markup
        for option in current_question[1:]:
            markup.add(types.KeyboardButton(option))

        bot.send_message(message.chat.id, current_question[0], reply_markup=markup)

    send_question()

    @bot.message_handler(func=lambda message: message.text in questions[current_question_index][1:])
    def handle_answer(message):
        nonlocal points, current_question_index

        user_answer = message.text
        correct_answer = questions[current_question_index][5]

        if user_answer == correct_answer:
            bot.send_message(message.chat.id, random1)
            points += 1
        else:
            bot.send_message(message.chat.id, random2)

        current_question_index += 1
        if current_question_index < len(questions):
            send_question()
        else:
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            bot.send_message(message.chat.id, f'Ви успішно пройшли тест за {time_taken} секунд.')
            bot.send_message(message.chat.id, f'Ви набрали {points} з {len(questions) - 1}.')  # Subtract 1 for the initial question

bot.polling()



