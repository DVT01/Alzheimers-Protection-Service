from pyAesCrypt import decryptFile, encryptFile
from getpass import getpass
from pathlib import Path
from os import system
import subprocess
import pyperclip
import logging
import hashlib
import sqlite3
import atexit
import main
import sys
import re

actions = {
    'add': 'add_account()',
    'remove': 'delete_account()',
    'edit': 'update_account()',
    'see': 'look_in_accounts()',
    'file': 'file_enc_and_dec()',
    'see all': 'see_all()'
}

logfile = Path('logs.log')
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s:%(message)s')


def outer_record(original_function):
    def inner_record(*args, **kwargs):
        logging.info(f'{original_function.__name__} ran with: {args}, {kwargs} arguments, from {__file__}.')
        return original_function(*args, **kwargs)
    return inner_record


@outer_record
def on_startup(user='Guest', user_password=None):

    global cursor, connection, logged_user, db_table_name, logged_user_password

    logged_user = user
    logged_user_password = user_password
    db_table_name = f'{logged_user}_accounts'
    database = Path('testing.db')

    if user == 'Guest':
        database = ':memory:'

    connection = sqlite3.connect(database)
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS accounts(domain TEXT, username TEXT, email TEXT, password TEXT, user TEXT)')
    main_menu()


@outer_record
def valid_email(email):
    valid_email_regex = re.compile(r'''
    [a-zA-Z0-9._%+-]+      # username
    @                      # @ symbol
    [a-zA-Z0-9.-]+         # domain name
    (\.[a-zA-Z]{2,4})      # dot-something
    ''', re.VERBOSE)
    if valid_email_regex.search(email) is None:
        return False
    return True


@outer_record
def add_account():

    subprocess.call('cls', shell=True)
    print('Account Domain')
    account_name = input()

    print(f'\nUsername of {account_name} account.')
    account_username = input()

    while True:
        print(f'Email of {account_name} account.')
        account_email = input()

        if account_email == str():
            account_email = 'No Email'
            break
        elif not valid_email(account_email):
            subprocess.call('cls', shell=True)
            print(f'{account_email} is not a valid email!')

            print('Do you want to leave it as None?')
            answer = input()

            if answer.lower() in ('no', 'n'):
                continue
            else:
                account_email = 'No Email'
                break
        else:
            break

    while True:
        print(f'\nThe password of {account_name} account.')
        account_password0 = getpass('As you type the password, it will not be seen:')
        account_password1 = getpass('\nPlease re-type password:')

        if account_password0 != account_password1:
            subprocess.call('cls', shell=True)
            print('The passwords do not match!\nPlease re-type them again.')
            continue

        if account_password0 == str():
            account_password0 = 'No Password'
            break

    cursor.execute('INSERT INTO accounts(domain, username, email, password, user) VALUES (:domain, :username, :email, :password, :user)', {
        'domain': account_name,
        'username': account_username,
        'email': account_email,
        'password': account_password0,
        'user': logged_user
    })
    connection.commit()


