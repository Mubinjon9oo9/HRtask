import sqlite3
import csv

def connect_db(db_name='requests.db'):
    conn = sqlite3.connect(db_name)
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT ,
            mail TEXT,
            q1 TEXT,
            q2 TEXT,
            q3 TEXT,
            q4 TEXT,
            q5 TEXT,
            q6 TEXT,
            q7 TEXT,
            q8 TEXT,  
            q9 TEXT,    
            q10 TEXT
        )
    ''')
    # Создаём новую таблицу для статусов прохождения опроса
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_status (
            user_id INTEGER PRIMARY KEY,
            started_at TEXT,
            finished_at TEXT,
            status TEXT -- started, positive, negative
        )
    ''')
    conn.commit()
    conn.close()

def save_response(question, answer):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO responses (question, answer) VALUES (?, ?)
    ''', (question, answer))
    conn.commit()

def update_column_by_name(user_id, column_name, value):
    conn = connect_db()
    cursor = conn.cursor()
    query = f'''
        UPDATE responses
        SET {column_name} = ?
        WHERE id = ?
    '''
    cursor.execute(query, (value, user_id))
    conn.commit()
    conn.close()

def fetch_responses(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM responses')
    return cursor.fetchall()

def close_db(conn):
    conn.close()

def add_user_with_empty_values(user_id):
    if not get_user_by_id(user_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO responses (id, name, phone, mail, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10)
            VALUES (?, '', '', '', '', '', '', '', '', '', '', '', '', '')
        ''', (user_id,))
        conn.commit()
        conn.close()

def get_user_by_id(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM responses WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def export_to_csv(file_name='responses_export.csv'):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM survey_status')
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    with open(file_name, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(rows)
    conn.close()
    print(f"Данные успешно экспортированы в файл {file_name}")

def mark_survey_started(user_id):
    """Сохраняет факт начала опроса пользователем."""
    from datetime import datetime
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO survey_status (user_id, started_at, status)
        VALUES (?, ?, ?)
    ''', (user_id, datetime.now().isoformat(), 'started'))
    conn.commit()
    conn.close()

def mark_survey_finished(user_id, is_positive):
    """Сохраняет результат завершения опроса пользователем."""
    from datetime import datetime
    conn = connect_db()
    cursor = conn.cursor()
    status = 'positive' if is_positive else 'negative'
    cursor.execute('''
        UPDATE survey_status
        SET finished_at = ?, status = ?
        WHERE user_id = ?
    ''', (datetime.now().isoformat(), status, user_id))
    conn.commit()
    conn.close()

create_table()