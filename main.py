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
from data.Buildings import Building
from data.Streets import Street
from data.Monuments import Monument
import httplib2
import requests
from random import choice
import openai

anecdot = ["""Тренер утешает проигравшего боксера:
- Но в третьем раунде ты своего противника здорово напугал.
- Чем это?
- Ему показалось, что он тебя убил.""", """Старушка входит в переполненный ленинградский автобус. Никто ей не уступает место.
- Неужели в Санкт-Петербурге не осталось интеллигенции?
Ей отвечает сидящий здоровяк:
- Интелихенции, мамаша, до хрена, а вот автобусов мало!""",
           """- Господин капитан, почему большинство кораблей носят женские имена?
           - Если бы вы знали, как ими трудно управлять, вы бы не задавали глупых вопросов.""",
           """- Официант, я хотел бы получить то же, что у господина за соседним столиком.
           - Нет проблем, месье. Я сейчас позову его к телефону, а вы действуйте.""",
           """Шестисотый мерин въезжает сзади в каток. Из машины вылезает здоровенный детина и начинает звонить по мобиле своему гаишнику.
           Через некоторое время останавливается милицейская тачка, из нее выходит гаишник, подходит к водителю катка, отводит его в сторону и задушевно шепчет:
           - Ну, рассказывай. Как обгонял... Как подрезал...""",
           """- Вовочка, открой скорее ротик и скажи а-а-а, чтобы этот злой и противный доктор смог наконец вытащить свой пальчик из твоих зубок!""",
           """Лекция в сельскохозяйственном институте. Профессор говорит:
- Племенной бык может произвести до ста половых актов.
Студентка:
- Это за какой период времени?
Профессор:
- За сутки.
Студентка:
- Повторите это для студента с последнего ряда.
Студент с последнего ряда:
- Скажите, профессор, с одной коровой или со всем стадом?
Профессор:
- Со всем стадом.
Студент:
- Повторите это для студентки с первого ряда.""",
           """Прапор приходит домой и говорит жене:
- Жрать давай!
Жена жалуется:
- Я так устала. За весь день ни разу не присела...
.....
Прапор сжалился над ней и заставил присесть ее двести раз...""",
           """- Иногда приходится жалеть, что твой друг не был большой свиньей, - вздыхал голодный Винни-Пух, обжаривая Пятачка на костре.""",
           """Налоговый инспектор спрашивает нового русского:
- Вы уверены, что виллу, пять "Мерседесов" и шесть квартир в центре вы купили на честно заработанные деньги?
- А, на какие еще?
- Мне кажется, что все это куплено на народные деньги!
- Ты че, ваще?! Откуда у народа такие деньги?""",
           """- Хаим, ты слышал, что скоро будет погром?
- А я не боюсь - я по паспорту русский.
- Дурак, бить будут не по паспорту, а по морде!""",
           """На ташкентском базаре покупатель поднимает дыню и, чтобы сбить цену, ехидничает:
- Эти яблоки у вас самые большие?
Продавец парирует:
- Не трогайте виноград руками...""",
           """Автобус битком набит пассажирами. Один мужчина стоит на подножке и говорит:
- Наро-о-од, потеснитесь. Иначе по головам пойду!
Лысый мужик отвечает ему, поглаживая лысину мокрой ладошкой:
- Да чтоб ты поскользнулся!
- Да у меня шиповки!""",
           """Разгадана тайна скрипки Шерлока Холмса:
тихими зимними вечерами её звуки разносились по ночному Лондону, и от этого у хулиганов отнимались ноги, у грабителей опускались руки!
Насильники тоже были не довольны...""",
           """Муж внезапно возвращается из командировки и обнаруживает на ночном столике сигару.
- Откуда эта сигара?
Жена молчит.
- Я в последний раз спрашиваю, откуда сигара?
- Да из Гаваны, болван! - раздается из шкафа.""",
           """Шеф обращается к новому сотруднику:
- Мой заместитель объяснил вам, что вы будете делать?
- Да, мсье.
- И что же он вам сказал?
- Что я должен просыпаться, если вы появитесь.""",
           """- Скажите, пожалуйста, ваш цепной пес подпускает к себе?
- Конечно! Иначе как он сможет вас укусить?""",
           """- Куда идем мы с Пятачком - большой, большой секрет!
- Ой, Винни, а я бумагу забыл взять!""",
           '''Заблудился Геолог в тайге, кричит: "Люди! Где вы!? Помогите!"
Выходит из-за дерева Чукча и говорит демоническим голосом:
"А, как здесь - так "люди!", а как в Москве - так "сковородки с ушами"!"''',
           '''Поручик Ржевский танцует на балу с Наташей Ростовой.
- Поручик, - удивляется Наташа, - почему вы гладите меня по спине?
- Пытаюсь найти ваши груди, мадемуазель.
- Но ведь они у меня спереди!
- Да там я уже искал-с!''',
           '''Прапорщик объясняет новобранцам:
- Если камень подбросить, он упадет на землю - на него действует сила земного притяжения.
- А если он упадет в воду? - спрашивает новичок.
- Это нас не касается, этим занимаются на флоте.''',
           '''Приземляется парапланеристка:
- Ой, так ударилась, чуть ноги не переломала!
Инструктор посмотрел и говорит:
- Ну-у, переломать не переломала, но погнула капитально.''',
           '''- Официант! Этот бифштекс из конины?
- Нет, сэр, бифштекс не из конины: кони кончились! Этот бифштекс из телеги!''',
           '''Новый русский едет со своей девушкой в Мерсе.
- Смотри, я щас на красный свет проеду!
И проезжает на полной скорости. Девушка в восторге.
На следующем перекрестке останавливается, несмотря на то, что горит зеленый свет.
Девушка:
- Ты чего?
- Да вот щас такой же джигит поедет...''',
           '''Исповедуется друг алкоголика:
- Я не люблю напиваться в присутствии жены, неприятно видеть, как их становится двое...''',
           '''Нищий стучится в дом.
- Мадам, я уже три дня не видел мяса.
- Сара, покажи ему котлету.''',
           '''Приезжает ковбой в город и останавливается в крутой гостинице. Там все как положено, сауна, бассейн. И вдруг на третий день его к этому бассейну инструктор не допускает:v - Почему меня не пускают. Я за все уплатил.
- Да, сэр, но вы писаете в воду!
- Ну и что, так делают почти все!
- Да, но вы один делаете это с вышки.''',
           '''Чапаев ездил поступать в военную академию.
- Василий Иваныч, все сдал?
- Нет, не все, Петька. Кровь сдал, мочу сдал, а математику не смог.''',
           '''Зона. 8 часов утра. Перекличка. Начальник сообщает заключенным:
- С сегодняшнего дня наша зона перешла на трехразовое усиленное питание!
- Ур-р-ра! - кричат зеки.
- Вторник, четверг, суббота!''',
           '''Студент хнычет:
- Профессор, я не заслуживаю двойки! Профессор:
- Знаю... Но более низких оценок у нас, к сожалению, нет!''',
           '''У одного чукчи сломался будильник. Приходит он в часовую мастерскую, где приемщик тоже чукча. Открыл он будильник и видит, что в механизме застрял дохлый таракан.
- Не будет работать, - уверенно констатирует он.
- Почему? - удивляется владелец часов.
- Механик сдох! - разводит руками приемщик.''',
           '''Два джентльмена после охоты сидят у камина, вытянув ноги к огню, и молчат:
- Сэр, боюсь, что ваши носки начинают тлеть.
- Вы, вероятное, хотите сказать - сапоги, сэр?
- Нет, сапоги уже давно сгорели, сэр.''',
           '''Служащий опоздал на работу и столкнулся в коридоре со своим шефом:
- Вы опоздали на целых два часа! У вас есть уважительная причина?
- Да, я готовился стать отцом.
- О! Поздравляю... И когда же это случится?
- Месяцев через девять...''',
           '''На экзамене профессор спрашивает студента:
- Скажите, почему я Вас не видел ни на одной лекции?
- Да я все время за колонной сидел.
- Никогда бы не подумал, что за одной колонной могут сидеть столько человек!''',
           '''- Где вы бы посоветовали нам поставить палатки? - спрашивают туристы местного жителя.
- Внизу, на лугу. Там уже стоит около десятка палаток.
- А какие-нибудь развлечения в вашей округе есть?
- Да, раз в неделю я выпускаю на луг своего быка.''',
           '''- Потерпевший, узнаете ли вы человека, который угнал у вас машину?
- Ваша честь, после речи его адвоката, я вообще не уверен, была ли у меня машина.''',
           '''Пьяный никак не может затолкнуть двушку в прорезь автомата.
- Напился, - а еще таксист, - сказала прохожая.
- С чего взяла?
- Шапка таксистская.
- Да, - задумчиво произнес пьяный, - а была ондатровая.''',
           '''Комментатор футбольного матча по радио:
- Родригес выходит к воротам. Удар головой - штанга!
Еще удар головой - штанга! Опять удар головой - штанга!!!... v Дайте ему, наконец, мяч или как-нибудь прекратите эту истерику!''',
           '''Один новый русский решил по старой доброй памяти покататься в троллейбусе. Но у него ничего не вышло: "Мерседес" в троллейбус не влез...''',
           '''- Послушайте, официант, вы принесли мне омара без одной клешни.
В чем дело?
- Видите ли, сэр, эти омары такие свежие, что не успели их доставить сюда, как они устроили на кухне настоящую драку друг с другом...
- Тогда заберите этого и принесите мне победителя!''',
           '''Мужик долго не был дома, приехал, стучит в дверь костяшками пальцев - никто не открывает. Он стучит кулаком - все равно не открывают. Он ногой - без результата. Тут соседка высовывается из-за двери:
- А ты рогами, рогами постучи!''',
           '''Едет по лесу генеральская машина, половину штаба везет на заседание к другой половине. Колея узкая такая. Вдруг видят впереди ГАЗ-66 буксует. Застрял, значит. Ну генерал подходит к водителю: мол освобождай дорогу. А тот ему:
Не могу, товарищ генерал. Застрял. А если вам ехать надо, так толкайте.
Вытолкал генерал со штабом ГАЗ и говорит, вытирая пот: "Ну и тяжелая у тебя машина". На что водитель делает добрые глаза и отвечает:
Конечно тяжелая - 20 дебелей домой везу.''',
           '''Проходит футбольный матч между слонами и муравьями. Ну соответственно слоны выиграли. После окончания игры капитан слонов подходит к капитану муравьев и говорит:
- Извини, понимаешь, мы сегодня столько ваших затоптали.
- Ничего, мы тоже грубо играли.''',
           '''Полночь. Морг. Санитары сидят в подсобке и дринчат казенный спирт. В секционной дежурит бедный студент. Вдруг он с позеленевшим лицом влетает в подсобку: Там... Там... Встревоженные санитары: Что? Там покойник ожил!!!!!
Итить твою мать, что людей пугаешь. Мы уж испугались - подумали главврач с проверкой.''',
           '''Два студента заключили пари. Пришли на остановку такси.
- Скажи, водитель, какая цена до ул. Горького?
- Червонец.
- А если я с другом?
- Червонец.
- Видишь, Вася, я же говорил тебе, что ты ничего не стоишь.''',
           '''Стоят на посту двое гаишников - старый и молодой. Старый ушел в будку погреться, а молодой остановил водителя за превышение скорости. Водитель прилепил гаишнику 25 рублей на лоб и со словами "Подавись, собака" поехал дальше. Тот пришел в будку и рассказал все старому. Старый отлепил четвертной со лба молодого, положил в карман и говорит:
- Это я собака, а ты еще щенок!''',
           '''Сели играть в карты Волк, Медведь, Заяц и Лиса.
Медведь раздал карты и говорит:
- Играть честно, а кто будет хитрить, получит по РЫЖЕЙ и НАГЛОЙ МОРДЕ!!!''',
           '''Поймал Старик золотую рыбку, а она ему и говорит:
-Слушай, Дед, твоя Старуха еще жива?
-Жива.
-Ну, тогда лучше сразу в уху!''',
           '''Однажды Чукча купил автомобиль. Приехал на нем к себе в стойбище. Высыпал народ, любуется. Один Чукча протер фары:
- Однако, какие большие глаза!
Другой похлопал по крыше:
- Однако, какая крепкая шкура!
Третий подергал за выхлопную трубу:
- Однако, - самец!''',
           '''Инструктор по физической подготовке старался вызвать y группы новобранцев интерес к спорту, расхваливая свои физические возможности. Он рассказал им, как однажды переплыл широкую реку три раза подряд. Из группы послышался смех.
- Что здесь смешного? - обиженно спросил инструктор.
- Извините, сэр, - ответил один солдат, - но мне показалось странным, почему вы не переплыли реку в четвертый раз и не вернулись на тот берег, где оставили одежду.''',
           '''Маленькая Катя рассматривает семейный альбом.
- Мамочка, - кричит она. - Кто этот кудрявый красавец с черной бородкой?
- Это твой папа.
- Что ты говоришь? А кто же тогда этот лысый человек с седой щетиной, который живет с нами?''',
           '''Заловили бандиты в парке парня и говорят ему:
- Ну, все, пиши завещание ЩА положим!...
Он:
- Ребят, вас много, все равно положите, дайте размяться.
- Ну, разминайся...
Парень начинает приседать, прыгать и т.д.
Они:
- Эээ, чувак, ты боксер, что ли?
- Да неееет, бегун...''',
           '''Новый русский покупает квартиру и спрашивает:
- А это тихая квартира?
- Очень тихая! Предыдущего владельца пристрелили - так никто и не услышал!''',
           '''Час пик. Два наркомана сидят в троллейбусе. Подходит старушка.
- Сыночек, и как вам не стыдно! Уступили бы место.
Один начинает вставать. Другой ему:
- Сиди, Серега! Я эту наколку знаю: ты встанешь - она сядет!''',
           '''Мужчина в обеих руках несет бутылки. Приятель его спрашивает:
- Ты что, тару несешь сдавать?
- Нет, с женой поругался, так она сказала: забирай свои вещи и уходи.''',
           '''У хирурга.
- Сестра, что у нас сегодня?
- Два легких случая: автокатастрофа, производственная травма. И один тяжелый - муж, отказавшийся мыть посуду.''',
           '''Начальник - секретарше:
- Вы уволены!
- Почему, шеф? Я вас уважаю и люблю.
- Во время уважения вы мне кое-что подарили, чем я успел поделиться с женой!''',
           '''Новый русский в больнице весь побитый, перебинтованный. Больные его спрашивают:
- Что случилось-то?
- Дык, еду я на своём "Мерсе" под 180, гляжу, блин, впереди - мужик на лошади прёт. Ну, я по тормозам, но не успел - кааааак въехал, прям в него - "Мерс" вдребезги, так жалко машину...
- Ну, а мужик-то жив или нет?
- Дык ему то что - он же бронзовый.''',
           '''Двое пьяных прут вечером по улице. Один:
- Вась! Видишь - впереди еврей идет. Давай ему морду набьем!
- Да ну! Он здоровый, еще нам набьет!
- А нам то за что?!''',
           '''- Почему ваши дети все время ссорятся?
- Конфликт версий, - отвечает программист.''',
           '''В зоомагазине:
- Слышал, вчера у вас были в продаже говорящие попугаи. Может найдете одного? Уплачу как за двоих.
- К сожалению, попугаев уже не осталось, но есть очень толковый дятел. Он знает азбуку Морзе!''',
           '''Построил Чапаев дивизию и говорит:
- Солдаты! Как вы думаете, птицам деньги нужны?
- Нет!
- Так вот, орлы, я пропил вашу зарплату!!!
Подбегает Анка:
- И мою, Василь Иваныч?!
- И твою, ласточка, тоже...''',
           '''Криминальная хроника. В городе Леворукске был закрыт склад поддельной виагры.
Склад удалось обнаружить при помощи специально обученных импотентов.''',
           '''В трамвае в час пик ужасная давка. Девушка обращается к стоящей рядом маме:
- Знаешь, мама, у меня, кажется, будет маленький ребенок...
- От кого, доченька?
- Не знаю, не могу оглянуться.''',
           '''Матрос спрашивает капитана, старого морского волка: - Капитан, а правда, что вас акула укусила?
Правда, матрос!
- А куда?
- А вот это - неправда!..''',
           '''Адвокат выступает в суде:
- Господа присяжные заседатели! Сам факт того, что обвиняемый выбрал меня своим адвокатом, свидетельствует о его полной невменяемости.''',
           '''Вовочка спрашивает отца-метеоролога:
- Папа, а твои прогнозы всегда сбываются?
- Всегда. Только даты не всегда совпадают.''',
           '''В кабинет гинеколога входит женщина:
- Доктор, я у вас трусы не оставила?
- Нет.
- Тогда извините. Значит, у окулиста...''',
           '''В зоопарке ребенок, возбужденно тыча пальцем на клетку с приматами, кричит:
- Мама! Мама! Смотри - программисты!
- Почему ты так решил?
- Они как папа! - не мытые, лохматые и мозоль на попе!''',
           '''Шериф испытывает нового помощника. Стреляет в него с пяти метров из двух кольтов. Прострелил шляпу и пиджак. Помощник не шелохнулся.
- Молодец Билл! Пиджак и шляпу я куплю тебе новые.
- Неплохо было бы купить и новые штаны.''',
           '''Покупатель:
- Я не могу спать по ночам, меня беспокоит малейший звук, я жертва бессонницы. Тот проклятый кот, что кричит под моим окном, просто доконал меня.
Аптекарь:
- Вот этот порошок очень эффективен.
- А когда мне его принимать?
- Это не для вас, дайте его коту.''',
           '''- Василий Иванович, ты бы бросил курить.
- Не знаю я, Петька, как от этой заразы избавиться.
- А ты бы конфеты купил. Говорят, помогают.
- Пробовал, не горят.''',
           '''В тюремном дворе встречаются двое заключенных, ненавидящих друг друга. Один осужден за увод коровы, другой - за кражу наручных часов. При встрече один с ехидцей спрашивает:
- Который час на ваших новеньких?
- Да уже пора доить вашу корову...''',
           '''Журналист берет интервью у отставного капитана,
- Итак, капитан, вспомните, какую вам пришлось пережить самую страшную бурю в своей жизни? Старый морской волк, после некоторого раздумья:
- Я думаю, что это случилось тогда, когда я плюнул на кухне, которую только что вымыла моя жена!''',
           '''Приятель приятелю:
- Какие у тебя круглые розовые щеки после отпуска! Ты, наверное, очень хорошо питался?
- Нет, мне приходилось каждый день надувать резиновый матрас для жены и тещи.''',
           '''Адвокат:
- Прежде чем огласить завещание господина Смита, я хотел бы задать вопрос его жене: сударыня, не выйдете ли вы за меня замуж?''',
           '''Хирург говорит пациенту, которого готовят к операции:
- Вам совершенно нечего боятся. Это моя шестнадцатая операция, так что должна же она когда-нибудь получиться.''',
           '''Два студента военной кафедры стоят, курят в туалете. Один спрашивает:
- А знаешь, чем наш майор от осла отличается? Из-за спины майорская морда, ехидно:
- Ну и чем же?
- Ничем, товарищ майор!
- Вот. То-то же!'''
           ]