@outer_record
def update_account():

    subprocess.call('cls', shell=True)
    print(f"What is the account domain of the account you want to update")
    searched_account = input()

    subprocess.call('cls', shell=True)
    cursor.execute('SELECT * FROM accounts WHERE domain=:account_domain AND user=:user', {
        'account_domain': searched_account,
        'user': logged_user
    })
    connection.commit()
    accounts = cursor.fetchall()

    subprocess.call('cls', shell=True)
    if len(accounts) == 1:
        account_password = len(accounts[0][3]) * '*' if accounts[0][3] != 'No Password' else 'No Password'

        print(f'''
Your account domain is: {accounts[0][0]}
Your account username is: {accounts[0][1]}
Your account email email is: {accounts[0][2]}
Your account password password is: {account_password}
''')

        print('What item do you want to change?')
        selected_item = input()

        chosen_account = accounts.pop(0)
    elif len(accounts) > 1:
        while True:
            for account in enumerate(accounts):
                account_password = len(account[1][3]) * '*' if account[1][3] != 'No Password' else 'No Password'

                print(f'''\t\t\t\taccount[0]
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}''')

                if not account[0] == (len(accounts) - 1):
                    continue
                break

            print('Which account do you want to update?')
            selected_account = input()

            if selected_account.isdigit():
                selection = int(selected_account)

            if not isinstance(selection, int) or not 0 <= selection <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print('Invalid Input!\n')
                print('Choose one account by inputting the number above the desired account!')
                system('pause >nul 2>&1')
                subprocess.call('cls', shell=True)
                continue
            elif 0 <= selection <= (len(accounts) - 1):
                for account in enumerate(accounts):
                    if account[0] == selection:
                        chosen_account = account[1]
                        break
            break

        subprocess.call('cls', shell=True)
        print(f'''
Your account domain is: {chosen_account[0]}
Your account username is: {chosen_account[1]}
Your account email email is: {chosen_account[2]}
Your account password password is: {'*'*len(chosen_account[3])}
''')

        print('What item do you want to change?')
        selected_item = input()
    else:
        subprocess.call('cls', shell=True)
        print(f'''
There is no account domain called {searched_account}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry (Give another domain)
-Main (Go to the main menu)
''')
        answer = input()

        if answer.lower() in ('retry', 'r'):
            update_account()
        else:
            main_menu()

    if selected_item.lower() == 'domain':
        subprocess.call('cls', shell=True)
        print("\nWhat do you want to change the account domain to?")
        selected_change = input()
        cursor.execute("UPDATE accounts SET domain=:account_domain_new WHERE domain=:account_domain_previous AND username=:username AND email=:email AND password=:password AND user=:user", {
            'account_domain_new': selected_change,
            'account_domain_previous': chosen_account[0],
            'username': chosen_account[1],
            'email': chosen_account[2],
            'password': chosen_account[3],
            'user': logged_user
        })
        connection.commit()
    elif selected_item.lower() == 'username':
        subprocess.call('cls', shell=True)
        print('\nWhat do you want to change your username to?')
        selected_change = input()
        cursor.execute('UPDATE accounts SET username=:username_new WHERE domain=:account_domain AND username=:username_previous AND email=:email AND password=:password AND user=:username_previous', {
            'username_new': selected_change,
            'account_domain': chosen_account[0],
            'username_previous': chosen_account[1],
            'email': chosen_account[2],
            'password': chosen_account[3],
            'user': logged_user
        })
        connection.commit()
    elif selected_item.lower() == 'email':
        while True:
            subprocess.call('cls', shell=True)
            print('''
What do you want to change your account email to?
(Type none if no email)''')
            selected_change = input()

            if selected_change.lower() == 'none':
                selected_change = 'No Email'
                break
            elif not valid_email(selected_change):
                subprocess.call('cls', shell=True)
                print(f'{selected_change} is not a valid email!')
                system('pause >nul 2>&1')

                subprocess.call('cls', shell=True)
                print('Do you want to leave it as None?')
                answer = input()

                if answer.lower() in ('no', 'n'):
                    continue
                else:
                    selected_change = 'No Email'
                    subprocess.call('cls', shell=True)
                    break
            else:
                break

        cursor.execute('UPDATE accounts SET email=:email_new WHERE domain=:account_domain AND username=:username AND email=:email_previous AND password=:password AND user=:user', {
            'email_new': selected_change,
            'account_domain': chosen_account[0],
            'username': chosen_account[1],
            'email_previous': chosen_account[2],
            'password': chosen_account[3],
            'user': logged_user
        })
        connection.commit()
    elif selected_item.lower() == 'password':
        while True:
            subprocess.call('cls', shell=True)
            print('''
What do you want to change your account password to?
The password will not be seen as you type
(type none if no password)''')
            password_try0 = getpass('')
            password_try1 = getpass('Re-enter password:')

            if password_try0 != password_try1:

                subprocess.call('cls', shell=True)
                print('The passwords are not the same!\nTry again.')
                system('pause >nul 2>&1')
                continue
            break

        if password_try0 == str():
            password_try0 = 'No Password'

        cursor.execute('UPDATE accounts SET password=:password_new WHERE domain=:account_domain AND username=:username AND email=:email AND password=:password_previous AND user=:user', {
            'password_new': password_try0,
            'account_domain': chosen_account[0],
            'username': chosen_account[1],
            'email': chosen_account[2],
            'password_previous': chosen_account[3],
            'user': logged_user
        })
        connection.commit()

        main_menu()


