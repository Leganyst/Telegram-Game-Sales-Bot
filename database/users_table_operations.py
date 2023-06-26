import sqlite3

class UsersTable:
    def __init__(self):
        self.conn = sqlite3.connect('game_store.db')
        self.cursor = self.conn.cursor()
    
    def add_user(self, user_id, user_link, is_admin=False):
        query = "INSERT OR IGNORE INTO users (user_id, user_link, is_admin) VALUES (?, ?, ?);"
        values = (user_id, user_link, is_admin)
        self.conn.execute(query, values)
        self.conn.commit()

    def update_admin_status(self, user_id, is_admin):
        query = "UPDATE users SET is_admin = ? WHERE user_id = ?;"
        values = (is_admin, user_id)
        self.conn.execute(query, values)
        self.conn.commit()

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = ?;"
        values = (user_id,)
        self.conn.execute(query, values)
        self.conn.commit()

    def get_user_by_id(self, user_id):
        self.cursor.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
        user_data = self.cursor.fetchone()

        if user_data:
            user = {
                'user_id': user_data[0],
                'user_link': user_data[1],
                'is_admin': bool(user_data[2])
            }
            return user
        else:
            return None

    def __del__(self):
        self.conn.close()