SqlAlchemyBase = dec.declarative_base()
__factory = None
openai.api_key = "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"


def send(message):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=message.text,
        temperature=0.9,
        max_tokens=2000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.6, )
    bot.send_message(message.chat.id, response['choices'][0]['text'])
    start_command(message, rol=1)


def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")
    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from data import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


bot = telebot.TeleBot('5187622946:AAHdoul6bLiS7aAqC0oQdh1l2pyylk7R6RY')
error = """Уважаемый пользователь, к сожалению, ваш запрос не может быть выполнен из-за некорректного ввода данных. Пожалуйста, проверьте правильность введенной информации и повторите попытку."""


# команда /start
@bot.message_handler(commands=['start'])
def start_command(message, rol=0):
    if rol == 0:
        bot.send_message(message.chat.id,
                         f"""Здравствуйте, @{message.from_user.first_name}! Рады приветствовать Вас в нашем телеграмм боте. Мы создали его, чтобы облегчить Вам жизнь и сделать её более интересной и продуктивной. Здесь Вы можете получить доступ к множеству полезных функций, а также узнать много всего нового. Мы надеемся, что использование нашего бота станет для Вас приятным и удобным, и Вы найдете здесь все, что Вам нужно. Желаем приятного использования нашего телеграмм бота!""")
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Математика', 'История')
    keyboard.row('Анекдот', 'ChatGPT')
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=keyboard)
    bot.register_next_step_handler(message, decide)


def decide(message):
    if message.text == 'Математика':
        dice_function(message)
    if message.text == 'История':
        tice_function(message)
    if message.text == 'Анекдот':
        qice_function(message)
    if message.text == 'ChatGPT':
        bot.send_message(message.chat.id, 'Напишите запрос')
        bot.register_next_step_handler(message, send)


def qice_function(message):
    global anecdot
    bot.send_message(message.chat.id, choice(anecdot))
    start_command(message, rol=1)


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
        start_command(message, rol=1)
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


bot.polling(none_stop=True)
