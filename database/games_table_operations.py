import sqlite3

class GamesTable:
    def __init__(self):
        self.conn = sqlite3.connect('game_store.db')
        self.cursor = self.conn.cursor()

    def add_game(self, name, price, description, genre, photos=None):
        photos_str = ','.join(photos) if photos else None
        self.cursor.execute('''INSERT INTO games (name, price, description, genre_id, photos)
                               VALUES (?, ?, ?, ?, ?)''', (name, price, description, genre, photos_str))
        self.conn.commit()
        print(f"Игра '{name}' добавлена в таблицу.")

    def update_game_photos(self, game_id, photos):
        photos_str = ','.join(photos) if photos else None
        self.cursor.execute('''UPDATE games SET photos = ? WHERE game_id = ?''', (photos_str, game_id))
        self.conn.commit()
        print(f"Фотографии игры с ID {game_id} обновлены.")

    def update_game(self, game_id, new_data):
        update_query = "UPDATE games SET "
        update_values = []

        for field, value in new_data.items():
            update_query += f"{field} = ?, "
            update_values.append(value)

        update_query = update_query.rstrip(", ")
        update_query += " WHERE game_id = ?"
        update_values.append(game_id)

        self.cursor.execute(update_query, update_values)
        self.conn.commit()
        print(f"Данные игры с game_id {game_id} обновлены.")

    def delete_game(self, game_id):
        self.cursor.execute('''DELETE FROM games WHERE game_id = ?''', (game_id,))
        self.conn.commit()
        print(f"Игра с game_id {game_id} удалена из таблицы.")

    def select_rows(self, limit=5, offset=0):
        # выполнить запрос с заданными limit и offset
        self.cursor.execute(f"SELECT * FROM games LIMIT {limit} OFFSET {offset};")
        # получить результаты запроса
        rows = self.cursor.fetchall()
        # вернуть результаты
        return rows

    def select_rows_by_genre(self, genre_id, limit=5, offset=0):
        # Выполнить запрос с указанным genre_id, limit и offset
        self.cursor.execute(f"SELECT * FROM games WHERE genre_id = {genre_id} LIMIT {limit} OFFSET {offset};")
        # Получить результаты запроса
        rows = self.cursor.fetchall()
        # Вернуть результаты
        return rows

    def get_game_by_id(self, game_id):
        self.cursor.execute('''SELECT * FROM games WHERE game_id = ?''', (game_id,))
        game_data = self.cursor.fetchone()

        if game_data:
            game = {
                'game_id': game_data[0],
                'name': game_data[1],
                'price': game_data[2],
                'description': game_data[3],
                'genre_id': game_data[4],
                'photos': game_data[5].split(',') if game_data[5] else []
            }
            return game
        else:
            return None


    def __del__(self):
        self.conn.close()
