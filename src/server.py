# Server SQL Database ile haberlesip istenilen parcaya ve robota gore konum bilgilerini isteyecek
# Server Kullanicinin kaydetmek istedigi parcanin konum bilgilerini SQL Database yeni bir tablo olusturup kaydetecek

import mysql.connector
import socket
import threading

HEADER = 8
HOST = "0.0.0.0"
PORT = 12345
FORMAT = "iso8859_9"
ADDR = (HOST, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen(10)
print("[Listening] Server is listening...")

clients = []
threads = []


def handle(client: socket):
    while (True):
        header_msg = client.recv(HEADER).decode(FORMAT)
        print(header_msg)
        if header_msg:
            msg_len = int(header_msg)
            msg = client.recv(msg_len)
            print(msg)
            msg = msg.decode(FORMAT)
            if msg[:4] == "user":
                user_name = msg[5:]
                client.send("done".encode(FORMAT))
                password_len_str = client.recv(HEADER).decode(FORMAT)
                if password_len_str:
                    password_len = int(password_len_str)
                    msg = client.recv(password_len).decode(FORMAT)
                    password = msg
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
            elif msg[:6] == "create":
                part_name = msg[7:]
                if qualified:
                    # part_name = "eray"
                    sql_str = "create table %s (id int not null auto_increment, robot int not null, position int not null, x_axis double not null, y_axis double not null, z_axis double not null, a_axis double, b_axis double, c_axis double, p_axis double, q_axis double, unique (id), primary key (id));"
                    try:
                        cur.execute(sql_str %
                                    (msg[7:], ))

                        print("Parca olusturuldu.")
                    except:
                        print("error oldu yine")
                    client.send("qualified".encode(FORMAT))
                else:
                    client.send('not qualified'.encode(FORMAT))
            elif msg[:4] == "edit":  # ????????????????????????????????????
                part_name = msg[5:]
                position_len = client.recv(HEADER).decode(FORMAT)
                if position_len:
                    position = client.recv(
                        int(position_len)).decode(FORMAT)
                    cur.execute(f'insert into {part_name} values({position})')
            elif msg[:6] == "select":
                part_name = msg[7:]
                try:
                    cur.execute(f'select max(robot) from {part_name}')
                    max_robot = cur.fetchone()[0]
                    for i in range(1, max_robot+1):
                        cur.execute(
                            f'select * from {part_name} where robot={i}')
                        robot_positions = cur.fetchall()
                        cur.execute(
                            f'select max(position) from {part_name} where robot={i}')
                        max_postion = cur.fetchone()[0]
                        client.recv(4)
                        client.send(f'{i}'.encode(FORMAT))
                        for j in range(1, max_postion+1):
                            row = ','.join(str(k)
                                           for k in robot_positions[j-1])
                            client.recv(4)
                            client.send(f'{j}'.encode(FORMAT))
                            client.recv(4)
                            client.send(f'{len(row)}'.encode(FORMAT))
                            client.recv(4)
                            client.send(f'{row}'.encode(FORMAT))
                            print(i, j)
                        client.recv(4)
                        client.send("endp".encode(FORMAT))
                    client.recv(4)
                    client.send("endr".encode(FORMAT))
                except:
                    client.send("err".encode(FORMAT))
            elif msg[:6] == "delete":
                if qualified:
                    part_name = msg[7:]
                    print(part_name.encode())
                    client.send("qualified".encode(FORMAT))
                    cur.execute(f'drop table {part_name}')
                else:
                    client.send('not qualified'.encode(FORMAT))
            elif msg == "part_names":
                try:
                    cur.execute('show tables;')
                    parts = cur.fetchall()
                    parts_list = [part[0] for part in parts]
                    parts_str = ','.join(str(i) for i in parts_list)
                    client.send(f'{len(parts_str)}'.encode(FORMAT))
                    if client.recv(4).decode(FORMAT) == "done":
                        client.send(f'{parts_str}'.encode(FORMAT))
                except:
                    client.send('err'.encode(FORMAT))
                    print("sunucuya baglanamadi!")
            elif msg == DISCONNECT_MESSAGE:
                print("Client disconnected!")
                break
            else:
                client.send("err".encode(FORMAT))
                break
            msg = ''
        header_msg = ''


while True:
    client, address = server.accept()
    print(f'Connected with {str(address)}')
    clients.append(client)
    thread = threading.Thread(target=handle, args=(client,))
    print("Aktif Baglanti sayisi: ", threading.active_count())
    threads.append(thread)
    thread.start()
