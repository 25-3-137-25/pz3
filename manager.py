import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, config: dict = None):
        self.config = config or {
            'host': 'idk',
            'user': 'idk',
            'password': 'idk',
            'database': 'idk',
            'connection_timeout': 900,
        }
        self.connection = None
        self.cursor = None
        self._connect()

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("Подключение к БД установлено")
        except Error as e:
            print(f"Ошибка подключения: {e}")
            raise

    def _ensure_connection(self):
        if not self.connection or not self.connection.is_connected():
            self._connect()

    def create(self, table: str, data: dict) -> int:
        self._ensure_connection()
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            print(f"Запись добавлена в таблицу '{table}'")
            return self.cursor.lastrowid
        except Error as e:
            self.connection.rollback()
            print(f"Ошибка CREATE: {e}")
            raise

    def read(self, table: str, columns: list = None, conditions: dict = None,
             order_by: str = None, limit: int = None) -> list:
        self._ensure_connection()
        try:
            cols = ', '.join(columns) if columns else '*'
            query = f"SELECT {cols} FROM {table}"
            params = []
            if conditions:
                where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                query += f" WHERE {where_clause}"
                params = list(conditions.values())
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            print(f"Прочитано {len(result)} записей из '{table}'")
            return result
        except Error as e:
            print(f"Ошибка READ: {e}")
            raise

    def update(self, table: str, data: dict, conditions: dict) -> int:
        self._ensure_connection()
        try:
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            params = list(data.values()) + list(conditions.values())
            self.cursor.execute(query, params)
            self.connection.commit()
            print(f"Обновлено {self.cursor.rowcount} записей в '{table}'")
            return self.cursor.rowcount
        except Error as e:
            self.connection.rollback()
            print(f"Ошибка UPDATE: {e}")
            raise

    def delete(self, table: str, conditions: dict) -> int:
        self._ensure_connection()
        try:
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
            query = f"DELETE FROM {table} WHERE {where_clause}"
            self.cursor.execute(query, list(conditions.values()))
            self.connection.commit()
            print(f"Удалено {self.cursor.rowcount} записей из '{table}'")
            return self.cursor.rowcount
        except Error as e:
            self.connection.rollback()
            print(f"Oшибка DELETE: {e}")
            raise

    def execute_query(self, query: str, params: tuple = None) -> list:
        self._ensure_connection()
        try:
            self.cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                result = self.cursor.fetchall()
                print(f"Выполнен SELECT, найдено {len(result)} записей")
                return result
            else:
                self.connection.commit()
                print(f"Выполнен запрос, затронуто {self.cursor.rowcount} записей")
                return self.cursor.rowcount
        except Error as e:
            self.connection.rollback()
            print(f"Ошибка запроса: {e}")
            raise

    def table_exists(self, table: str) -> bool:
        self._ensure_connection()
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = %s AND table_name = %s",
                (self.config['database'], table)
            )
            return self.cursor.fetchone()['COUNT(*)'] > 0
        except Error as e:
            print(f"Ошибка проверки таблицы: {e}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Соединение закрыто")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()