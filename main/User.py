import csv


class User:

    def __init__(self, username, password, cursor, connection):
        with open('users.csv', 'r') as file:
            csv_reader = csv.DictReader(file, delimiter='|')
            for account in csv_reader:
                if account['username'] == username and account['password'] == password:
                    self.user = username
                    self.password = password
            else:
                raise KeyError('Account not found')

        self.cursor = cursor
        self.connection = connection

    def add_account(self, name, username, email, password):
        self.cursor.execute(
            'INSERT INTO accounts(domain, username, email, password, user) VALUES (:domain, :username, :email, :password, :user)',
            {
                'domain': name,
                'username': username,
                'email': email,
                'password': password,
                'user': self.user
            })
        self.connection.commit()

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
    Your account password password is: {'*' * len(chosen_account[3])}
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
            cursor.execute(
                "UPDATE accounts SET domain=:account_domain_new WHERE domain=:account_domain_previous AND username=:username AND email=:email AND password=:password AND user=:user",
                {
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
            cursor.execute(
                'UPDATE accounts SET username=:username_new WHERE domain=:account_domain AND username=:username_previous AND email=:email AND password=:password AND user=:username_previous',
                {
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

            cursor.execute(
                'UPDATE accounts SET email=:email_new WHERE domain=:account_domain AND username=:username AND email=:email_previous AND password=:password AND user=:user',
                {
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

            cursor.execute(
                'UPDATE accounts SET password=:password_new WHERE domain=:account_domain AND username=:username AND email=:email AND password=:password_previous AND user=:user',
                {
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
                    account[0]
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

                cursor.execute(
                    'DELETE FROM accounts WHERE domain=:account_domain AND username=:username AND email=:email AND password=:password AND user=:user',
                    {
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
