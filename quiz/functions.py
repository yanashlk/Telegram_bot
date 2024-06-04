import datetime
import random
import csv
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def load_and_shuffle_questions(file_path: str) -> List[Dict[str, any]]:
    questions: List[Dict[str, any]] = load_questions_from_file(file_path)
    if questions:
        shuffle_questions(questions)
    return questions

def load_questions_from_file(file_path: str) -> List[Dict[str, any]]:
    questions: List[Dict[str, any]] = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                question: Dict[str, any] = create_question_from_row(row)
                questions.append(question)
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не знайдено.")
        return []
    except Exception as e:
        logger.error(f"Помилка при завантаженні питань: {e}")
        return []
    return questions

def create_question_from_row(row: Dict[str, str]) -> Dict[str, any]:
    return {
        'question': row['Question'],
        'options': [row['Option 1'], row['Option 2'], row['Option 3'], row['Option 4']],
        'correct_option': int(row['Correct Option'])
    }

def shuffle_questions(questions: List[Dict[str, any]]) -> None:
    random.shuffle(questions)

def ask_question(quiz, bot, message):
    if quiz.current_question_number < len(quiz.questions):
        send_question(quiz, bot, message)
        quiz.current_question_number += 1
    else:
        end_quiz(quiz, bot, message, datetime.datetime.now())

def send_question(quiz, bot, message):
    if quiz.current_question_number < len(quiz.questions):
        question_data: Dict[str, any] = quiz.questions[quiz.current_question_number]
        markup = create_question_markup(question_data['options'])
        question_text: str = question_data['question']
        bot.send_message(message.chat.id, question_text, reply_markup=markup)
    else:
        logger.error("Спроба відправки питання, коли всі питання вже задані.")

def create_question_markup(options: List[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for i, option in enumerate(options, start=1):
        callback_data = f"answer_{i}"
        button = create_inline_keyboard_button(i, option, callback_data)
        markup.add(button)
    return markup

def create_inline_keyboard_button(index: int, text: str, callback_data: str) -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(text=f"{index}. {text}", callback_data=callback_data)

def know_correct_answer(quiz) -> str:
    if quiz.current_question_number < len(quiz.questions):
        correct_option_index = quiz.questions[quiz.current_question_number - 1]['correct_option'] - 1
        return quiz.questions[quiz.current_question_number - 1]['options'][correct_option_index]
    else:
        logger.error("Спроба отримати правильну відповідь, коли всі питання вже задані.")
        return ""

def increment_number_of_correct_answers(quiz, user_answer: str, correct_answer: str):
    if user_answer == correct_answer:
        quiz.number_of_correct_answers += 1

def end_quiz(quiz, bot, message, end_time: datetime.datetime):
    if quiz.start_time is not None:
        duration = end_time - quiz.start_time
        duration_formatted = format_duration(duration)
        formatted_end_time = format_end_time(end_time)
        send_quiz_summary(quiz, bot, message, duration_formatted, formatted_end_time)
    else:
        logger.error("Спроба завершити тест, але час початку не встановлено.")

def format_duration(duration: datetime.timedelta) -> str:
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def format_end_time(end_time: datetime.datetime) -> str:
    return end_time.strftime("%Y-%m-%d %H:%M:%S")

def send_quiz_summary(quiz, bot, message, duration_formatted, formatted_end_time):
    summary = create_quiz_summary_message(quiz, duration_formatted, formatted_end_time)
    bot.send_message(message.chat.id, summary)
    bot.send_message(message.chat.id, "Для початку нового тесту введіть /start")

def create_quiz_summary_message(quiz, duration_formatted, formatted_end_time) -> str:
    return (f"Тест завершено!\n"
            f"Кількість правильних відповідей: {quiz.number_of_correct_answers}\n"
            f"Дата та час завершення: {formatted_end_time}\n"
            f"Тривалість проходження тесту: {duration_formatted}\n")
