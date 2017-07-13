# -*- coding: utf8 -*-


'''
Copyright (c) 2017 Anischenko Konstantin Maximovich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from time import sleep
from requests import get
from sqlite3 import connect
from bs4 import BeautifulSoup


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.groups = tuple(self.get_groups())

    def create_users_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Users(id Integer, name char(20), group_name char(20))")
        con.close()

    def create_groups_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Groups(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20))")
        con.commit()
        con.close()

    def create_session_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Session(" +
                    "id Integer  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20), " +
                    "date char(8), " +
                    "time char(15), " +
                    "subject char(70), " +
                    "teacher char(70), " +
                    "location char(25))")
        con.commit()
        con.close()

    def create_scheldule_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Scheldule(" +
                    "id Integer  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20), " +
                    "week_type Integer, " +
                    "day char(2), " +
                    "time char(15), " +
                    "lesson_type char(2), " +
                    "subject char(70), " +
                    "teacher char(70), " +
                    "location char(25))")
        con.commit()
        con.close()

    def _parse_groups(self):
        target_url = 'https://www.mai.ru/education/schedule'
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        groups = []
        for group in soup.find_all('a', class_="sc-group-item"):
            group = group.get_text()
            groups.append(group)
        return groups

    def _parse_session(self, group_name):
        target_url = "https://www.mai.ru/" +\
                     "education/schedule/session.php?group=" +\
                      group_name
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        exams = []
        for exam in soup.find_all('div', class_="sc-container"):
            exam = exam.get_text().split('\n')
            for i in range(exam.count('')):
                exam.pop(exam.index(''))
            exams.append(exam)
        return exams

    def _parse_scheldule(self, group_name, week_number):
        target_url = "http://www.mai.ru/" +\
                     "education/schedule/detail.php?group=" +\
                      group_name + '&week=' + str(week_number)
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        result = []
        for day in soup.find_all('div', class_="sc-container"):
            day = day.get_text().split('\n')
            day = [x for x in day if x != '']
            result.append(day)
        return result

    def fill_groups_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        group_list = self._parse_groups()
        for group in group_list:
            cur.execute('INSERT INTO Groups (group_name) VALUES (?)', [group])
        con.commit()
        con.close()

    def fill_session_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        for group in self.groups:
            session = self._parse_session(group)
            for exam in session:
                date = exam[0]
                time = exam[1]
                subject = exam[3]
                teacher = exam[4]
                location = exam[5].replace(u'\xa0', u'')
                cur.execute("INSERT INTO Session " +
                            "(group_name, date, time," +
                            " subject, teacher, location) " +
                            "VALUES (?, ?, ?, ?, ?, ?)",
                            [group, date, time, subject, teacher, location])
                con.commit()

            sleep(0.5)
        con.commit()
        con.close()

    def _fill_week(self, week, group, week_type):
        con = connect(self.db_name)
        cur = con.cursor()
        for day in week:
            date = day[0][-2:]
            day.pop(0)
            for i in range(0, len(day)-4, 5):
                time = day[i]
                lesson_type = day[i+1]
                subject = day[i+2]
                teacher = day[i+3]
                location = day[i+4].replace(u'\xa0', u'')
                cur.execute("INSERT INTO Scheldule " +
                            "(group_name, week_type, day," +
                            " time, lesson_type, subject, " +
                            "teacher, location) " +
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            [group, week_type, date,
                             time, lesson_type, subject, teacher, location])
                con.commit()
        con.close()

    def fill_scheldule_table(self):
        for group in self.groups:

            down_week = self._parse_scheldule(group, 4)
            up_week = self._parse_scheldule(group, 5)

            self._fill_week(up_week, group, 0)
            self._fill_week(down_week, group, 1)

            sleep(0.5)

    def get_groups(self):
        con = connect(self.db_name)
        cur = con.cursor()
        groups_list = []
        for row in cur.execute("SELECT group_name FROM Groups"):
            groups_list.append(row[0])
        con.close()
        return groups_list

    def check_id(self, id):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE id=?", [id])
        result = cur.fetchone()
        return result

    def get_group(self, id):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT group_name FROM Users WHERE id=?", [id])
        group = cur.fetchone()
        if group is not None:
            group = group[0]
        return group

    def get_session(self, group):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT date, time, subject, "
                               "teacher, location " +
                               "FROM Session WHERE group_name=?",
                               [group]):
            result.append(list(row))
        con.close()
        return result

    def get_week_scheldule(self, group, week_type):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT day, time, lesson_type, subject, " +
                               "teacher, location FROM Scheldule WHERE " +
                               "group_name=? AND week_type=?",
                               [group, week_type]):
            result.append(list(row))
        con.close()
        return result

    def get_day_scheldule(self, group, week_type, day):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT time, lesson_type, subject," +
                               "teacher, location FROM Scheldule WHERE " +
                               "group_name=? AND week_type=? AND day=?",
                               [group, week_type, day]):
            result.append(list(row))
        con.close()
        return result

    def insert_user(self, id, name, group=None):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Users (id, name, group_name) " +
                    "VALUES (?, ?, ?)",
                    [id, name, group])
        con.commit()
        con.close()

    def update_group(self, id, group):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute('UPDATE Users SET group_name=? WHERE id=?',
                    [group, id])
        con.commit()
        con.close()


if __name__ == '__main__':
    pass