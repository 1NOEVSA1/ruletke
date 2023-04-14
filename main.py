import telebot
import matplotlib.pyplot as plt
import numpy as np
from numexpr import evaluate
from sympy import solve, parse_expr, simplify
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import httplib2
import requests

SqlAlchemyBase = dec.declarative_base()

__factory = None


class Monument(SqlAlchemyBase):
    __tablename__ = 'monument'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    information = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Building(SqlAlchemyBase):
    __tablename__ = 'building'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    information = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)


class Street(SqlAlchemyBase):
    __tablename__ = 'streets'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    information = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


bot = telebot.TeleBot('5187622946:AAHdoul6bLiS7aAqC0oQdh1l2pyylk7R6RY')
error = """Уважаемый пользователь, к сожалению, ваш запрос не может быть выполнен из-за некорректного ввода данных. Пожалуйста, проверьте правильность введенной информации и повторите попытку."""


# команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,
                     f"""Здравствуйте, @{message.from_user.first_name}! Рады приветствовать Вас в нашем телеграмм боте. Мы создали его, чтобы облегчить Вам жизнь и сделать её более интересной и продуктивной. Здесь Вы можете получить доступ к множеству полезных функций, а также узнать много всего нового. Мы надеемся, что использование нашего бота станет для Вас приятным и удобным, и Вы найдете здесь все, что Вам нужно. Желаем приятного использования нашего телеграмм бота!""")
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Математика', 'История')
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)
    bot.register_next_step_handler(message, decide)


def decide(message):
    if message.text == 'Математика':
        dice_function(message)
    if message.text == 'История':
        tice_function(message)


def tice_function(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Памятники', 'Улицы')
    keyboard.row('Здания', 'Вернуться назад')
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)
    bot.register_next_step_handler(message, dice_roll)


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
    elif message.text == 'Памятники':
        bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=mon('Памятники'))
        bot.register_next_step_handler(message, obrabot_mon)
    elif message.text == 'Улицы':
        bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=mon('Улицы'))
        bot.register_next_step_handler(message, obrabot_street)
    elif message.text == 'Здания':
        bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=mon('Здания'))
        bot.register_next_step_handler(message, obrabot_bil)


def load_photo(link):
    h = httplib2.Http('.cache')
    response, content = h.request(f'{link}')
    out = open('img.jpg', 'wb')
    out.write(content)
    out.close()


def locate(name):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={name}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        k = ''.join(toponym).split()
        return f'http://static-maps.yandex.ru/1.x/?ll={str(k[0])},{str(k[-1])}&spn=0.002,0.002&l=map&pt={str(k[0])},{str(k[-1])},pm2rdm'

    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def obrabot_mon(message):
    global_init('data_base.db')
    session = create_session()
    if message.text == 'Вернуться назад':
        bot.register_next_step_handler(message, tice_function)
    else:
        for user in session.query(Monument).filter(Monument.name == message.text):
            load_photo(user.link)
            bot.send_photo(message.chat.id, open('img.jpg', 'rb'), caption=f'{user.name}')
            bot.send_message(message.chat.id, f'{user.information}\nРасположение:\n{user.full_name}')
    tice_function(message)


def obrabot_bil(message):
    global_init('db/data_base.db')
    session = create_session()
    if message.text == 'Вернуться назад':
        bot.register_next_step_handler(message, tice_function)
    else:
        for user in session.query(Building).filter(Building.name == message.text):
            load_photo(user.link)
            bot.send_photo(message.chat.id, open('img.jpg', 'rb'), caption=f'{user.name}')
            bot.send_message(message.chat.id, f'{user.information}')
            load_photo(locate(user.full_name))
            bot.send_photo(message.chat.id, open('img.jpg', 'rb'), caption=f'Расположение:\n{user.full_name}')
    tice_function(message)


def obrabot_street(message):
    global_init('db/data_base.db')
    session = create_session()
    if message.text == 'Вернуться назад':
        bot.register_next_step_handler(message, tice_function)
    else:
        for user in session.query(Street).filter(Street.name == message.text):
            load_photo(locate(user.full_name))
            bot.send_photo(message.chat.id, open('img.jpg', 'rb'), caption=f'Расположение:\n{user.full_name}')
            bot.send_message(message.chat.id, f'{user.information}')
    tice_function(message)


def mon(name):
    global_init('db/data_base.db')
    session = create_session()
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    if name == 'Памятники':
        for user in session.query(Monument):
            keyboard.row(user.name)
    if name == 'Улицы':
        for user in session.query(Street):
            keyboard.row(user.name)
    if name == 'Здания':
        for user in session.query(Building):
            keyboard.row(user.name)
    keyboard.row('Вернуться назад')
    return keyboard


def send_plot(message):
    global error
    try:
        expression = message.text.replace(' ', '').replace('y=', '').replace('^', '**')
        x = np.linspace(-10, 10, 1000)
        y = evaluate(expression)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_title(f"График функции {expression}")
        fig.savefig('plot.png')
        bot.send_photo(message.chat.id, open('plot.png', 'rb'),
                       caption=f"""Уважаемый @{message.from_user.first_name}, представляем вашему вниманию график функции {expression}. Надеемся, что он поможет вам лучше понять и проанализировать данную функцию. Желаем успешных вычислений!""")
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
                         f"""Уважаемый @{message.from_user.first_name}, мы рады предоставить вам ответ на ваш запрос по неравенству. Наш алгоритм обработал ваш запрос и нашёл решение: {roots}. Мы надеемся, что наш ответ поможет вам добиться желаемого результата. Желаем вам успехов в решении математических задач!""")
        dice_function(message)
    except Exception:
        bot.send_message(message.chat.id, error)
        dice_function(message)


def symp1(message):
    global error
    try:
        bot.send_message(message.chat.id,
                         f"""Уважаемый @{message.from_user.first_name}, мы рады предоставить вам ответ на ваш запрос. Наш алгоритм обработал ваш запрос и нашёл решение: {simplify(parse_expr(message.text.replace(")(", ")*(").replace("^", "**")))}. Мы надеемся, что наш ответ поможет вам добиться желаемого результата. Желаем вам успехов в решении математических задач!""")
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
                             f"""Уважаемый @{message.from_user.first_name}, предоставляем вам корни уравнения: {", ".join(roots)}, которые вы запрашивали. Мы надеемся, что данная информация поможет вам более глубоко изучить и проанализировать вашу задачу. Желаем вам удачи в решении вычислительных задач!""")
        elif len(roots) == 0:
            bot.send_message(message.chat.id,
                             f"""Уважаемый @{message.from_user.first_name}, мы рады сообщить, что наш алгоритм успешно обработал ваш запрос и вычислил, что корень уравнения может быть любым числом или не иметь решения. Мы надеемся, что наш ответ поможет вам понять особенности данного уравнения и продвинуться в решении математических задач. Желаем вам успехов и легкости в изучении математики!""")
        else:
            bot.send_message(message.chat.id,
                             f"""Уважаемый @{message.from_user.first_name}, предоставляем вам корни уравнения: {str(roots[0])}, которые вы запрашивали. Мы надеемся, что данная информация поможет вам более глубоко изучить и проанализировать вашу задачу. Желаем вам удачи в решении вычислительных задач!""")
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
