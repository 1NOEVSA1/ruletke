import telebot
import time
import random
from sympy import symbols, solve, parse_expr, simplify
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

bot = telebot.TeleBot('5187622946:AAHdoul6bLiS7aAqC0oQdh1l2pyylk7R6RY')


# команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/math', '/history')
    bot.send_message(message.chat.id, 'Выберите функцию:', reply_markup=keyboard)


# команда /dice
@bot.message_handler(commands=['math'])
def dice_function(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('решение уравнений', 'упрощение выражений')
    keyboard.row('рисование графиков функций', 'решение неравенств')
    keyboard.row('вернуться назад')
    bot.send_message(message.chat.id, 'Выберите кнопку', reply_markup=keyboard)
    bot.register_next_step_handler(message, dice_roll)


def dice_roll(message):
    if message.text == 'решение уравнений':
        bot.send_message(message.chat.id, 'Напишите уравнение:')
        bot.register_next_step_handler(message, symp)
    elif message.text == 'упрощение выражений':
        bot.send_message(message.chat.id, 'Напишите выражение:')
        bot.register_next_step_handler(message, symp1)
    elif message.text == 'рисование графиков функций':
        result = str(random.randint(1, 20))
        bot.send_message(message.chat.id, 'Выпало число: ' + result)
        dice_function(message)
    elif message.text == 'решение неравенств':
        bot.send_message(message.chat.id, 'Напишите неравенство:')
        bot.register_next_step_handler(message, symp2)
    elif message.text == 'вернуться назад':
        start_command(message)


def map_operations(formula_str):
    return formula_str.replace("^", "**").replace("=", "-")

def symp2(message):
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f = parse_expr(map_operations(message.text), transformations=transformations)
        roots = solve(f)  # <-- вернуть все корни уравнения в виде списка
        bot.send_message(message.chat.id, f'Ответ: {roots}')
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, f'Ошибка')
        dice_function(message)

def symp1(message):
    try:
        bot.send_message(message.chat.id,
                         f'Упрощённое выражение: '
                         f'{simplify(parse_expr(message.text.replace(")(", ")*(").replace("^", "**")))}')
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, f'Ошибка')
        dice_function(message)


def symp(message):
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f = parse_expr(map_operations(message.text), transformations=transformations)
        roots = solve(f)  # <-- вернуть все корни уравнения в виде списка
        if len(roots) > 1:
            bot.send_message(message.chat.id, f'Ответ: {", ".join(roots)}')
        elif len(roots) == 0:
            bot.send_message(message.chat.id, f'У уравнения либо нет решения или корнем является любое число')
        else:
            bot.send_message(message.chat.id, f'Ответ: {roots[0]}')
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, f'Ошибка')
        dice_function(message)


# команда /timer
@bot.message_handler(commands=['timer'])
def timer_function(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('30 секунд', '1 минута')
    keyboard.row('5 минут', 'вернуться назад')
    bot.send_message(message.chat.id, 'Выберите время:', reply_markup=keyboard)
    bot.register_next_step_handler(message, timer)


def timer(message):
    if message.text == 'вернуться назад':
        start_command(message)
    elif message.text == '30 секунд':
        bot.send_message(message.chat.id, 'Засек 30 секунд')
        time.sleep(30)
        bot.send_message(message.chat.id, '30 секунд истекло')
        close_keyboard(message)
    elif message.text == '1 минута':
        bot.send_message(message.chat.id, 'Засек 1 минуту')
        time.sleep(60)
        bot.send_message(message.chat.id, '1 минута истекла')
        close_keyboard(message)
    elif message.text == '5 минут':
        bot.send_message(message.chat.id, 'Засек 5 минут')
        time.sleep(300)
        bot.send_message(message.chat.id, '5 минут истекло')
        close_keyboard(message)


def close_keyboard(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/close')
    bot.send_message(message.chat.id, 'Таймер остановлен.', reply_markup=keyboard)
    bot.register_next_step_handler(message, reset_keyboard)


def reset_keyboard(message):
    if message.text == '/close':
        start_command(message)


bot.polling(none_stop=True)
