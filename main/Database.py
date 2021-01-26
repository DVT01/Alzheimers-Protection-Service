import sqlite3
from pathlib import Path

UPDATE_NAME = 'name'
UPDATE_USERNAME = 'username'
UPDATE_EMAIL = 'email'
UPDATE_PASSWORD = 'password'


class Database:
    def __init__(self, db='accounts.db'):
        database = Path(db)
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            '''CREATE TABLE
            IF NOT EXISTS accounts(
            name TEXT, username TEXT, email TEXT, password TEXT
            )'''
        )

    def fetchall(self):
        self.cursor.execute('SELECT * FROM accounts')
        self.connection.commit()
        return self.cursor.fetchall()

    def from_fetchall(self, name):
        self.cursor.execute("SELECT * FROM accounts WHERE name=:name", {
            'name': name
        })
        self.connection.commit()

        return self.cursor.fetchall()

    def get_row_from_index(self, name, row_index):
        for account in enumerate(self.from_fetchall(name)):
            if account[0] == row_index:
                return account[1]
        else:
            raise ZeroDivisionError

    def add_account(self, name, username, email, password):
        self.cursor.execute(
            '''INSERT INTO accounts(name, username, email, password)
            VALUES (:name, :username, :email, :password)''',
            {
                'name': name,
                'username': username,
                'email': email,
                'password': password
            })
        self.connection.commit()

    def delete_account(self, name, row_index):
        chosen_account = self.get_row_from_index(name, row_index)

        self.cursor.execute(
            '''DELETE FROM accounts
            WHERE domain=:account_domain AND username=:username
            AND email=:email AND password=:password''',
            {
                'account_domain': chosen_account[0],
                'username': chosen_account[1],
                'email': chosen_account[2],
                'password': chosen_account[3],
            })
        self.connection.commit()

    def update_account(self, name, row_index, item, change):
        chosen_account = self.get_row_from_index(name, row_index)

        if item == UPDATE_NAME:
            self.cursor.execute(
                '''UPDATE accounts SET name=:new_name
                WHERE name=:name AND username=:username
                AND email=:email AND password=:password''',
                {
                    'new_name': change,
                    'name': chosen_account[0],
                    'username': chosen_account[1],
                    'email': chosen_account[2],
                    'password': chosen_account[3]
                })
        elif item == UPDATE_USERNAME:
            self.cursor.execute(
                '''UPDATE accounts SET username=:new_username
                WHERE name=:name AND username=:username
                AND email=:email AND password=:password''',
                {
                    'new_username': change,
                    'name': chosen_account[0],
                    'username': chosen_account[1],
                    'email': chosen_account[2],
                    'password': chosen_account[3],
                })
        elif item == UPDATE_EMAIL:
            self.cursor.execute(
                '''UPDATE accounts SET email=:new_email
                WHERE name=:name AND username=:username
                AND email=:email AND password=:password''',
                {
                    'new_email': change,
                    'name': chosen_account[0],
                    'username': chosen_account[1],
                    'email': chosen_account[2],
                    'password': chosen_account[3],
                })
        elif item == UPDATE_PASSWORD:
            self.cursor.execute(
                '''UPDATE accounts SET password=:new_password
                WHERE name=:name AND username=:username
                AND email=:email AND password=:password''',
                {
                    'new_password': change,
                    'name': chosen_account[0],
                    'username': chosen_account[1],
                    'email': chosen_account[2],
                    'password': chosen_account[3],
                })

        self.connection.commit()
