from pyAesCrypt import decryptFile, encryptFile
from main.Database import Database
from getpass import getpass
from pathlib import Path
from os import system
import subprocess
import pyperclip
import hashlib
import atexit
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


def add_account():

    subprocess.call('cls', shell=True)
    print('Account Name')
    name = input()

    print(f'\nUsername of {name} account.')
    username = input()

    email = str()
    while not valid_email(email):
        print(f'Email of {name} account.')
        email = input()

    password = getpass('As you type the password, it will not be seen:')

    db.add_account(name, username, email, password)


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


def see_all():
    accounts = db.fetchall()

    if accounts == list():
        subprocess.call('cls', shell=True)
        print('There are no accounts saved yet!')
        system('pause >nul 2>&1')

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


@atexit.register
def on_exit():
    db.close()


if __name__ == '__main__':

    db = Database()

    while True:
        subprocess.call('cls', shell=True)
        print('\tMain Menu')
        print('What do you want to do?')
        print('-Add (Add an account)')
        print('-Remove (Delete an account)')
        print('-Edit (Modify an account)')
        print('-See (See an accounts details)')
        print('-File (Encrypt or Decrypt files)')
        print('-Delete User (Deletes a user)')
        print('-Exit')
        action = input()

        if action == '':
            continue
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
