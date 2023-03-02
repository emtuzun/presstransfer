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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(10)
print("[Listening] Server is listening...")

clients = []


def handle(client: socket.socket):
    while (True):
        header_msg = client.recv(HEADER).decode(FORMAT)
        if header_msg:
            msg_len = int(header_msg)
            msg = client.recv(msg_len).decode(FORMAT)
            if msg[:4] == "user":
                user_name = msg[5:]
                client.send("done".encode(FORMAT))
                msg_len = int(header_msg)
                msg = client.recv(msg_len).decode(FORMAT)
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
                cur.execute(f'select max(robot) from {part_name}')
                max_robot = cur.fetchone()[0]
                for i in range(1, max_robot+1):
                    cur.execute(f'select * from {part_name} where robot={i}')
                    robot_positions = cur.fetchall()
                    cur.execute(
                        f'select max(postion) from {part_name} where robot={i}')
                    client.send(f'{i}'.encode(FORMAT))
                    max_postion = cur.fetchone()[0]
                    for i in range(0, max_postion):
                        row = ','.join(str(j) for j in robot_positions[i])
                        client.send("done".encode(FORMAT))
                        client.send(f'{row}'.encode(FORMAT))
                    client.send("endr".encode(FORMAT))
                client.send("endp".encode(FORMAT))
            else:
                client.send("error")


while True:
    client, address = server.accept()
    print(f'Connected with {str(address)}')
    clients.append(client)
    thread = threading.Thread(target=handle, args=(client,))
    thread.start()
