import telebot
from telebot import types
import sqlite3
import db as rep
import re

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot("7701481676:AAFg5Lz5lFZ47SFk6qixSwynk9r8SJaHmyE")
questions = [
    # "1. Введите ФИО",
    # "2. Ваш номер телефона",
    # "3. Адрес электронной почты",
    "1. Как часто ты участвуешь в мероприятиях университета?",
    "2. Умеешь ли ты общаться с новыми людьми легко и с удовольствием?",
    "3. Считаешь ли ты себя организованным человеком?",
    "4. Хотел бы ты участвовать в организации карьерных мероприятий (встречи с работодателями, мастер-классы, хакатоны и т.п.)?",
    "5. Есть ли у тебя опыт участия в студенческих организациях или проектах?",
    "6. Готов ли ты тратить время на развитие карьерного направления (примерно 3–5 часов в неделю)?",
    "7. Насколько тебе интересна тема трудоустройства, карьеры и профориентации?",
    "8. Можешь ли ты представить, что рассказываешь о возможностях вуза студентам или работодателям?",
    "9. Чувствуешь ли ты ответственность за результат своей команды?",
    "10. Хочешь ли ты развивать soft skills (коммуникация, лидерство, тайм-менеджмент и т.п.)?"
]

responses = {}
current_question_index = {}

def validate_phone(phone):
    """
    Проверяет, является ли телефонный номер корректным.
    Допускаются только цифры и длина от 10 до 15 символов.
    """
    pattern = r'^\d{10,15}$'
    return re.match(pattern, phone) is not None

def validate_email(email):
    """
    Проверяет, является ли адрес электронной почты корректным.
    Используется стандартный формат email.
    """
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

@bot.message_handler(commands=['start'])
def start_survey(message):
    user_id = message.chat.id
    rep.add_user_with_empty_values(user_id)
    rep.mark_survey_started(user_id)
    responses[user_id] = 0
    current_question_index[user_id] = 0
    hello_message = """💬 Привет! 👋 
    \nХочешь узнать, подойдёшь ли ты на роль Амбассадора карьеры? 
    \nЭто твой шанс стать частью студенческого сообщества, помогать другим строить карьеру и развивать свои навыки! Пройди короткий тест, и мы вместе разберёмся, готов ли ты начать этот путь!"""
    bot.send_message(user_id, hello_message)
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Очень часто", callback_data=f"q1_1")
    btn1 = types.InlineKeyboardButton("Иногда", callback_data=f"q1_2")
    btn2 = types.InlineKeyboardButton("Почти не участвую", callback_data=f"q1_3")
    markup.add(btn,btn1,btn2)
    bot.send_message(message.chat.id, questions[0], reply_markup=markup)
    # bot.register_next_step_handler(message, saveName)

@bot.message_handler(commands=['export'])
def exportCSV(message):
    rep.export_to_csv()
    with open('responses_export.csv', 'rb') as file:
        bot.send_document(message.chat.id, file)

# @bot.message_handler(func=lambda message: True)
# def handle_response(message):
#     user_id = message.chat.id
#     if user_id not in current_question_index:
#         bot.send_message(user_id, "Введите /start для начала опроса.")
#         return

#     # Сохраняем ответ на текущий вопрос
#     responses[user_id][questions[current_question_index[user_id]]] = message.text

#     # Переходим к следующему вопросу
#     current_question_index[user_id] += 1

#     if current_question_index[user_id] < len(questions):
#         bot.send_message(user_id, questions[current_question_index[user_id]])
#     else:
#         # Сохраняем ответы в базу данных
#         save_response(user_id, responses[user_id])
#         bot.send_message(user_id, "Спасибо за участие в опросе!")
#         del current_question_index[user_id]
#         del responses[user_id]

def saveName(message):
    rep.update_column_by_name(message.chat.id, "name", message.text)
    bot.send_message(message.chat.id, questions[1])
    bot.register_next_step_handler(message, savePhone)

def savePhone(message):
    phone = message.text
    phone = str(phone).replace("+", "").strip()
    if validate_phone(phone):
        rep.update_column_by_name(message.chat.id, "phone", phone)
        bot.send_message(message.chat.id, questions[2])
        bot.register_next_step_handler(message, saveMail)
    else:
        bot.send_message(message.chat.id, "Неверный формат телефона. Пожалуйста, введите номер телефона снова.")
        bot.register_next_step_handler(message, savePhone)

