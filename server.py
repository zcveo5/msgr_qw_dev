import json
import os.path
import socket
import sys
import threading
import time
import traceback

data = json.load(open("./conf.json", 'r'))
host = data['HOST']
port = data['PORT_CHAT']
clients = []
client_addresses = {}
client_addresses_username = {}
client_addresses_username_alt = {}
send_queue = {}

#with open('./server_log.log', 'w'):
#    pass
#sys.stdout = open('./server_log.log', 'a')

if host == '' or port == 0:
    print('Incorrect IP_CONFIGURATION')
    while True:
        time.sleep(1)


def handle_client(client_socket):
    addr = client_addresses[client_socket]
    data_raw = json.load(open('data.json', 'r'))
    data_user = data_raw['users']
    while True:
        try:
            try:
                message = eval(client_socket.recv(1024).decode('utf-8'))
            except SyntaxError:
                return
            if not message:
                break
            if message != {'action_for_chat_server': 'OnlineList'}:
                print(f"Received: {message}")
            if 'text' in message or 'action_for_chat_server' in message:
                name = f'{addr[0]}:{addr[1]}'
                if 'action_for_chat_server' not in message:
                    if message['_show_ip'] == 'False':
                        name = message['name']
                    print(name)
                    if message['to'] == 'public':
                        broadcast(f"{name}: {message['text']}", client_socket)
                    elif message['to'] == 'private':
                        print(client_addresses_username)
                        print(message['to_cl'].split(':'))
                        try:
                            key = client_addresses_username[message['to_cl']]
                            list(client_addresses.keys())[list(client_addresses.values()).index(key)].send(
                                str(f'PRIVATE: {list(client_addresses_username.keys())[list(client_addresses_username.values()).index(client_addresses[client_socket])]}: ' + str(
                                    message['text'])).encode('utf-8'))

                        except KeyError:
                            print('adding to q')
                            if message['to_cl'] not in send_queue:
                                send_queue.update({message['to_cl']: [f'PRIVATE: {list(client_addresses_username.keys())[list(client_addresses_username.values()).index(client_addresses[client_socket])]}: {message["text"]}']})
                            else:
                                send_queue[message['to_cl']].append(f'PRIVATE: {list(client_addresses_username.keys())[list(client_addresses_username.values()).index(client_addresses[client_socket])]}: {message["text"]}')
                            print(send_queue[message['to_cl']])
                            print(send_queue)
                else:
                    if message['action_for_chat_server'] == 'MyUSER':
                        client_addresses_username.update({message['username']: client_addresses[client_socket]})
                    elif message['action_for_chat_server'] == 'ReadyToQ':
                        if message['username'] in send_queue:
                            for msg in send_queue[message['username']]:
                                client_socket.send(msg.encode('utf-8'))
                            send_queue.pop(message['username'])
                    elif message['action_for_chat_server'] == 'OnlineList':
                        client_socket.send(str({'type': 'online_list', 'answer': ['Online:'] + list(client_addresses_username.keys())}).encode('utf-8'))
            else:
                print('this is auth')
                data_recv = message
                ans = {}
                if 'username' in data_recv:
                    if data_recv['username'] not in data_user:
                        data_user.update(
                            {data_recv['username']: {'password': data_recv['password'], 'global_block': 'False'}})
                        ans = {'status': 'ok', 'answer': data_user[data_recv['username']]}
                        print(f"new user {data_recv['username']}")
                    else:
                        if data_user[data_recv['username']]['global_block'] == 'True':
                            ans = {'status': 'ok', 'answer': 'blocked'}
                if 'action' in data_recv:
                    if data_recv['action'].split(':')[0] == 'update_data':
                        if data_recv['action'].split(':')[1] not in data_user[data_recv['username']]:
                            if data_recv['action'].split(':')[1] != 'global_block':
                                print('adding')
                                data_user[data_recv['username']].update(
                                    {data_recv['action'].split(':')[1]: data_recv['action'].split(':')[2]})
                        else:
                            if data_recv['action'].split(':')[1] != 'global_block':
                                print('adding')
                                data_user[data_recv['username']][data_recv['action'].split(':')[1]] = \
                                data_recv['action'].split(':')[2]
                    if data_recv['action'].split(':')[0] == '_in_db':
                        ans = {'status': 'ok', 'answer': data_recv['username'] in data_user}
                    if data_recv['action'] == 'modlist':
                        ans = {'status': 'ok', 'answer': f'{list(data_raw["modlist"].keys())}'}
                    if data_recv['action'].split(':')[0] == 'get_mod':
                        ans = {'status': 'ok', 'answer': f'{data_raw["modlist"][data_recv['action'].split(':')[1]]}'}
                    if data_recv['action'] == 'upload_mod':
                        data_raw["modlist"].update({data_recv['MOD_NAME']: data_recv['PLUG_CODE']})
                        ans = {'status': 'ok', 'answer': 'uploaded'}
                    if data_recv['action'] == 'update':
                        ans = {'status': 'ok', 'answer': f"{open('./msgr.py', 'r').read()}"}
                    if data_recv['action'] == 'my_ip':
                        ans = {'status': 'ok', 'answer': client_addresses[client_socket]}
                if ans == {}:
                    ans = {'status': 'ok', 'answer': data_user[data_recv['username']]}
                if 'username' in message:
                    if message['username'] in client_addresses_username_alt and client_addresses_username_alt[message['username']] != addr:
                        print(f'blocking access for {addr} {message["username"]}, logined as {client_addresses_username_alt[message['username']]}')
                        ans = {'status': 'error', 'answer': f'User {message["username"]} is already login on another client'}
                client_socket.send(f'{ans}'.encode('utf-8'))
                json.dump(data_raw, open('data.json', 'w'))
        except ConnectionError:
            print(f'{addr} disconnected hard')
            try:
                client_addresses_username_alt.pop(list(client_addresses_username_alt.keys())[list(client_addresses_username_alt.values()).index(addr)])
                client_addresses_username.pop(list(client_addresses_username.keys())[list(client_addresses_username.values()).index(addr)])
            except ValueError:
                print(f'Connecdtion close error: {traceback.format_exc()}')
            break
        except Exception as _ex:
            print(type(_ex))
            print(traceback.format_exc())
            try:
                client_socket.send(f'error {traceback.format_exc()}'.encode('utf-8'))
            except ConnectionAbortedError:
                break

def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

def start_server():
    global port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    _port = port
    while True:
        try:
            server.bind((host, port))
            break
        except OSError:
            port += 1
            if (port - _port) > 10:
                tb = traceback.format_exc()
                if '10049' in tb:
                    print('Invalid host ip')
                else:
                    print(f'Failed:\n{tb}')
                return
    #    print(f'Address already in use. kill all python instances\nrun in terminal on Linux: "sudo killall {os.path.basename(sys.executable)}"\non Windows: taskkill /f /im {os.path.basename(sys.executable)}')
    server.listen(5)
    print(f"Server started on: {host}:{port}")
    if port != _port:
        print(f'[ ! WARNING ! ] Server Port is not equal conf[port] : {port} != {_port}')

    while True:
        client_socket, addr = server.accept()
        print(f"chat Connected with {addr}")
        clients.append(client_socket)
        client_addresses.update({client_socket: addr})

        threading.Thread(target=handle_client, args=(client_socket,)).start()


start_server()