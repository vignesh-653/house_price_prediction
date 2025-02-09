import os
import psycopg2
import json
import time

class DatabaseManager:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME", "fastapi_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "yourpassword")
        self.host = os.getenv("DB_HOST", "db")
        self.port = os.getenv("DB_PORT", "5432")
        self.connection = None

    # def connect(self):
    #     retries = 5
    #     while retries > 0:
    #         try:
    #             self.connection = psycopg2.connect(
    #                 dbname=self.db_name,
    #                 user=self.user,
    #                 password=self.password,
    #                 host=self.host,
    #                 port=self.port
    #             )
    def connect(self):
        retries = 5
        while retries > 0:
            try:
                self.connection = psycopg2.connect(
                    dbname="HouseDB",
                    user="postgres",
                    password="1234",
                    host="localhost",
                    port=5432
                )
                self.connection.autocommit = False
                print("Database connection successful.")
                return
            except Exception as e:
                print(f"Error connecting to database: {e}, retrying...")
                retries -= 1
                time.sleep(5)
        raise Exception("Failed to connect to the database after retries.")


    def create_table(self, table_name, json_file):
        try:
            with open(json_file, 'r') as file:
                schema = json.load(file)

            # Extract the column definitions from the JSON file
            columns = schema.get(table_name, {})
            column_definitions = ", ".join([f"{col} {col_type}" for col, col_type in columns.items()])
            
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"
            
            # Execute the query
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()  # Commit the transaction after table creation
                print(f"Table '{table_name}' created successfully.")
        except Exception as e:
            self.connection.rollback()  # Roll back transaction on failure
            print(f"Error creating table: {e}")

    def insert_data(self, table_name, data):
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = tuple(data.values())
            
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()  # Commit after inserting data
                print("Data inserted successfully.")
        except Exception as e:
            self.connection.rollback()  # Roll back transaction on failure
            print(f"Error inserting data: {e}")

    def close_connection(self):
        if self.connection:
            try:
                self.connection.commit()  # Ensure all changes are saved before closing
                self.connection.close()
                print("Database connection closed.")
            except Exception as e:
                print(f"Error closing the connection: {e}")


    def login_check(self, user_name, password ,table_name='users'):
        try:
            query = f"SELECT username FROM {table_name} WHERE username = %s AND password = %s"
            with self.connection.cursor() as cursor:
                cursor.execute(query, (user_name, password))
                result = cursor.fetchone()
                if result:
                    return "good"
                else:
                    return "bad"
        except Exception as e:
            print(f"Error closing the connection: {e}")


    def register_user(self, user_name, password, table_name='users'):
        columns = ["username", "password"]        
        placeholders = ", ".join(["%s"] * len(columns))
        values = (user_name,password)
        try:
           query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
           with self.connection.cursor() as cursor:
                cursor.execute(query, values)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()  # Roll back transaction on failure
            print(f"Error inserting data: {e}")
        
            
    def create_users_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
            """
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                print("Users table created successfully (if not already existing).")
        except Exception as e:
            self.connection.rollback()
            print(f"Error creating users table: {e}")