@outer_record
def delete_account():

    subprocess.call('cls', shell=True)
    print(f'What is the account domain you want to delete?')
    searched_account = input()

    cursor.execute("SELECT * FROM accounts WHERE domain=:account_domain AND user=:user", {
        'account_domain': searched_account,
        'user': logged_user
    })
    connection.commit()
    accounts = cursor.fetchall()

    if len(accounts) == 0:
        subprocess.call('cls', shell=True)
        print(f'''
There is no account domain called {searched_account}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry(Give another domain)
-Main(Go to the MainMenu)
''')
        selection = input()
        if selection.lower() in ('retry', 'r'):
            delete_account()
        else:
            main_menu()

    elif len(accounts) > 1:
        subprocess.call('cls', shell=True)
        while True:
            for account in enumerate(accounts):
                account_password = len(account[1][3]) * '*' if account[1][3] != 'No Password' else 'No Password'

                print(f'''
                {account[0]}
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}''')

                if account[0] != (len(accounts) - 1):
                    continue
                break

            print(f'Which account do you want to delete?')
            selection = input()

            if selection.isdigit():
                selection = int(selection)

            if not isinstance(selection, int) or not 0 <= selection <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print('Invalid Input!\n')
                print('Choose one account by inputing the number above the desired account(in red)')
                system('pause >nul 2>&1')
                subprocess.call('cls', shell=True)
                continue
            elif 0 <= selection <= (len(accounts) - 1):
                for account in enumerate(accounts):
                    if account[0] == selection:
                        choosen_account = account[1]
                        break

            cursor.execute('DELETE FROM accounts WHERE domain=:account_domain AND username=:username AND email=:email AND password=:password AND user=:user', {
                'account_domain': choosen_account[0],
                'username': choosen_account[1],
                'email': choosen_account[2],
                'password': choosen_account[3],
                'user': logged_user
            })
            connection.commit()

            main_menu()

    elif len(accounts) == 1:
        cursor.execute('DELETE FROM accounts WHERE domain=:account_domain AND user=:user', {
            'account_domain': searched_account,
            'user': logged_user
        })
        connection.commit()


