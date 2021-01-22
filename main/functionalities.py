from pyAesCrypt import decryptFile, encryptFile
from termcolor import colored
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
    MainMenu()


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
    print(colored('Account Domain', 'blue', attrs=['bold']))
    account_name = input()

    print(colored(f'\nUsername of the {account_name} account.', 'yellow', attrs=['bold']))
    account_username = input()

    while True:
        print(colored(f'''
Email of the {account_username} account.
If you don't have an email then type none''', 'red', attrs=['bold']))
        account_email = input()

        if account_email.lower() == 'none':
            account_email = 'No Email'
            break
        elif not valid_email(account_email):
            subprocess.call('cls', shell=True)
            print(colored(f'{account_email} is not a valid email!', 'white', 'on_red', attrs=['bold']))
            system('pause >nul 2>&1')

            subprocess.call('cls', shell=True)
            print(colored('Do you want to leave it as None?', 'blue', attrs=['bold']))
            answer = input()

            if answer.lower() in ('no', 'n'):
                continue
            else:
                account_email = 'No Email'
                break
        else:
            break

    while True:
        print(colored(f'\nThe password of the {account_username} account.', 'magenta', attrs=['bold']))
        account_password0 = getpass(colored('As you type the password, it will not be seen:', 'cyan', attrs=['bold']))
        account_password1 = getpass(colored('\nPlease re-type password:', 'red', attrs=['bold']))

        if account_password0 != account_password1:
            subprocess.call('cls', shell=True)
            print(colored('The passwords do not match!\nPlease re-type them again.', 'red', 'on_white', attrs=['bold']))
            system('pause >nul 2>&1')
            subprocess.call('cls', shell=True)
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
    print(f"What is the account domain of the account you want to {colored('update', 'red', attrs=['bold'])}?")
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
Your account {colored('domain', 'red', attrs=['bold'])} is: {accounts[0][0]}
Your account {colored('username', 'red', attrs=['bold'])} is: {accounts[0][1]}
Your account {colored('email', 'red', attrs=['bold'])} email is: {accounts[0][2]}
Your account {colored('password', 'red', attrs=['bold'])} password is: {account_password}
''')

        print(colored('What item (in red) do you want to change?', 'yellow', attrs=['bold']))
        selected_item = input()

        choosen_account = accounts.pop(0)

    elif len(accounts) > 1:
        while True:
            for account in enumerate(accounts):
                account_password = len(account[1][3]) * '*' if account[1][3] != 'No Password' else 'No Password'

                print(f'''              {colored(account[0], 'red', attrs=['bold'])}
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}
''')

                if not account[0] == (len(accounts) - 1):
                    continue
                break

            print(colored('Which account do you want to update?', 'blue', attrs=['bold']))
            selected_account = input()

            if selected_account.isdigit():
                selection = int(selected_account)

            if not isinstance(selection, int) or not 0 <= selection <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print(colored('Invalid Input!\n', 'red', attrs=['bold']))
                print(colored('Choose one account by inputing the number above the desired account(in red)!', 'green', attrs=['bold']))
                system('pause >nul 2>&1')
                subprocess.call('cls', shell=True)
                continue
            elif 0 <= selection <= (len(accounts) - 1):
                for account in enumerate(accounts):
                    if account[0] == selection:
                        choosen_account = account[1]
                        break
            break

        subprocess.call('cls', shell=True)
        print(f'''
Your account {colored('domain', 'red', attrs=['bold'])} is: {choosen_account[0]}
Your account {colored('username', 'red', attrs=['bold'])} is: {choosen_account[1]}
Your account {colored('email', 'red', attrs=['bold'])} email is: {choosen_account[2]}
Your account {colored('password', 'red', attrs=['bold'])} password is: {'*'*len(choosen_account[3])}
''')

        print(colored('What item do you want to change?', 'yellow', attrs=['bold']))
        selected_item = input()
    else:
        subprocess.call('cls', shell=True)
        print(colored(f'''
