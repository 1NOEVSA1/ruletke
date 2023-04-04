import telebot
import matplotlib.pyplot as plt
import numpy as np
from numexpr import evaluate
from sympy import symbols, solve, parse_expr, simplify
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

bot = telebot.TeleBot('5187622946:AAHdoul6bLiS7aAqC0oQdh1l2pyylk7R6RY')
error = """Уважаемый пользователь, к сожалению, ваш запрос не может быть выполнен из-за некорректного ввода данных. Пожалуйста, проверьте правильность введенной информации и повторите попытку."""


# команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, f"""Здравствуйте, {message.from_user.first_name}! Рады приветствовать
     Вас в нашем телеграмм боте. Мы создали его, чтобы облегчить Вам жизнь и сделать её более интересной и продуктивной.
      Здесь Вы можете получить доступ к множеству полезных функций, а также узнать много всего нового. Мы надеемся, что
       использование нашего бота станет для Вас приятным и удобным, и Вы найдете здесь все, что Вам нужно.
        Желаем приятного использования нашего телеграмм бота!""")
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/math', '/history')
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)


# команда /dice
@bot.message_handler(commands=['math'])
def dice_function(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Решение уравнений', 'Упрощение выражений')
    keyboard.row('Построение графиков функций', 'Решение неравенств')
    keyboard.row('Вернуться назад')
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)
    bot.register_next_step_handler(message, dice_roll)


def dice_roll(message):
    if message.text == 'Решение уравнений':
        bot.send_message(message.chat.id, 'Напишите уравнение:')
        bot.register_next_step_handler(message, symp)
    elif message.text == 'Упрощение выражений':
        bot.send_message(message.chat.id, 'Напишите выражение:')
        bot.register_next_step_handler(message, symp1)
    elif message.text == 'Построение графиков функций':
        bot.send_message(message.chat.id, 'Напишите функцию:')
        bot.register_next_step_handler(message, send_plot)
    elif message.text == 'Решение неравенств':
        bot.send_message(message.chat.id, 'Напишите неравенство:')
        bot.register_next_step_handler(message, symp2)
    elif message.text == 'Вернуться назад':
        start_command(message)


def send_plot(message):
    global error
    try:
        expression = message.text.replace(' ', '').replace('y=', '').replace('^', '**')
        print(expression)
        x = np.linspace(-10, 10, 1000)
        y = evaluate(expression)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title(f"График функции {expression}")
        fig.savefig('plot.png')
        bot.send_photo(message.chat.id, open('plot.png', 'rb'),
                       caption=f"""Уважаемый {message.from_user.first_name}, представляем вашему вниманию график функции {expression}. Надеемся, что он поможет вам лучше понять и проанализировать данную функцию. Желаем успешных вычислений!""")
        dice_function(message)
    except:
        bot.send_message(message.chat.id, error)
        dice_function(message)


def map_operations(formula_str):
    return formula_str.replace("^", "**").replace("=", "-")


def symp2(message):
    global error
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f = parse_expr(map_operations(message.text), transformations=transformations)
        roots = solve(f)  # <-- вернуть все корни уравнения в виде списка
        bot.send_message(message.chat.id,
                         f"""Уважаемый {message.from_user.first_name}, мы рады предоставить вам ответ на ваш запрос по неравенству. Наш алгоритм обработал ваш запрос и нашёл решение: {roots}. Мы надеемся, что наш ответ поможет вам добиться желаемого результата. Желаем вам успехов в решении математических задач!""")
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, error)
        dice_function(message)


def symp1(message):
    global error
    try:
        bot.send_message(message.chat.id,
                         f"""Уважаемый {message.from_user.first_name}, мы рады предоставить вам ответ на ваш запрос. Наш алгоритм обработал ваш запрос и нашёл решение: {simplify(parse_expr(message.text.replace(")(", ")*(").replace("^", "**")))}. Мы надеемся, что наш ответ поможет вам добиться желаемого результата. Желаем вам успехов в решении математических задач!""")
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, error)
        dice_function(message)


def symp(message):
    global error
    try:
        transformations = (standard_transformations + (implicit_multiplication_application,))
        f = parse_expr(map_operations(message.text), transformations=transformations)
        roots = [str(x) for x in solve(f)]  # <-- вернуть все корни уравнения в виде списка
        if len(roots) > 1:
            bot.send_message(message.chat.id,
                             f"""Уважаемый {message.from_user.first_name}, предоставляем вам корни уравнения: {", ".join(roots)}, которые вы запрашивали. Мы надеемся, что данная информация поможет вам более глубоко изучить и проанализировать вашу задачу. Желаем вам удачи в решении вычислительных задач!""")
        elif len(roots) == 0:
            bot.send_message(message.chat.id,
                             f"""Уважаемый {message.from_user.first_name}, мы рады сообщить, что наш алгоритм успешно обработал ваш запрос и вычислил, что корень уравнения может быть любым числом или не иметь решения. Мы надеемся, что наш ответ поможет вам понять особенности данного уравнения и продвинуться в решении математических задач. Желаем вам успехов и легкости в изучении математики!""")
        else:
            bot.send_message(message.chat.id,
                             f'f"""Уважаемый {message.from_user.first_name}, предоставляем вам корни уравнения: {str(roots[0])}, которые вы запрашивали. Мы надеемся, что данная информация поможет вам более глубоко изучить и проанализировать вашу задачу. Желаем вам удачи в решении вычислительных задач!"""')
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, error)
        dice_function(message)


def close_keyboard(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/close')
    bot.send_message(message.chat.id, 'Таймер остановлен.', reply_markup=keyboard)
    bot.register_next_step_handler(message, reset_keyboard)


def reset_keyboard(message):
    if message.text == '/close':
        start_command(message)


bot.polling(none_stop=True)