@outer_record
def look_in_accounts():

    subprocess.call('cls', shell=True)
    print('What is the Account Domain you are looking for?')
    account_domain = input()

    cursor.execute('SELECT * FROM accounts WHERE domain=:account_domain AND user=:user', {
        'account_domain': account_domain,
        'user': logged_user
    })
    connection.commit()
    accounts = cursor.fetchall()

    subprocess.call('cls', shell=True)
    if len(accounts) > 1:
        while True:
            for account in enumerate(accounts):
                account_password = len(account[1][3]) * '*' if account[1][3] != 'No Password' else 'No Password'

                print(f'''
                {account[0]}
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}''')

                if not account[0] == (len(accounts) - 1):
                    continue
                break

            print('Which account do you want to see the password of?')
            account_selected = input()

            if account_selected.isdigit():
                account_selected = int(account_selected)

            if not isinstance(account_selected, int) or not 0 <= account_selected <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print('Invalid Input!\n')
                print('Choose one account by inputing the number above the desired account.')
                system('pause >nul 2>&1')
                subprocess.call('cls', shell=True)
                continue
            elif 0 <= account_selected <= (len(accounts) - 1):
                for account in enumerate(accounts):
                    if account[0] == account_selected:
                        choosen_account = account[1]
                        break
            break

        if choosen_account[3] == 'No Password':
            subprocess.call('cls', shell=True)
            print(f'The {choosen_account[0]} account doesn\'t have a password!')
            system('pause >nul 2>&1')
            main_menu()

        subprocess.call('cls', shell=True)
        print('Do you want me to copy your account password to your clipboard?')
        password_selection = input()

        if password_selection.lower() in ('no', 'n'):
            subprocess.call('cls', shell=True)
            print(f'Your account password is: {choosen_account[3]}')
            system('pause >nul 2>&1')

        else:
            subprocess.call('cls', shell=True)
            pyperclip.copy(choosen_account[3])
            print('Your account password has been copied to your clipboard')
            system('pause >nul 2>&1')

    elif len(accounts) == 1:
        account_password = len(accounts[0][3]) * '*' if accounts[0][3] != 'No Password' else 'No Password'

        subprocess.call('cls', shell=True)
        print(f'''
Your account domain is: {accounts[0][0]}
Your username is: {accounts[0][1]}
Your account email is: {accounts[0][2]}
Your account password is: {account_password}''')
        system('pause >nul 2>&1')

        if account_password == 'No Password':
            main_menu()

        subprocess.call('cls', shell=True)
        print('Do you want me to copy your account password to your clipboard?')
        copy_selection = input()

        if copy_selection.lower() in ('no', 'n'):
            subprocess.call('cls', shell=True)
            print(f'Your account password is: {accounts[0][3]}')
            system('pause >nul 2>&1')

        subprocess.call('cls', shell=True)
        pyperclip.copy(accounts[0][3])
        print('Your account password has been copied to your clipboard')
        system('pause >nul 2>&1')

    else:
        subprocess.call('cls', shell=True)
        print(f'''
There is no account domain called {account_domain}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry(Give another domain)
-Main(Go to the MainMenu)
''')
        selection = input()
        if selection.lower() in ('retry', 'r'):
            look_in_accounts()
        else:
            main_menu()


@outer_record
def file_enc_and_dec():

    buffer_size = 64

    subprocess.call('cls', shell=True)
    print('Do you want to encrypt or decrypt a file?')
    selection = input()

    if selection.lower() in ('encrypt', 'enc'):

        while True:
            subprocess.call('cls', shell=True)
            print('Full directory to file')
            path_to_file = Path(input().replace('\\', '/'))

            file_ = path_to_file.name

            if not path_to_file.exists():

                subprocess.call('cls', shell=True)
                print('Invalid Directory!!')
                print(f'Choose a valid directory, the directory {path_to_file}, doesn\'t exist!')
                system('pause >nul 2>&1')
                continue

            while True:
                print('\nDirectory of where the file will end')
                end_directory = Path(input().replace('\\', '/'))

                if not end_directory.exists():

                    subprocess.call('cls', shell=True)
                    print('Invalid Directory!!')
                    print(f'Choose a valid directory, the directory {end_directory}, doesn\'t exist!')
                    system('pause >nul 2>&1')
                    subprocess.call('cls', shell=True)
                    continue

                if end_directory.endswith('/'):
                    end_directory = end_directory + file_ + '.aes'
                    break
                else:
                    end_directory = end_directory + '/' + file_ + '.aes'
                    break

            while True:
                subprocess.call('cls', shell=True)
                print('Password of the encryption')
                password = input()

                break

            encryptFile(path_to_file, end_directory, password, buffer_size)

            break

    elif selection.lower() in ('decrypt', 'dec'):

        while True:
            subprocess.call('cls', shell=True)
            print('Full directory to file')
            path_to_file = Path(input().replace('\\', '/'))

            file_ = path_to_file.name

            if not path_to_file.exists():

                subprocess.call('cls', shell=True)
                print('Invalid Directory!!')
                print(f'Choose a valid directory, the directory {path_to_file}, doesn\'t exist!')
                system('pause >nul 2>&1')
                continue

            while True:
                print('\nDirectory of where the file will end')
                end_directory = Path(input().replace('\\', '/'))

                if not end_directory.exists():
                    subprocess.call('cls', shell=True)
                    print('Invalid Directory!!')
                    print(f'Choose a valid directory, the directory {end_directory}, doesn\'t exist!')
                    system('pause >nul 2>&1')
                    subprocess.call('cls', shell=True)
                    continue

                if end_directory.endswith('/'):
                    end_directory = end_directory + file_
                    end_directory = end_directory.replace('.aes', '')
                    break
                else:
                    end_directory = end_directory + '/' + file_
                    end_directory = end_directory.replace('.aes', '')
                    break

            while True:
                subprocess.call('cls', shell=True)
                print('Password of the encryption')
                password = input()

                try:
                    decryptFile(path_to_file, end_directory, password, buffer_size)
                    break
                except ValueError:
                    subprocess.call('cls', shell=True)
                    print('The Password is wrong!')
                    system('pause >nul 2>&1')
                    continue
            break
    else:

        subprocess.call('cls', shell=True)
        print('Invalid Answer!!')
        print("Valid answers are: 'encrypt' or 'enc', and/or 'decrypt' or 'dec'")
        system('pause >nul 2>&1')

        file_enc_and_dec()