There is no account domain called {searched_account}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry(Give another domain)
-Main(Go to the MainMenu)
''', 'yellow', attrs=['bold']))
        answer = input()

        if answer.lower() in ('retry', 'r'):
            update_account()
        else:
            MainMenu()

    if selected_item.lower() == 'domain':
        subprocess.call('cls', shell=True)
        print(colored("\nWhat do you want to change the account domain to?", "yellow", attrs=["bold"]))
        selected_change = input()
        cursor.execute("UPDATE accounts SET domain=:account_domain_new WHERE domain=:account_domain_previous AND username=:username AND email=:email AND password=:password AND user=:user", {
            'account_domain_new': selected_change,
            'account_domain_previous': choosen_account[0],
            'username': choosen_account[1],
            'email': choosen_account[2],
            'password': choosen_account[3],
            'user': logged_user
        })
        connection.commit()
    elif selected_item.lower() == 'username':
        subprocess.call('cls', shell=True)
        print(colored('\nWhat do you want to change your username to?', 'blue', attrs=['bold']))
        selected_change = input()
        cursor.execute('UPDATE accounts SET username=:username_new WHERE domain=:account_domain AND username=:username_previous AND email=:email AND password=:password AND user=:username_previous', {
            'username_new': selected_change,
            'account_domain': choosen_account[0],
            'username_previous': choosen_account[1],
            'email': choosen_account[2],
            'password': choosen_account[3],
            'user': logged_user
        })
        connection.commit()
    elif selected_item.lower() == 'email':
        while True:
            subprocess.call('cls', shell=True)
            print(colored('''
What do you want to change your account email to?
(Type none if no email)''', 'red', attrs=['bold']))
            selected_change = input()

            if selected_change.lower() == 'none':
                selected_change = 'No Email'
                break
            elif not valid_email(selected_change):
                subprocess.call('cls', shell=True)
                print(colored(f'{selected_change} is not a valid email!', 'white', 'on_red', attrs=['bold']))
                system('pause >nul 2>&1')

                subprocess.call('cls', shell=True)
                print(colored('Do you want to leave it as None?', 'blue', attrs=['bold']))
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
            'account_domain': choosen_account[0],
            'username': choosen_account[1],
            'email_previous': choosen_account[2],
            'password': choosen_account[3],
            'user': logged_user
        })
        connection.commit()

    elif selected_item.lower() == 'password':
        while True:
            subprocess.call('cls', shell=True)
            print(colored('''
What do you want to change your account password to?
The password will not be seen as you type
(type none if no password)''', 'magenta', attrs=['bold']))
            password_try0 = getpass('')
            password_try1 = getpass(colored('Re-enter password:', 'magenta', attrs=['bold']))

            if password_try0 != password_try1:

                subprocess.call('cls', shell=True)
                print(colored('The passwords are not the same!\nTry again.', 'red', attrs=['bold']))
                system('pause >nul 2>&1')
                continue
            break

        if password_try0 == str():
            password_try0 = 'No Password'

        cursor.execute('UPDATE accounts SET password=:password_new WHERE domain=:account_domain AND username=:username AND email=:email AND password=:password_previous AND user=:user', {
            'password_new': password_try0,
            'account_domain': choosen_account[0],
            'username': choosen_account[1],
            'email': choosen_account[2],
            'password_previous': choosen_account[3],
            'user': logged_user
        })
        connection.commit()

        MainMenu()


@outer_record
def delete_account():

    subprocess.call('cls', shell=True)
    print(f'What is the account domain you want to {colored("delete", "red", attrs=["bold"])}?')
    searched_account = input()

    cursor.execute("SELECT * FROM accounts WHERE domain=:account_domain AND user=:user", {
        'account_domain': searched_account,
        'user': logged_user
    })
    connection.commit()
    accounts = cursor.fetchall()

    if len(accounts) == 0:
        subprocess.call('cls', shell=True)
        print(colored(f'''
There is no account domain called {searched_account}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry(Give another domain)
-Main(Go to the MainMenu)
''', "yellow", attrs=["bold"]))
        selection = input()
        if selection.lower() in ('retry', 'r'):
            delete_account()
        else:
            MainMenu()

    elif len(accounts) > 1:
        subprocess.call('cls', shell=True)
        while True:
            for account in enumerate(accounts):
                account_password = len(account[1][3]) * '*' if account[1][3] != 'No Password' else 'No Password'

                print(colored(f'''
                {colored(account[0], 'red', attrs=['bold'])}
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}
                ''', 'green', attrs=['bold']))

                if account[0] != (len(accounts) - 1):
                    continue
                break

            print(f'Which account do you want to {colored("delete", "red", attrs=["bold"])}?')
            selection = input()

            if selection.isdigit():
                selection = int(selection)

            if not isinstance(selection, int) or not 0 <= selection <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print(colored('Invalid Input!\n', 'red', attrs=['bold']))
                print(colored('Choose one account by inputing the number above the desired account(in red)', 'green', attrs=['bold']))
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

            MainMenu()

    elif len(accounts) == 1:
        cursor.execute('DELETE FROM accounts WHERE domain=:account_domain AND user=:user', {
            'account_domain': searched_account,
            'user': logged_user
        })
        connection.commit()


@outer_record
def look_in_accounts():

    subprocess.call('cls', shell=True)
    print(colored('What is the Account Domain you are looking for?', 'yellow', attrs=['bold']))
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

                print(colored(f'''
                {colored(account[0], 'red', attrs=['bold'])}
