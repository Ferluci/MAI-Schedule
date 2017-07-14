# MAI-Schedule
Бот для телеграмма, показывающий расписание, оповещающий о следующих парах и вообще прикольная утилита для настоящего маёвца!

# Переезд на личный репозиторий
Кажется я дошел до той точки, когда можно сказать, что не имеет смысла быть форком и проще стать отдельным репозиторием. Сергей все равно никогда не откажется от своего кода, а мне легче развивать бота, как своего личного. На том и разойдемся.

# V 2.1
- Переписан весь функционал бота
- За основу GUI взята схема murych
- Функционал разбит на 3 отдельных модуля:
  * db_manage.py - работа с бд
  * dates.py - разбота с датой и временем
  * bot.py - основной функционал бота, который использует функции из db_manage.py и dates.py
- Теперь расписание не парсится каждый раз при запросе пользователя, а запрашивается из таблицы бд
- Также была добавлена лицензия, после того как я узнал, что мое имя, наглым образом, не показывается в именах разработчиков бота
- Все написано соблюдая стандарты PEP8

# TODO
- Учитывать дни военной подготовки
- Красивый вывод расписания:
    * Добавить через регулярки наличие определенных полей
- Написать декоратор в bd_manage.py, который бы обеспечивал работу с курсором
- Вывод сообщения о Каникулах (в дальнейшем планируется расписание каникул)
- Закомментировать код
- Уведомления об экзаменах
- Возможно будет пересмотрена организация базы данных, на примере http://www.cyberforum.ru/database/thread826510.html
