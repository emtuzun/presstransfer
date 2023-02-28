# Server SQL Database ile haberlesip istenilen parcaya ve robota gore konum bilgilerini isteyecek
# Server Kullanicinin kaydetmek istedigi parcanin konum bilgilerini SQL Database yeni bir tablo olusturup kaydetecek

# komutlar:
# client_request: 'user {user_name}'
# server_respoense: 'done'
# client_request: 'password {password}'
# server_respoense: 'connected' or 'not connected'

# client_request: 'create_part {part_name}'
# if client not qualified then server_response: 'not qualified'
# else:
# server: 'create table {part_name} (id int not null auto_increment, robot int not null, position int not null, x_axis double not null, y_axis double not null, z_axis double not null, a_axis double, b_axis double, c_axis double, p_axis double, q_axis double, unique (id), primary key (id))'
# server_response: 'done'
# client_request: 'robot_num,position_num,x_axis,y_axis,z_axis,a_axis,b_axis,c_axis,p_axis,q_axis'
# server: 'insert into {part_name} values ({robot_num}, {position_num}, {x_axis}, {y_axis}, {z_axis}, {a_axis}, {b_axis}, {c_axis}, {p_axis}, {q_axis})'

# client_request: 'select {part_name}'
# server: 'select * from {part_name} where robot=1'...
# server_response: '{robot_1}'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# ...
# server_response: 'endr'
# server: 'select * from {part_name} where robot=1'...
# server_response: '{robot_2}'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# server_response: 'done'
# server_response: 'position_num, x_axis, y_axis, z_axis, a_axis, b_axis, c_axis, p_axis, q_axis'
# ...
# server_response: 'endr'
# ...
# ...
# server_response: 'endp'

# client

import mysql.connector
import socket
import threading

HEADER = 8
HOST = "0.0.0.0"
PORT = 12345
FORMAT = "utf-8"
ADDR = (HOST, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

qualified = False

con = mysql.connector.connect(host='192.168.0.250', port=3306,
                              user='root', password='123456Tt', database='presstransfer')
cur = con.cursor()

# sonuc = cur.fetchall()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(10)

clients = []


def handle(client: socket.socket):
    header_msg = client.recv(HEADER).decode(FORMAT)
    if header_msg:
        msg_len = int(header_msg)
        msg = client.recv(msg_len)
        if msg[:4] == "user":
            user_name = msg[5:]
            client.send("done".encode(FORMAT))
            msg_len = int(header_msg)
            msg = client.recv(msg_len)
            password = msg[9:]
        elif msg[:11] == "create_part":
            if qualified:
                part_name = msg[12:]
                cur.execute(f'create table {part_name} (id int not null auto_increment, robot int not null, position int not null, x_axis double not null, y_axis double not null, z_axis double not null, a_axis double, b_axis double, c_axis double, p_axis double, q_axis double, unique (id), primary key (id))')
                client.send("done".encode(FORMAT))
            else:
                client.send('not qualified'.encode(FORMAT))
        elif msg[:6] == "select":
            part_name = msg[7:]

        else:
            client.send("error")


while True:
    client, address = server.accept()
    client.recv()
    print(f'Connected with {str(address)}')
    clients.append(client)
    thread = threading.Thread(target=handle, args=(client,))
    thread.start()
