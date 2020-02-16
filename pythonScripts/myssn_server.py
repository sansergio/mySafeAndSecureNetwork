# myssn_server.py
# Based on the server from https://pymotw.com/3/socket/tcp.html
import myssn
import sys

SERVER_ADDRESS = 'localhost'

server = myssn.server_create(SERVER_ADDRESS)

while True:
    conn = myssn.server_accept(server)
    if conn is None:
        print('INFO: No client connected')
    else:
        while True:
            dat = myssn.recv(conn)
            if dat is None:
                print('INFO: Connection closed')
                break
            myssn.send(conn, dat)
    answer = input('INFO: Do you want to try again (y/n)? ')
    if 'n' in answer:
        break
    else:
        continue

print('INFO: Bye!')