Your account domain is: {account[1][0]}
Your username is: {account[1][1]}
Your account email is: {account[1][2]}
Your account password is: {account_password}
                ''', 'green', attrs=['bold']))

                if not account[0] == (len(accounts) - 1):
                    continue
                break

            print(colored('Which account do you want to see the password of?', 'blue', attrs=['bold']))
            account_selected = input()

            if account_selected.isdigit():
                account_selected = int(account_selected)

            if not isinstance(account_selected, int) or not 0 <= account_selected <= (len(accounts) - 1):
                subprocess.call('cls', shell=True)
                print(colored('Invalid Input!\n', 'red', attrs=['bold']))
                print(colored('Choose one account by inputing the number above the desired account(in red).', 'green', attrs=['bold']))
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
            MainMenu()

        subprocess.call('cls', shell=True)
        print(colored('Do you want me to copy your account password to your clipboard?', 'red', attrs=['bold']))
        password_selection = input()

        if password_selection.lower() in ('no', 'n'):
            subprocess.call('cls', shell=True)
            print(colored(f'Your account password is: {choosen_account[3]}', 'white', attrs=['bold']))
            system('pause >nul 2>&1')

        else:
            subprocess.call('cls', shell=True)
            pyperclip.copy(choosen_account[3])
            print(colored('Your account password has been copied to your clipboard', 'blue', attrs=['bold']))
            system('pause >nul 2>&1')

    elif len(accounts) == 1:
        account_password = len(accounts[0][3]) * '*' if accounts[0][3] != 'No Password' else 'No Password'

        subprocess.call('cls', shell=True)
        print(colored(f'''
Your account domain is: {accounts[0][0]}
Your username is: {accounts[0][1]}
Your account email is: {accounts[0][2]}
Your account password is: {account_password}
        ''', 'green', attrs=['bold']))
        system('pause >nul 2>&1')

        if account_password == 'No Password':
            MainMenu()

        subprocess.call('cls', shell=True)
        print(colored('Do you want me to copy your account password to your clipboard?', 'red', attrs=['bold']))
        copy_selection = input()

        if copy_selection.lower() in ('no', 'n'):
            subprocess.call('cls', shell=True)
            print(colored(f'Your account password is: {accounts[0][3]}', 'white', attrs=['bold']))
            system('pause >nul 2>&1')

        subprocess.call('cls', shell=True)
        pyperclip.copy(accounts[0][3])
        print(colored('Your account password has been copied to your clipboard', 'blue', attrs=['bold']))
        system('pause >nul 2>&1')

    else:
        subprocess.call('cls', shell=True)
        print(colored(f'''
There is no account domain called {account_domain}.
--Remember, account domains are CASE-SENSITIVE--