@outer_record
def see_all():
    tries = 1
    while True:
        if logged_user_password is None:
            break
        subprocess.call('cls', shell=True)
        print(f'''Please type the password for the {logged_user} RSIH APS account.\t\t\t\t\t\t\t\t\t\t\t\t Try {tries} of 2
(As you type the password won't be visible)''')
        password = hashlib.sha512(getpass('').encode('UTF-8')).hexdigest()

        if password != logged_user_password:
            if tries == 2:
                sys.exit()
            subprocess.call('cls', shell=True)
            print('''Incorrect Password!
Please try again.''')
            system('pause >nul 2>&1')
            tries += 1
            continue
        break

    cursor.execute('SELECT * FROM accounts WHERE user=:user', {
        'user': logged_user
    })
    connection.commit()
    accounts = cursor.fetchall()

    if accounts == list():
        subprocess.call('cls', shell=True)
        print('There are no accounts saved yet!')
        system('pause >nul 2>&1')
        main_menu()

    subprocess.call('cls', shell=True)
    for account in accounts:
        account_password = len(account[3]) * '*' if account[3] != 'No Password' else 'No Password'
        print(f'''
This account domain is: {account[0]}
This account username is: {account[1]}
This account email is: {account[2]}
This account password is: {account_password}
''')
    system('pause >nul 2>&1')
    main_menu()


@atexit.register
@outer_record
def on_exit():
    try:
        cursor.close()
        connection.close()
    except NameError as error:
        print('Run the main.py file instead of this please!')
        system('pause >nul 2>&1')


@outer_record
def main_menu():
    while True:

        subprocess.call('cls', shell=True)
        print(f'\tMain Menu\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tLogged in as {logged_user}.')
        print('''What do you want to do?
-Add (Add an account)
-Remove (Delete an account)
-Edit (Modify an account)
-See (See an accounts details)
-File (Encrypt or Decrypt files)
-Delete User (Deletes a user)
-Exit
''')
        action = input()

        if action == '':
            continue
        elif action.lower() == 'delete user' and logged_user != 'Guest':
            main.remove(logged_user, logged_user_password)
        elif action.lower() in actions:
            eval(actions[action.lower()])
        elif action.lower() == 'exit':
            sys.exit()
        else:
            subprocess.call('cls', shell=True)
            print('Invalid Input!\n')
            print(f"Valid inputs are: add, remove, edit, see, file and exit")
            system('pause >nul 2>&1')
            continue


if __name__ == '__main__':
    sys.exit()
