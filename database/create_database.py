import sqlite3

# Создание базы данных и подключение к ней
conn = sqlite3.connect('game_store.db')
cursor = conn.cursor()

# Создание таблицы users
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_link TEXT,
            is_admin BOOLEAN DEFAULT 0);""")

# Создание таблицы жанров (genres)
cursor.execute('''CREATE TABLE IF NOT EXISTS genres
 (genre_id INTEGER PRIMARY KEY, name TEXT UNIQUE);''')

# Создание таблицы игр (games) и связь с таблицей жанров (genres)
cursor.execute('''CREATE TABLE IF NOT EXISTS games
 (game_id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT, genre_id INTEGER,
 photos TEXT, FOREIGN KEY (genre_id) REFERENCES genres(genre_id));''')

# Создание таблицы purchases
cursor.execute('''CREATE TABLE IF NOT EXISTS purchases
                  (purchase_id INTEGER PRIMARY KEY, user_id INTEGER, game_id INTEGER, purchase_date TEXT,
                   FOREIGN KEY(user_id) REFERENCES users(user_id),
                   FOREIGN KEY(game_id) REFERENCES games(game_id))''')

# Сохранение изменений и закрытие соединения с базой данных
conn.commit()
conn.close()
