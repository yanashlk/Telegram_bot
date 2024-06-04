import logging
from quiz.QuizBot import QuizBot
from quiz.Quiz import Quiz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '6668250527:AAFINq_6I0cTjxIfAW51J0NDCKP3fP8zZDA'
QUESTIONS_FILE = 'questions.csv'

if __name__ == "__main__":
    bot = telebot.TeleBot(BOT_TOKEN)
    quiz_bot = QuizBot(bot, Quiz(QUESTIONS_FILE))
    quiz_bot.start()