import sqlite3

class PurchasesTable:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def add_purchase(self, user_id, game_id, purchase_date):
        self.cursor.execute('''INSERT INTO purchases (user_id, game_id, purchase_date)
                               VALUES (?, ?, ?)''', (user_id, game_id, purchase_date))
        self.conn.commit()
        print(f"Покупка пользователя с user_id {user_id} для игры с game_id {game_id} добавлена в таблицу.")

    def update_purchase(self, purchase_id, new_data):
        update_query = "UPDATE purchases SET "
        update_values = []

        for field, value in new_data.items():
            update_query += f"{field} = ?, "
            update_values.append(value)

        update_query = update_query.rstrip(", ")
        update_query += " WHERE purchase_id = ?"
        update_values.append(purchase_id)

        self.cursor.execute(update_query, update_values)
        self.conn.commit()
        print(f"Данные покупки с purchase_id {purchase_id} обновлены.")

    def delete_purchase(self, purchase_id):
        self.cursor.execute('''DELETE FROM purchases WHERE purchase_id = ?''', (purchase_id,))
        self.conn.commit()
        print(f"Покупка с purchase_id {purchase_id} удалена из таблицы.")

    def __del__(self):
        self.conn.close()
