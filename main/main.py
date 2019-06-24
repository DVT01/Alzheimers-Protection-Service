from getpass import getpass
import subprocess
import hashlib
import functionalities
import sys
import csv
import os


def create_account(first_account=False):
    while True:
        subprocess.call('cls', shell=True)
        print('Create an account.')

        username = input('Username: ')
        password0 = getpass('(The password will not be seen as you type) Password: ')
        password1 = getpass('(The password will not be seen as you type) Re-Type Password: ')

        if password0 != password1:
            subprocess.call('cls', shell=True)
            print('Passwords don\'t match, try again!')
            os.system('pause >nul 2>&1')
            continue
        password = hashlib.sha512(password0.encode('UTF-8')).hexdigest()
        break

    with open('users.csv', 'r') as read_file, open('users.csv', 'a') as write_file:
        csv_reader = list(csv.reader(read_file))
        fieldnames = ['username', 'password']
        csv_writer = csv.DictWriter(write_file, fieldnames=fieldnames, delimiter='|')

        if csv_reader == list():
            csv_writer.writeheader()

        csv_writer.writerow({
            'username': username,
            'password': password
        })

    if first_account:
        functionalities.logging.info(f'''
=================================================
Running on_startup, from {__file__}, with {username}''')
        functionalities.on_startup(user=username, user_password=password0)
    else:
        functionalities.logging.info(f'Running on_startup, from {__file__}, with {username}')
        functionalities.on_startup(user=username, user_password=password0)


def account_found(username, password):
    while True:
        subprocess.call('cls', shell=True)
        print(f'''Account Found
What is the password of the {username} account.
(As you type the password won't be visible)''')
        account_password = hashlib.sha512(getpass('').encode('UTF-8')).hexdigest()

        if account_password == password:
            subprocess.call('cls', shell=True)
            print('Succesful Log In!')
            os.system('pause >nul 2>&1')
            functionalities.logging.info(f'''
=================================================
Running on_startup, from {__file__}, with {username}''')
            functionalities.on_startup(user=username, user_password=account_password)
        else:
            subprocess.call('cls', shell=True)
            print('''Incorrect Password!
            Try Again.''')
            os.system('pause >nul 2>&1')
            continue


def remove(user, user_password):
    subprocess.call('cls', shell=True)
    print(f'Are you sure you want to remove the {user} user?')
    answer = input()

    if answer in ('n', 'no'):
        functionalities.MainMenu()

    while True:
        subprocess.call('cls', shell=True)
        print(f"What's the password of the {user} user?")
        account_password = hashlib.sha512(getpass('').encode('UTF-8')).hexdigest()

        if account_password != user_password:
            subprocess.call('cls', shell=True)
            print('Wrong Password!\nPlease Try Again')
            os.system('pause >nul 2>&1')
            continue
        break

    with open('users.csv', 'r') as file1, open('users.csv', 'w') as file2:
        fieldnames = ['username', 'password']
        writer = csv.DictWriter(file2, fieldnames=fieldnames, delimiter='|')
        accounts = [row for row in csv.DictReader(file1, delimiter='|') if row['username'] != user]
        writer.writeheader()
        for account in accounts:
            writer.writerow({
                'username': account['username'],
                'password': account['password']
            })
    sys.exit()


if __name__ == '__main__':
    os.system('title DVT\'s Account Saver')

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    if not os.path.exists('users.csv'):
        os.system('fsutil file createnew users.csv 0 >nul 2>&1')

    with open('users.csv', 'r') as file:
        csv_reader = list(csv.DictReader(file, delimiter='|'))

    if csv_reader != list():
        subprocess.call('cls', shell=True)
        print('Do you have an account?')
        has_account = input()
        if has_account.lower() in ('no', 'n'):
            create_account()
        else:
            while True:
                subprocess.call('cls', shell=True)
                print('What is the username of the account?')
                account_username = input()
                with open('users.csv', 'r') as file:
                    csv_reader = csv.DictReader(file, delimiter='|')
                    for account in csv_reader:
                        if account['username'] == account_username:
                            account_found(account['username'], account['password'])
                    else:
                        subprocess.call('cls', shell=True)
                        print('''Account not found!
-- Capitalization matters --
Try Again.''')
                        os.system('pause >nul 2>&1')
                        continue
    else:
        create_account(first_account=True)
