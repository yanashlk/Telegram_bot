import datetime
import random
import csv
from typing import List, Dict
import logging
from .functions import (
    load_and_shuffle_questions,
    load_questions_from_file,
    ask_question,
    send_question,
    create_question_markup,
    know_correct_answer,
    increment_number_of_correct_answers,
    end_quiz,
    format_duration,
    send_quiz_summary
)

logger = logging.getLogger(__name__)

class Quiz:
    def __init__(self, questions_file):
        self.questions: List[Dict[str, any]] = load_and_shuffle_questions(questions_file)
        self.number_of_correct_answers: int = 0
        self.current_question_number: int = 0
        self.start_time: datetime.datetime = None

    def ask_question(self, bot, message):
        ask_question(self, bot, message)

    def end_quiz(self, bot, message, end_time: datetime.datetime):
        end_quiz(self, bot, message, end_time)

    def format_duration(self, duration: datetime.timedelta) -> str:
        return format_duration(duration)

    def send_quiz_summary(self, bot, message, duration_formatted, formatted_end_time):
        send_quiz_summary(self, bot, message, duration_formatted, formatted_end_time)
