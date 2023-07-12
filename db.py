import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_coin(self, user_id, name, description, image):
        """Создаем запись о монете"""
        self.cursor.execute("INSERT INTO `coins` (`users_id`, `name`, `description`, `img`) VALUES (?, ?, ?, ?)",
            (self.get_user_id(user_id),
            name,
            description,
            image))
        return self.conn.commit()

    def get_coins(self, user_id, name):
        """Получаем монеты"""
        
        result = self.cursor.execute("SELECT * FROM `coins` WHERE `users_id` = ? AND `name` = ?",
            (self.get_user_id(user_id), name,))
        if result is None:
            return None
        else:
            return result.fetchall()

    def get_coin_names(self, user_id):
        """Получаем имя и кол-во монет"""
        result = self.cursor.execute("SELECT name, COUNT(*) FROM `coins` WHERE `users_id` = ? GROUP BY name",
            (self.get_user_id(user_id), ))
    
        if result is None:
            return None
        else:
            return result.fetchall()

    

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()