def saveMail(message):
    email = message.text
    email = str(email).strip()
    if validate_email(email):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Очень часто", callback_data=f"q1_1")
        btn1 = types.InlineKeyboardButton("Иногда", callback_data=f"q1_2")
        btn2 = types.InlineKeyboardButton("Почти не участвую", callback_data=f"q1_3")
        markup.add(btn,btn1,btn2)
        bot.send_message(message.chat.id, questions[3], reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неверный формат электронной почты. Пожалуйста, введите адрес электронной почты снова.")
        bot.register_next_step_handler(message, saveMail)

@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
    data = str(callback.data)
    if data.__contains__("q1_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=5
            bot.send_message(callback.message.chat.id, "🟢 Ты настоящий студент! Активность тебе знакома.")
        elif var == "2":
            responses[callback.message.chat.id] +=2
            bot.send_message(callback.message.chat.id, "🟡 Отлично, ты уже в теме. Попробуй быть чуть активнее!")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Начни с малого. Участие — первый шаг к лидерству!")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, мне это нравится", callback_data=f"q2_1")
        btn1 = types.InlineKeyboardButton("Только с теми, кто мне интересен", callback_data=f"q2_2")
        btn2 = types.InlineKeyboardButton("Не очень", callback_data=f"q2_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[1], reply_markup=markup)
    elif data.__contains__("q2_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=5
            bot.send_message(callback.message.chat.id, "🟢 Супер! Тебе точно подойдёт роль проводника между студентами и работодателями.")
        elif var == "2":
            responses[callback.message.chat.id] +=3
            bot.send_message(callback.message.chat.id, "🟡 Не беда! Это можно научиться. Главное — желание.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Полезный навык, но в роли амбассадора важно находить общий язык с разными людьми.")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, всегда держу план в голове", callback_data=f"q3_1")
        btn1 = types.InlineKeyboardButton("Иногда", callback_data=f"q3_2")
        btn2 = types.InlineKeyboardButton("Нет, всё по настроению", callback_data=f"q3_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)        
        bot.send_message(callback.message.chat.id, questions[2], reply_markup=markup)
    elif data.__contains__("q3_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=5
            bot.send_message(callback.message.chat.id, "🟢 Отличная база для успешной работы в проектах!")
        elif var == "2":
            responses[callback.message.chat.id] +=3
            bot.send_message(callback.message.chat.id, "🟡 Ты на пути к порядку. Подумай, как сделать его регулярным.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Важно учиться планировать. Эта привычка пригодится в работе амбассадора.  ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, мне это нравится", callback_data=f"q4_1")
        btn1 = types.InlineKeyboardButton("Возможно, если будет интересно ", callback_data=f"q4_2")
        btn2 = types.InlineKeyboardButton("Нет, я не люблю это", callback_data=f"q4_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)        
        bot.send_message(callback.message.chat.id, questions[3], reply_markup=markup)
    elif data.__contains__("q4_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=15
            bot.send_message(callback.message.chat.id, "🟢 Ты уже почти амбассадор! Такие люди нам нужны!")
        elif var == "2":
            responses[callback.message.chat.id] +=7
            bot.send_message(callback.message.chat.id, "🟡 Интерес — отличная мотивация. Можно начинать с малого.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Может, просто ещё не пробовал? Организация — это целое искусство! ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, недавно участвовал", callback_data=f"q5_1")
        btn1 = types.InlineKeyboardButton("Был, но давно ", callback_data=f"q5_2")
        btn2 = types.InlineKeyboardButton("Нет", callback_data=f"q5_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)        
        bot.send_message(callback.message.chat.id, questions[4], reply_markup=markup)
    elif data.__contains__("q5_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=15
            bot.send_message(callback.message.chat.id, "🟢 Опыт на вес золота! Это серьёзный плюс в твоём портфолио.")
        elif var == "2":
            responses[callback.message.chat.id] +=7
            bot.send_message(callback.message.chat.id, "🟡 Отлично! Значит, ты умеешь включаться в работу команды.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Никто не начинал с опыта. Главное — начать сейчас!")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, готов", callback_data=f"q6_1")
        btn1 = types.InlineKeyboardButton("Возможно, зависит от задач ", callback_data=f"q6_2")
        btn2 = types.InlineKeyboardButton("Нет, времени нет ", callback_data=f"q6_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[5], reply_markup=markup)
    elif data.__contains__("q6_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=15
            bot.send_message(callback.message.chat.id, "🟢 Отличный уровень вовлечённости! Мы ценим таких людей.")
        elif var == "2":
            responses[callback.message.chat.id] +=7
            bot.send_message(callback.message.chat.id, "🟡 Гибкость — хорошо. Главное, чтобы было место для развития.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Жаль… Но если в будущем появится возможность — попробуй.  ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Очень интересно", callback_data=f"q7_1")
        btn1 = types.InlineKeyboardButton("Иногда интересно", callback_data=f"q7_2")
        btn2 = types.InlineKeyboardButton("Совсем не интересно ", callback_data=f"q7_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[6], reply_markup=markup)
    elif data.__contains__("q7_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=15
            bot.send_message(callback.message.chat.id, "🟢 Ты уже в теме! Это важная черта амбассадора.")
        elif var == "2":
            responses[callback.message.chat.id] +=7
            bot.send_message(callback.message.chat.id, "🟡 Отлично! Интерес можно развивать через практику.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Если хочешь стать амбассадором, стоит хотя бы немного «влюбиться» в эту тему.  ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, без проблем ", callback_data=f"q8_1")
        btn1 = types.InlineKeyboardButton("Возможно, если подготовиться ", callback_data=f"q8_2")
        btn2 = types.InlineKeyboardButton("Нет, это сложно", callback_data=f"q8_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[7], reply_markup=markup)
    elif data.__contains__("q8_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=5
            bot.send_message(callback.message.chat.id, "🟢 Ты готов быть лицом отдела карьеры!")
        elif var == "2":
            responses[callback.message.chat.id] +=3
            bot.send_message(callback.message.chat.id, "🟡 Подготовка — ключ к успеху. Ты на правильном пути.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Публичные выступления — навык, который можно тренировать.  ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, стараюсь делать всё максимально качественно ", callback_data=f"q9_1")
        btn1 = types.InlineKeyboardButton("Иногда", callback_data=f"q9_2")
        btn2 = types.InlineKeyboardButton("Нет, я работаю один ", callback_data=f"q9_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[8], reply_markup=markup)
    elif data.__contains__("q9_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=5
            bot.send_message(callback.message.chat.id, "🟢 Ответственность — основа успеха любой команды!")
        elif var == "2":
            responses[callback.message.chat.id] +=3
            bot.send_message(callback.message.chat.id, "🟡 Хороший старт. Давай расти в этом направлении.")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 В команде важно чувствовать ответственность за общее дело.  ")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Да, именно поэтому и хочу стать амбассадором ", callback_data=f"q10_1")
        btn1 = types.InlineKeyboardButton("Возможно", callback_data=f"q10_2")
        btn2 = types.InlineKeyboardButton("Нет, мне хватает того, что есть ", callback_data=f"q10_3")
        markup.add(btn)
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(callback.message.chat.id, questions[9], reply_markup=markup)
    elif data.__contains__("q10_"):
        var = data.split("_")[1]
        if var == "1":
            responses[callback.message.chat.id] +=15
            bot.send_message(callback.message.chat.id, "🟢 Ура! Ты на верном пути к личностному росту!")
        elif var == "2":
            responses[callback.message.chat.id] +=8
            bot.send_message(callback.message.chat.id, "🟡 Это уже шаг вперёд. Ждём тебя в числе кандидатов!")
        elif var == "3":
            bot.send_message(callback.message.chat.id, "🟡 Развитие — путь к большему. Возможно, однажды захочется больше. ")
        finalMessage(callback.message.chat.id)
        
def finalMessage(user_id):
    if responses[user_id]>35:
        final_message = "🎉 Поздравляем! Ты подходишь на роль амбассадора карьеры! \nХочешь стать частью команды, которая помогает другим студентам находить свой путь?"
        final_message1 = "👉 Переходи по ссылке и подавай заявку: \nhttps://forms.yandex.ru/cloud/683fd13002848f268513e616/ "
        bot.send_message(user_id, final_message)
        bot.send_message(user_id, final_message1)
        rep.mark_survey_finished(user_id, is_positive=True)  # если результат положительный
    else:
        final_message = "⚠️ К сожалению, на данный момент мы не можем предложить вам участие, так как полученные ответы указывают на недостаточный уровень активности и мотивации к дальнейшему развитию, что является важным критерием для нас."
        final_message1 = "🚀 Тем не менее, вы можете пройти форму снова в будущем, если почувствуете больше интереса и желания двигаться вперёд."
        bot.send_message(user_id, final_message)
        bot.send_message(user_id, final_message1)
        rep.mark_survey_finished(user_id, is_positive=False) # если результат отрицательный

def pol():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        print("Connection Refused!")
        pol()
pol()