What do you want to do?
-Retry(Give another domain)
-Main(Go to the MainMenu)
''', "yellow", attrs=["bold"]))
        selection = input()
        if selection.lower() in ('retry', 'r'):
            look_in_accounts()
        else:
            MainMenu()


@outer_record
def file_enc_and_dec():

    buffer_size = 64

    subprocess.call('cls', shell=True)
    print(colored('Do you want to encrypt or decrypt a file?'))
    selection = input()

    if selection.lower() in ('encrypt', 'enc'):

        while True:
            subprocess.call('cls', shell=True)
            print(colored('Full directory to file', 'yellow', attrs=['bold']))
            path_to_file = Path(input().replace('\\', '/'))

            file_ = path_to_file.name

            if not path_to_file.exists():

                subprocess.call('cls', shell=True)
                print(colored('Invalid Directory!!', 'white', 'on_red', attrs=['bold']))
                print(colored(f'Choose a valid directory, the directory {path_to_file}, doesn\'t exist!', 'white', 'on_red', attrs=['bold']))
                system('pause >nul 2>&1')
                continue

            while True:
                print(colored('\nDirectory of where the file will end', 'blue', attrs=['bold']))
                end_directory = Path(input().replace('\\', '/'))

                if not end_directory.exists():

                    subprocess.call('cls', shell=True)
                    print(colored('Invalid Directory!!', 'white', 'on_red', attrs=['bold']))
                    print(colored(f'Choose a valid directory, the directory {end_directory}, doesn\'t exist!', 'white', 'on_red', attrs=['bold']))
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
                print(colored('Password of the encryption', 'magenta', attrs=['bold']))
                password = input()

                break

            encryptFile(path_to_file, end_directory, password, buffer_size)

            break

    elif selection.lower() in ('decrypt', 'dec'):

        while True:
            subprocess.call('cls', shell=True)
            print(colored('Full directory to file', 'yellow', attrs=['bold']))
            path_to_file = Path(input().replace('\\', '/'))

            file_ = path_to_file.name

            if not path_to_file.exists():

                subprocess.call('cls', shell=True)
                print(colored('Invalid Directory!!', 'white', 'on_red', attrs=['bold']))
                print(colored(f'Choose a valid directory, the directory {path_to_file}, doesn\'t exist!', 'white', 'on_red', attrs=['bold']))
                system('pause >nul 2>&1')
                continue

            while True:
                print(colored('\nDirectory of where the file will end', 'blue', attrs=['bold']))
                end_directory = Path(input().replace('\\', '/'))

                if not end_directory.exists():
                    subprocess.call('cls', shell=True)
                    print(colored('Invalid Directory!!', 'white', 'on_red', attrs=['bold']))
                    print(colored(f'Choose a valid directory, the directory {end_directory}, doesn\'t exist!', 'white', 'on_red', attrs=['bold']))
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
                print(colored('Password of the encryption', 'magenta', attrs=['bold']))
                password = input()

                try:
                    decryptFile(path_to_file, end_directory, password, buffer_size)
                    break
                except ValueError:
                    subprocess.call('cls', shell=True)
                    print(colored('The Password is wrong!', 'red', attrs=['bold']))
                    system('pause >nul 2>&1')
                    continue
            break
    else:

        subprocess.call('cls', shell=True)
        print(colored('Invalid Answer!!', 'white', 'on_red', attrs=['bold']))
        print(colored("Valid answers are: 'encrypt' or 'enc', and/or 'decrypt' or 'dec'", 'red', attrs=['bold']))
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
        MainMenu()

    subprocess.call('cls', shell=True)
    for account in accounts:
        account_password = len(account[3]) * '*' if account[3] != 'No Password' else 'No Password'
        print(f'''
This account {colored('domain', 'red', attrs=['bold'])} is: {account[0]}
This account {colored('username', 'red', attrs=['bold'])} is: {account[1]}
This account {colored('email', 'red', attrs=['bold'])} is: {account[2]}
This account {colored('password', 'red', attrs=['bold'])} is: {account_password}
''')
    system('pause >nul 2>&1')
    MainMenu()


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
def MainMenu():
    while True:

        subprocess.call('cls', shell=True)
        print(colored(f'\tMain Menu\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tLogged in as {logged_user}.', 'red', attrs=['bold']))
        print(colored('''What do you want to do?
-Add(Add an account)
-Remove(Delete an account)
-Edit(Modify an account)
-See(See an accounts details)
-File(Encrypt or Decrypt files)
-Delete User(Deletes a user)
-Exit
''', 'green', attrs=['bold']))
        action = input()

        if action == '':
            continue
        elif action.lower() == 'delete user' and logged_user != 'Guest':
            main.remove(logged_user, logged_user_password)
        elif action.lower() in actions:
            eval(actions[action.lower()])
        elif action.lower() == 'exit':
            sys.exit()
        elif action.lower() not in actions:
            subprocess.call('cls', shell=True)
            print(colored('Invalid Input!\n', 'white', 'on_red', attrs=['underline', 'bold']))
            print(colored(f"Valid inputs are: {colored('add', 'red', attrs=['bold'])}{colored(',', 'green', attrs=['bold'])} \
{colored('remove', 'red', attrs=['bold'])}{colored(',', 'green', attrs=['bold'])} \
{colored('edit', 'red', attrs=['bold'])}{colored(',', 'green', attrs=['bold'])} \
{colored('see', 'red', attrs=['bold'])}{colored(',', 'green', attrs=['bold'])} \
{colored('file', 'red', attrs=['bold'])}{colored(', and', 'green', attrs=['bold'])} \
{colored('exit', 'red', attrs=['bold'])}", 'green', attrs=['bold']))
            system('pause >nul 2>&1')
            continue


if __name__ == '__main__':
    sys.exit()
