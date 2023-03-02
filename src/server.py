# Server SQL Database ile haberlesip istenilen parcaya ve robota gore konum bilgilerini isteyecek
# Server Kullanicinin kaydetmek istedigi parcanin konum bilgilerini SQL Database yeni bir tablo olusturup kaydetecek

import mysql.connector
import socket
import threading

HEADER = 8
HOST = "0.0.0.0"
PORT = 12345
FORMAT = "utf-8"
ADDR = (HOST, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

connected = False
qualified = False

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
                user_len_str = client.recv(HEADER).decode(FORMAT)
                if user_len_str:
                    user_len = int(user_len_str)
                    msg = client.recv(user_len).decode(FORMAT)
                    password = msg[9:]
                try:
                    con = mysql.connector.connect(host='192.168.0.250', port=3306,
                                                  user=f'{user_name}', password=f'{password}', database='presstransfer')
                    cur = con.cursor()
                    connected = True
                    if connected and user_name == "root":
                        qualified = True
                    else:
                        qualified = False
                    client.send("connected".encode(FORMAT))
                except:
                    connected = False
                    qualified = False
                    client.send("not connected".encode(FORMAT))
            elif msg[:6] == "create" and connected:
                if qualified:
                    part_name = msg[7:]
                    client.send("qualified".encode(FORMAT))
                    cur.execute(f'create table {part_name} (id int not null auto_increment, robot int not null, position int not null, x_axis double not null, y_axis double not null, z_axis double not null, a_axis double, b_axis double, c_axis double, p_axis double, q_axis double, unique (id), primary key (id))')
                    client.send("done".encode(FORMAT))
                else:
                    client.send('not qualified'.encode(FORMAT))
            elif msg[:4] == "edit" and connected:  # ????????????????????????????????????
                part_name = msg[5:]
                position_len = client.recv(HEADER).decode(FORMAT)
                if position_len:
                    position = client.recv(
                        int(position_len)).decode(FORMAT)
                    cur.execute(f'insert into {part_name} values({position})')
            elif msg[:6] == "select" and connected:
                part_name = msg[7:]
                try:
                    cur.execute(f'select max(robot) from {part_name}')
                    max_robot = cur.fetchone()[0]
                    client.send("done".encode(FORMAT))
                    for i in range(1, max_robot+1):
                        cur.execute(
                            f'select * from {part_name} where robot={i}')
                        robot_positions = cur.fetchall()
                        cur.execute(
                            f'select max(postion) from {part_name} where robot={i}')
                        max_postion = cur.fetchone()[0]
                        client.send(f'{i}'.encode(FORMAT))
                        for j in range(0, max_postion):
                            row = ','.join(str(k) for k in robot_positions[j])
                            client.send("done".encode(FORMAT))
                            client.send(f'{len(row)}'.encode(FORMAT))
                            client.send(f'{row}'.encode(FORMAT))
                        client.send("endp".encode(FORMAT))
                    client.send("endr".encode(FORMAT))
                except:
                    client.send("err".encode(FORMAT))
            elif msg[:6] == "delete" and connected:
                try:
                    part_name = msg[7:]
                    cur.execute(f'drop table {part_name}')
                    client.send('done'.encode(FORMAT))
                except:
                    client.send('err'.encode(FORMAT))
            elif msg == "part_mames" and connected:
                try:
                    cur.execute('show tables')
                    parts = cur.fetchall()
                    parts_list = [part[0] for part in parts]
                    parts_str = ','.join(str(i) for i in parts_list)
                    client.send(f'{len(parts_str)}'.encode(FORMAT))
                    client.send(f'{parts_str}'.encode(FORMAT))
                except:
                    client.send('err'.encode(FORMAT))
            else:
                client.send("err".encode(FORMAT))


while True:
    client, address = server.accept()
    print(f'Connected with {str(address)}')
    clients.append(client)
    thread = threading.Thread(target=handle, args=(client,))
    thread.start()
