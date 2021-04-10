from Account import Account
from pathlib import Path
from enum import Enum
import sqlite3


class Update(Enum):
    NAME = 1
    USERNAME = 2
    EMAIL = 3
    PASSWORD = 4


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

    def add_account(self, account: Account):
        self.cursor.execute(
            '''INSERT INTO accounts(name, username, email, password)
            VALUES (:name, :username, :email, :password)''',
            {
                'name': account.name,
                'username': account.username,
                'email': account.email,
                'password': account.password
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

        if item == Update.NAME:
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
        elif item == Update.USERNAME:
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
        elif item == Update.EMAIL:
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
        elif item == Update.PASSWORD:
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

    def close(self):
        self.cursor.close()
        self.connection.close()
