import sqlite3

class GenresTable:
    def __init__(self):
        self.connection = sqlite3.connect("game_store.db")
        self.cursor = self.connection.cursor()

    def add_genre(self, name):
        self.cursor.execute("INSERT INTO genres (name) VALUES (?)", (name,))
        self.connection.commit()
        print("Жанр успешно добавлен.")
        

    def get_genre_name(self, genre_id):
        query = "SELECT name FROM genres WHERE genre_id = ?"
        self.cursor.execute(query, (genre_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def get_all_genres(self):
        query = "SELECT genre_id, name FROM genres"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def has_genres(self):
        query = "SELECT COUNT(*) FROM genres"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result and result[0] > 0:
            return True
        else:
            return False

    def delete_genre(self, genre_id):
        try:
            self.cursor.execute("DELETE FROM genres WHERE genre_id=?", (genre_id,))
            self.connection.commit()
            print("Жанр успешно удален.")
        except sqlite3.Error as e:
            print(f"Ошибка при удалении жанра: {e}")

    def __del__(self):
        self.connection.close()
