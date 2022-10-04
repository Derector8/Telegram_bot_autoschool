'''Все функции, связанные с базой данных'''
import sqlite3

def checkUser(update, context):
    'Проверяет есть ли пользователь в базе. Если есть - пишет кто он, если нет - создаёт запись в базе'
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cur = conn.cursor()
    conn.text_factory = str
    if len(cur.execute('''SELECT id FROM users WHERE id = ?        
            ''', (update.message.from_user.id,)).fetchall())>0:
        c=cur.execute('''SELECT Имя FROM users WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        context.user_data['Имя']=c[0]
        c=cur.execute('''SELECT Фамилия FROM users WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        context.user_data['Фамилия']=c[0]
        state = 'Зарегистрированный пользователь'
    else:
        cur.execute('''INSERT OR IGNORE INTO users (id, firstname) VALUES (?, ?)''',
        (update.message.from_user.id, update.message.from_user.first_name,))
        state = 'Новый пользователь'
    conn.commit()
    conn.close()
    return state

def user_name(ID, name, surname):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET Имя = "{name}",Фамилия = "{surname}" WHERE id = {ID} ')
    conn.commit()
    conn.close()

def instructor_surname(update,context):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cur = conn.cursor()
    c = cur.execute('''SELECT Фамилия FROM users WHERE id = ?''', (update.message.from_user.id,)).fetchone()
    context.user_data['Фамилия'] = c[0]
    conn.commit()
    conn.close()


def add_teoria(id: int, Instructor: str = None, Uchenik: str = None, Grupa: str = None):
    '''Добавляет ученика в базу данных teoria'''
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT INTO teoria (id,Instructor,Uchenik,Grupa) VALUES (?, ?, ?, ?)',
              (id,Instructor,Uchenik,Grupa))
    conn.commit()
    conn.close()


def add_vozdenie(id: int, Instructor: str = None, Uchenik: str = None, Grupa: str = None):
    '''Добавляет ученика в базу данных vozdenie'''
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT INTO vozdenie (id,Instructor,Uchenik,Grupa) VALUES (?, ?, ?, ?)',
              (id,Instructor,Uchenik,Grupa))
    conn.commit()
    conn.close()

def check_students_teoria(ID):
    '''Получает из базы список учеников на теорию, отправленных запрашивающим пользователем'''
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    stroka = 'Список на теорию:\n\n'
    count = 1
    students = c.execute(f'SELECT Instructor,Uchenik,Grupa,student_id FROM teoria WHERE id = {ID}').fetchall()
    for one in students:
        stroka += str(count) + ') Инструктор: ' + str(one[0])+ '\nУченик: ' + str(one[1])+ '\nГруппа: ' + str(one[2]) + '\nНомер в списке:' + str(one[3]) + '\n\n'
        count += 1
    conn.close()
    return stroka


def check_students_vozdenie(ID):
    '''Получает из базы список учеников на вождение, отправленных запрашивающим пользователем'''
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    stroka = 'Список на вождение:\n\n'
    count = 1
    students = c.execute(f'SELECT Instructor,Uchenik,Grupa,student_id FROM vozdenie WHERE id = {ID}').fetchall()
    for one in students:
        stroka += str(count) + ') Инструктор: ' + str(one[0])+ '\nУченик: ' + str(one[1])+ '\nГруппа: ' + str(one[2]) + '\nНомер в списке:' + str(one[3]) + '\n\n'
        count += 1
    conn.close()
    return stroka


def change_students(table, student_id, data, value):
    '''Функция для изменения данных в таблице по student_id,
    где необходимо передать data-какой столбец изменить и value-на что изменить'''
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute(f'UPDATE {table} SET {data} = "{value}" WHERE student_id = {student_id} ')
    conn.commit()
    conn.close()



if __name__ == '__main__':
    check_students_teoria(336518017)
    print("Проверка списков завершена")
    add_teoria(111,'Болотов','Гусёк Царёк', 'тест007')
    print('Добавление на теорию успешно')
    add_vozdenie(111,'Болотов','Гусёк Царёк', 'тест007')
    print('Добавление на вождение успешно')
    change_students('vozdenie', 1, 'Uchenik', 'Нов Чувак')
    print('Замена совершена успешно')
    print('Всё работает!')


