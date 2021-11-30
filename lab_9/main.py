import datetime
import hashlib
import json
import tkinter as tk
import uuid
from tkinter import scrolledtext

from mpi4py import MPI

# mpiexec -np 2 py main.py

BLOCKCHAIN_PATH = 'C:\\Users\\roma\\Documents\\Python\\MPI\\lab_9\\data.json'
PASSWORDS_PATH = 'C:\\Users\\roma\\Documents\\Python\\MPI\\lab_9\\passwords.json'
TAG = 2

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


def print_output(text):
    output_label.delete(1.0, tk.END)
    output_label.insert(tk.INSERT, text)


def get_blockchain_data():
    with open(BLOCKCHAIN_PATH) as file:
        data = json.load(file)

    return data


def get_passwords():
    with open(PASSWORDS_PATH) as file:
        data = json.load(file)

    return data


def rewrite_blockchain_data(data):
    with open(BLOCKCHAIN_PATH, 'w') as file:
        json.dump(obj=data, fp=file, indent=2)


def rewrite_passwords(data):
    with open(PASSWORDS_PATH, 'w') as file:
        json.dump(obj=data, fp=file, indent=2)


def registration():
    login = None
    children = registration_block.grid_slaves()
    for child in children:
        if child.winfo_name() == 'login':
            login = child.get()

    if not login:
        print_output(text='Введите публичный ключ!')
        return

    passwords = get_passwords()

    if login in passwords:
        print_output(text='Введенный публичный ключ уже существует!')
        return

    salt = uuid.uuid4().hex.encode()
    password = hashlib.sha512(login.encode() + salt).hexdigest()[:40]
    passwords[login] = password

    rewrite_passwords(passwords)

    data = get_blockchain_data()

    blockchain = data['blockchain']
    new_block = {
        'address': login,
        'previous': blockchain['last_block'],
        'transactions': [
            {
                'datetime': datetime.datetime.now().isoformat(),
                'operation': 'registration',
                'text': f'Registered by process {rank}',
            },
        ],
    }
    blocks = blockchain['blocks']
    blocks[login] = new_block
    blockchain['last_block'] = login
    rewrite_blockchain_data(data)
    print_output(text=f'Закрытый ключ: {password}')


def auth():
    login = None
    password = None
    children = auth_block.grid_slaves()
    for child in children:
        if child.winfo_name() == 'login':
            login = child.get()

        if child.winfo_name() == 'password':
            password = child.get()

    passwords = get_passwords()

    if password != passwords.get(login):
        print_output(text='Неверный данные для авторизации!')
        return None

    data = get_blockchain_data()

    block = data['blockchain']['blocks'].get(login)
    transactions = block.get('transactions')
    transactions.append(
        {
            'datetime': datetime.datetime.now().isoformat(),
            'operation': 'login',
            'text': f'Login by process {rank}',
        }
    )
    rewrite_blockchain_data(data)

    formatted_block = json.dumps(block, indent=2)
    print_output(text=formatted_block)


window = tk.Tk()

window.title(f'Process {rank}')
window.geometry('504x486')

header_row = tk.Frame(window)
header_row.grid(row=0)

auth_block = tk.Frame(header_row)
auth_block.grid(row=0, column=0)
tk.Label(auth_block, text='Авторизация').grid(row=0)
tk.Label(auth_block, text='Публичный ключ').grid(row=1, column=0)
tk.Label(auth_block, text='Закрытый ключ').grid(row=2, column=0)
tk.Entry(auth_block, name='login').grid(row=1, column=1)
tk.Entry(auth_block, name='password').grid(row=2, column=1)

button = tk.Button(auth_block, text='Войти', command=auth)
button.grid(row=3)

registration_block = tk.Frame(header_row)
registration_block.grid(row=0, column=1)
tk.Label(registration_block, text='Новый пользователь').grid(row=0)
tk.Label(registration_block, text='Публичный ключ').grid(row=1, column=0)
tk.Entry(registration_block, name='login').grid(row=1, column=1)

button = tk.Button(registration_block, text='Создать', command=registration)
button.grid(row=3)

output_label = scrolledtext.ScrolledText(
    window,
    width=60
)
output_label.grid(
    row=1,
)

window.mainloop()
